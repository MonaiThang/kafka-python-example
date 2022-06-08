# Kafka Python Example
## Problem Context
This example will:
- Produce message and publish to Kafka topic (input_topic): Has a producer that publishes events (json object) to kafka topic.
- Consume (read) messages from topic (input topic), aggregate the messages by userId and produce a summary item to another kafka topic (output_topic).

The goal is to publish JSON objects as messages to a kafka topic (input_topic) in the following format (sample input):
```json
{  
 "userId":"j11288090", 
 "visitorId":"jas8v98171", 
 "type":"Event", 
 "metadata":{  
 "messageId":"123sfdafas-32487239857dsh98234", 
 "sentAt":1534382478, 
 "timestamp":1534382478, 
 "receivedAt":0, 
 "apiKey":"apikey1", 
 "spaceId":"space1", 
 "version":"v1" 
 }, 
 "event":"Played Movie", 
 "eventData":{  
 "MovieID":"MIM4ddd4" 
 } 
} 
```
The summary item should have following information (sample json) and should publish the json object to kafka topic (output_topic): 
```json
{  
 "userId":"j11288090", 
 "firstSeen":1534382478, 
 "lastSeen":1534386588 
}
```

## Table of Contents
1. [Environment Setup Instructions](#1-environment-setup-instructions)
   1. [Kafka Cluster](#11-kafka-cluster)
   2. [Development Environment](#12-development-environment)
2. [Problem Analysis](#2-problem-analysis)
   1. [Input Assumptions](#21-input-assumptions)
   2. [Output Assumptions](#22-output-assumptions)
3. [Implementation](#3-implementation)
   1. [Folder Structure](#31-folder-structure)
   2. [Producers](#32-producers)
   3. [Consumers](#33-consumers)

## 1. Environment Setup Instructions
The setup instructions are based on these assumptions:
- OS: Mac OS X 10.15.4
- Docker 2.2.0.5 (43684)
- Python 3.8.2

### 1.1 Kafka Cluster
For this task, I used Confluent Kafka Docker image and followed its official quickstart instructions:
https://docs.confluent.io/current/quickstart/ce-docker-quickstart.html

1. Increase Docker memory size to 8GB via Docker settings under the Resources/Advanced section.
2. Clone the Confluent platform repository using 5.5.0-post branch version. Then run `docker-compose` to build the Kafka Docker image at the path `cp-all-in-one/cp-all-in-one`.
    ```bash
    git clone https://github.com/confluentinc/cp-all-in-one
    cd cp-all-in-one
    git checkout 5.5.0-post
    cd cp-all-in-one
    docker-compose up -d --build
    ```

Note: Use `docker-compose ps` to verify the service is up and running. It should look something like this:
```
     Name                    Command                  State                         Ports                   
------------------------------------------------------------------------------------------------------------
broker            /etc/confluent/docker/run        Up             0.0.0.0:9092->9092/tcp                    
connect           /etc/confluent/docker/run        Up             0.0.0.0:8083->8083/tcp, 9092/tcp          
control-center    /etc/confluent/docker/run        Up             0.0.0.0:9021->9021/tcp                    
ksql-datagen      bash -c echo Waiting for K ...   Up                                                       
ksqldb-cli        /bin/sh                          Up                                                       
ksqldb-server     /etc/confluent/docker/run        Up (healthy)   0.0.0.0:8088->8088/tcp                    
rest-proxy        /etc/confluent/docker/run        Up             0.0.0.0:8082->8082/tcp                    
schema-registry   /etc/confluent/docker/run        Up             0.0.0.0:8081->8081/tcp                    
zookeeper         /etc/confluent/docker/run        Up             0.0.0.0:2181->2181/tcp, 2888/tcp, 3888/tcp
```
Make sure you wait until all services are up and running. In my case, it took me a long while to be able to access its control center via http://localhost:9021

### 1.2 Development Environment
1. Clone the source code. Since it is a private repository you have 2 options to clone this repos:
    1. SSH - more secure method but it has more steps to set up as referred to the [GitHub support page](https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account)
        ```bash
        git@github.com:MonaiThang/kafka-python-example.git
        ```
    2. HTTPS - less setup process than SSH, but you have to type your credentials in the command line.
        ```bash
        git clone https://github.com/MonaiThang/kafka-python-example.git
        Cloning into 'kafka-python-example'...
        Username for 'https://github.com': USERNAME
        Password for 'https://USERNAME@github.com': PASSWORD
        ```
2. Install pipenv
    ```bash
    pip install --user pipenv
    ```
3. Browse to the project path and install project dependencies
    ```bash
    cd kafka-python-example
    pipenv install
    ```
4. Activate pipenv virtual environment on your shell:
    ```bash
    pipenv shell
    ```
5. Run the consumer which also produces another message into `output_topic`, leave the consumer running.
    ```bash
    python produce_output_topic.py
    ```
6. Open another terminal, activate pipenv virtual environment and browse to same path that runs the consumer. Run another the producer for `input_topic`.
    ```bash
    pipenv shell
    python produce_input_topic.py
    ```
    Tips: If you prefer a better UI, make sure you open Confluent Control Center (http://localhost:9021) and browse into both topics message tab before running the `produce_input_topic.py` file. In my case, I opened 2 web browser tabs - one for `input_topic` message and another one for `output_topic` message.

Note: If you are using Python 3.8, you will get a warning message like this:
```
DeprecationWarning: PY_SSIZE_T_CLEAN will be required for '#' formats
  producer.produce("input_topic", key=data["metadata"]["messageId"], value=json.dumps(data),
```
This is a known issue of the library as discussed in this GitHub issue:
https://github.com/confluentinc/confluent-kafka-python/issues/763

## 2. Problem Analysis
The test consists of 2 task:
1. Produce message event in JSON format and publish them to a Kafka topic called `input_topic`
2. Produce another Kafka topic called `output_topic` which is a summary item of `input_topic` derived by aggregating the messages by userId

Expected sample data from `input_topic`
```json
{
  "userId":"j11288090",
  "visitorId":"jas8v98171",
  "type":"Event",
  "metadata":{
    "messageId":"123sfdafas-32487239857dsh98234",
    "sentAt":1534382478,
    "timestamp":1534382478,
    "receivedAt":0,
    "apiKey":"apikey1",
    "spaceId":"space1",
    "version":"v1"
  },
  "event":"Played Movie",
  "eventData":{
    "MovieID":"MIM4ddd4"
  }
}
```

Expected sample data from `output_topic`
```json
{
  "userId":"j11288090",
  "firstSeen":1534382478,
  "lastSeen":1534386588
}
```

As I'm completely new to Apache Kafka, I used Confluent Control Center to help me understand how Kafka works and its specific terms first before starting writing a code for the implementation.

### 2.1 Input Assumptions
- Sample input assumptions
    - No specific data structures in JSON schema format because I only see one sample record without schema information - I will produce a sample data in Python dictionary using my assumed patterns then parse into JSON before publish into Kafka.
    - To make it easy to check, I assumed that there will be 9 messages in total - these 9 messages will cover 3 users, where each user has 3 messages occurred on different timestamps.
    - userId consists of letter prefix "j" with 8 random digits
    - visitorId consists of letter prefix "jas8v" with 5 random digits
    - type is always "Event"
    - messageId is UUID format, which I used UUID4 to increase its randomness
    - sentAt and timestamp are the same number which generates from the closest integer of the current unix timestamp + random 4 digits
    - receivedAt is always 0
    - apiKey consists of letter prefix "apiKey" with 1 random digit
    - spaceId consists of letter prefix "space" with 1 random digit
    - version consists of letter prefix "v" with 1 random digit
    - event is always "Played Movie"
    - MovieID consists of 8 random alphanumeric characters

### 2.2 Output Assumptions
#### Aggregation
I chose timestamp as the event time data to aggregate as it is the best candidate to get the actual time since sinceAt and receiveAt are more relying on the network situation - these two keys can be null if the message is lost or having issue when sending out, but timestamp stays most of the time.

Since all the time data are represented in Unix epoch time which a BIGINT datatype, I can easily use MIN and MAX to find the firstSeen and lastSeen time.

From the given format above, I can produce a KSQL statement for the `output_topic` like this:
```sql
CREATE TABLE output_topic AS
SELECT userId
    , MIN(timestamp) AS firstSeen
    , MAX(timestamp) AS lastSeen
FROM input_topic
GROUP BY userId;
```

As I followed the instructions from the Confluent Docker Image quickstart instruction, the next question is "What format should I store for those topics?".

So I did a further research and found a blog post from Confluent that explains the definitions if streams and tables in Kafka context:
https://www.confluent.io/blog/kafka-streams-tables-part-1-event-streaming/

In this case, `input_topic` should be stream because it defines user action history whereas `output_topic` will be table because it summarises the information from `input_topic`.

#### Aggregate Time Window
The next question is "When/How often should I publish aggregated messages into the output topic?".
In the real world example, this depends on analytics requirements in details such as how often we refresh this state, etc.

Since the objective of the task is to see the ability to aggregate messages in memory over the lifetime of the application and publish the result to a different topic, so I simplified the requirements by assuming that the messages from the `input_topic` is in limited numbers (9 messages as I mentioned in the input assumption section), I will publish the aggregated results into the `output_topic` after consuming all 9 messages.

## 3. Implementation
I chose to implement in Python because it is my most proficient programming language which should take less time to implement given that I have limited amount of time.

Then I followed the examples from the Confluent Python client examples repository and Confluent Kafka Python client readme to learn how to use Confluent Python Client for Apache Kafka.
- https://github.com/confluentinc/examples/tree/5.5.0-post/clients/cloud/python
- https://github.com/confluentinc/confluent-kafka-python/blob/master/examples

### 3.1 Folder structure
- `utils`: Stores helper functions that are used often in the main files
    - `data.py`: Stores helper functions related to sample data generation
    - `delivery.py`: Stores `delivery_report` function which I reuse from the [Confluent Kafka Python client example](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/json_producer.py)
- `produce_input_topic.py`: Generates sample data of 9 messages that cover 3 users, each user has 3 messages on different timestamps. The publish this message into the `input_topic`.
- `produce_output_topic.py`: Consumes all 9 messages from the `input_topic`, aggregates data by userId and then publish the aggregated results into the `output_topic`.

### 3.2 Producers
There are 2 producers in this implementation:
1. The first producer is in the file `produce_input_topic.py`. It publishes the generated sample data messages into the `input_topic`.
2. The second producer is in the file `produce_output_topic.py`. It publishes the aggregated messages from the consumer that subscribes `input_topic` into the `output_topic`. This producer will only publish when the consumer has consumed all 9 messages in the `input_topic`.

### 3.3 Consumers
There is only 1 consumer in this implementation which is in the file `produce_output_topic.py` which subscribes messages from the `input_topic`.

As the consumer streams the incoming messages from `input_topic`, it calculates the earliest and latest timestamp grouped by userId and stores as firstSeen and lastSeen respectively.

Since we already have assumptions that there will be only 9 messages from the sample data, I make the consumer stops the process after it reads all 9 messages.