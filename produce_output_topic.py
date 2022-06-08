import json
import pprint

from confluent_kafka import Consumer
from confluent_kafka.cimpl import Producer
from utils.delivery import delivery_report

producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

# Create a Consumer instance
# Use 'auto.offset.reset=earliest' to start reading from the beginning of the topic if no committed offsets exist
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'input_consumer',
    'auto.offset.reset': 'earliest',
})

# Subscribe to topic
consumer.subscribe(["input_topic"])

# Process messages
summary = {}
read_count = 0
try:
    while read_count < 9:
        msg = consumer.poll(0)
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to `session.timeout.ms` for the consumer group
            # to re-balance and start consuming
            print("Waiting for message or event/error in poll()")
            continue
        elif msg.error():
            print("Error: {}".format(msg.error()))
        else:
            # Check for Kafka message
            record_key = msg.key()
            record_value = msg.value()
            data = json.loads(record_value)
            userId = data["userId"]
            timestamp = data["metadata"]["timestamp"]
            # Check if the user already exists in the summary dictionary
            # If the user is already exists, update MIN/MAX timestamp value
            # Otherwise, create a new user entry in the dictionary
            if userId in summary.keys():
                summary[userId]["firstSeen"] = min(summary[userId]["firstSeen"], timestamp)
                summary[userId]["lastSeen"] = max(summary[userId]["lastSeen"], timestamp)
            else:
                summary[userId] = {
                    "firstSeen": timestamp,
                    "lastSeen": timestamp
                }
            print("Consumed record with key {} and value:".format(record_key))
            pprint.pprint(record_value)
            print("Updated summary:")
            pprint.pprint(summary)
            read_count += 1
except KeyboardInterrupt:
    pass
finally:
    # Leave group and commit final offsets
    consumer.close()
    # Parse the summary dictionary into desired format before publishing to the output_topic
    for userId in summary.keys():
        data = {
            "userId": userId,
            "firstSeen": summary[userId]["firstSeen"],
            "lastSeen": summary[userId]["lastSeen"]
        }
        # Produce prepared message into the output_topic
        producer.produce("output_topic", key=data["userId"], value=json.dumps(data),
                         callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        producer.flush()
