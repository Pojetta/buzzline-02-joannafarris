"""
kafka_consumer_joannafarris.py

Consume messages from a Kafka topic and process them.
"""

###################################
# Import Modules
###################################

# Import packages from Python Standard Library
import os
from collections import Counter
import re


# Import external packages
from dotenv import load_dotenv

# Import functions from local modules
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger

###################################
# Load Environment Variables
###################################

load_dotenv()

CATEGORY_COUNTS = Counter()
SUBSYSTEM_COUNTS = Counter()
TOTAL_MESSAGES = 0


#####################################
# Getter Functions for .env Variables
#####################################


def get_kafka_topic() -> str:
    """Fetch Kafka topic from environment or use default."""
    topic = os.getenv("KAFKA_TOPIC", "unknown_topic")
    logger.info(f"Kafka topic: {topic}")
    return topic


def get_kafka_consumer_group_id() -> int:
    """Fetch Kafka consumer group id from environment or use default."""
    group_id: str = os.getenv("KAFKA_CONSUMER_GROUP_ID_JSON", "default_group")
    logger.info(f"Kafka consumer group id: {group_id}")
    return group_id


#####################################
# Define a function to process a single message
# #####################################


def process_message(message: str) -> None:
    """
    Process a single log-style message and raise simple alerts.

    Examples from producer:
      "[2025-09-08T12:34:56] #42 | webserver_01: GET /api/products 200 OK"
      "[2025-09-08T12:34:57] #43 | sensor_12: temperature reading = 73F"
      "[2025-09-08T12:34:58] #44 | db_node_3: replication lag = 2s"
    """
    global TOTAL_MESSAGES, CATEGORY_COUNTS, SUBSYSTEM_COUNTS

    logger.info(f"Processing message: {message}")
    TOTAL_MESSAGES += 1

    # Right side of the pipe: "webserver_01: GET /... 200 OK"
    try:
        right = message.split("|", 1)[1].strip()
    except IndexError:
        right = message

    # Subsystem token before the first colon
    subsystem = right.split(":", 1)[0].strip() if ":" in right else "unknown"
    SUBSYSTEM_COUNTS[subsystem] += 1

    # Category from alphabetic prefix (webserver, sensor, db, etc.)
    m = re.match(r"([a-zA-Z]+)", subsystem)
    category = m.group(1).lower() if m else "other"
    CATEGORY_COUNTS[category] += 1

    # --------- SIMPLE ALERTS (real-world-ish) ----------
    text = right.lower()

    # 1) Sensor temp high (≥ 75F)
    m_temp = re.search(r"temperature reading\s*=\s*(\d+)\s*f", text)
    if m_temp:
        temp_f = int(m_temp.group(1))
        if temp_f >= 75:
            logger.warning(f"ALERT: {subsystem} high temperature = {temp_f}F")

    # 2) Web status errors (HTTP ≥ 500)
    m_status = re.search(r"\s(\d{3})\s", text)  # captures ' 200 ' or ' 500 '
    if "webserver" in category and m_status:
        code = int(m_status.group(1))
        if code >= 500:
            logger.error(f"ALERT: {subsystem} HTTP {code} error observed")

    # 3) DB replication lag too high (≥ 3s)
    m_lag = re.search(r"replication lag\s*=\s*(\d+)\s*s", text)
    if "db" in category and m_lag:
        lag_s = int(m_lag.group(1))
        if lag_s >= 3:
            logger.warning(f"ALERT: {subsystem} replication lag {lag_s}s")

    # Every 10 messages, log a tiny summary
    if TOTAL_MESSAGES % 10 == 0:
        top_subsystems = ", ".join(
            f"{name}:{count}" for name, count in SUBSYSTEM_COUNTS.most_common(3)
        )
        top_categories = ", ".join(
            f"{name}:{count}" for name, count in CATEGORY_COUNTS.most_common()
        )
        logger.info(
            f"🧮 Summary after {TOTAL_MESSAGES} msgs | "
            f"categories => {top_categories} | top subsystems => {top_subsystems}"
        )


#####################################
# Define main function for this module
#####################################


def main() -> None:
    """
    Main entry point for the consumer.

    - Reads the Kafka topic name and consumer group ID from environment variables.
    - Creates a Kafka consumer using the `create_kafka_consumer` utility.
    - Processes messages from the Kafka topic.
    """
    logger.info("START consumer.")

    # fetch .env content
    topic = get_kafka_topic()
    group_id = get_kafka_consumer_group_id()
    logger.info(f"Consumer: Topic '{topic}' and group '{group_id}'...")

    # Create the Kafka consumer using the helpful utility function.
    consumer = create_kafka_consumer(topic, group_id)

     # Poll and process messages
    logger.info(f"Polling messages from topic '{topic}'...")
    try:
        for message in consumer:
            message_str = message.value
            logger.debug(f"Received message at offset {message.offset}: {message_str}")
            process_message(message_str)
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"Kafka consumer for topic '{topic}' closed.")

    logger.info(f"END consumer for topic '{topic}' and group '{group_id}'.")


#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
