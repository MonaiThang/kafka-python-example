import json
import math
import uuid
from confluent_kafka import Producer
from time import time
from utils.data import random_n_digits, random_alphanumeric_string
from utils.delivery import delivery_report

# Create a Producer instance
producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

# Generate sample data consists of 3 users where each user has different 3 timestamps and publish into the input topic
print('Generate sample data and publish into input_topic')
for user in range(3):
    userId = 'j' + str(random_n_digits(8))
    for user_event_count in range(3):
        timestamp = math.floor(time()) + random_n_digits(4)
        record = {
            'userId': userId,
            'visitorId': 'jas8v' + str(random_n_digits(5)),
            'type': 'Event',
            'metadata': {
                'messageId': str(uuid.uuid4()),
                'sentAt': timestamp,
                'timestamp': timestamp,
                'receivedAt': 0,
                'apiKey': 'apiKey' + str(random_n_digits(1)),
                'spaceId': 'space' + str(random_n_digits(1)),
                'version': 'v' + str(random_n_digits(1))
            },
            'event': 'Played Movie',
            'eventData': {
                'MovieID': random_alphanumeric_string(length=8, lowercase_only=False)
            }
        }
        print(record)

        # Produce generated data into the input_topic
        # Trigger any available delivery report callbacks from previous produce() calls
        producer.poll(0)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        producer.produce('input_topic', key=record['userId'], value=json.dumps(record),
                         callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
producer.flush()
