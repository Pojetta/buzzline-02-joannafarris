# buzzline-02-case

Streaming data is often too big for any one machine. Apache Kafka is a popular streaming platform that uses publish-subscribe patterns:

- **Producers** publish streaming data to topics
- **Consumers** subscribe to topics to process data in real-time

We'll write Python producers and consumers to work with Kafka topics.

Kafka needs space - it's big. 

It also comes from the Linux world. We'll use WSL on Windows machines.

## Copy This Example Project & Rename

1. Copy/fork this project into your GitHub account and create your own version of this project to run and experiment with.
2. Name it `buzzline-02-yourname` where yourname is something unique to you.

## Task 1. Install and Start Kafka (using WSL if Windows)

Before starting, ensure you have completed the setup tasks in <https://github.com/denisecase/buzzline-01-case> first.
Python 3.11 is required.

In this task, we will download, install, configure, and start a local Kafka service.

1. Install Windows Subsystem for Linux (Windows machines only)
2. Install Kafka Streaming Platform
3. Start the Kafka service (outside the project).


Open a terminal, go to ~/kafka, and run:  

```
cd ~/kafka 
bin/kafka-server-start.sh config/kraft/server.properties 
```

Keep this terminal open. This is the Kafka broker running in the background.

For detailed instructions, see:

- [SETUP_KAFKA](SETUP_KAFKA.md)

## Task 2. Manage Local Project Virtual Environment

Open your project in VS Code and use the commands for your operating system to:

1. Create a Python virtual environment
2. Activate the virtual environment
3. Upgrade pip
4. Install from requirements.txt

### Mac / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install --upgrade pip
python3.11 -m pip install --upgrade -r requirements.txt
```

## Task 3. Start a Kafka Producer

Producers generate streaming data for our topics.

In VS Code, open a terminal.
Use the commands below to activate .venv, and start the producer.

Mac/Linux:

```zsh
source .venv/bin/activate
python3.11 -m producers.kafka_producer_case
```

## Task 4. Start a Kafka Consumer

Consumers process data from topics or logs in real time.

In VS Code, open a NEW terminal in your root project folder.
Use the commands below to activate .venv, and start the consumer.

Mac/Linux:

```zsh
source .venv/bin/activate
python3.11 -m consumers.kafka_consumer_case
```

## Later Work Sessions

When resuming work on this project:

1. Open the folder in VS Code.
2. Start the Kafka service (outside the project).
3. Activate your local project virtual environment (.venv).

## Save Space

To save disk space, you can delete the .venv folder when not actively working on this project.
You can always recreate it, activate it, and reinstall the necessary packages later.
Managing Python virtual environments is a valuable skill.

## License

This project is licensed under the MIT License as an example project.
You are encouraged to fork, copy, explore, and modify the code as you like.
See the [LICENSE](LICENSE.txt) file for more.

---

## Custom Producer & Consumer

This project includes my custom Kafka producer and consumer that emit and process simple, real-world-ish log messages (sensor/webserver/db). The consumer also does tiny real-time analytics and raises alerts on specific patterns.

### Environment variables
Create or update your `.env` at the project root:

Topic + pacing 
``` 
KAFKA_TOPIC=buzz_topic
MESSAGE_INTERVAL_SECONDS=1
```

Consumer group (string)
```
KAFKA_CONSUMER_GROUP_ID_JSON=joanna-group
```

### Run producer

terminal 1

```
source .venv/bin/activate  
python3.11 -m producers   
kafka_producer_joannafarris
```

### Run consumer 

terminal 2 (new)
```
source .venv/bin/activate
python3.11 -m consumers.kafka_consumer_joannafarris
```

### What the producer does (custom messages)

- Emits simple log-style strings that look like real-world system events
  - Examples: `sensor_12: temperature reading = 72F`,  
    `webserver_01: GET /api/products 200 OK`,  
    `db_node_3: replication lag = 2s`
- Adds a timestamp and message counter to each event
- Sends messages continuously to the configured Kafka topic

### What the consumer does (real-time analytics)

- Tracks counts by subsystem and category (sensor / webserver / db)
- Prints a short summary every 10 messages
- Alerts on simple patterns in the stream:
  - Sensor high temperature (≥ 75F)
  - Web server HTTP 5xx errors
  - Database replication lag (≥ 3s)
