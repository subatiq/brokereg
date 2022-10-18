import json
from time import sleep
import os
from brokereg import registry
from confluent_kafka import Producer, Consumer

from dotenv import load_dotenv
from typing import Any, Callable, Type
from pydantic import BaseModel
from jsonschema import validate

from threading import Thread

from brokereg.event import Event

load_dotenv()

servers = {'bootstrap.servers': os.getenv("KAFKA_SERVER", "localhost:9092")}

PRODUCER_CONF = {**servers}

producer = Producer(PRODUCER_CONF)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))



def publish(event: Event):
    print('Publishing:', event)
    producer.produce(event.domain, key=registry.build_key(event.domain, event.name, event.version), value=event.json(), callback=acked)
    registry.update_event_schema(event)


conf = {**servers,
        'group.id': os.getenv("KAFKA_CONSUMER_GROUP", "default"),
        'auto.offset.reset': 'earliest',
        'allow.auto.create.topics': True
        }


consumer = Consumer(conf)

def _subscribe(topics: list[str], model: Type[BaseModel], callback: Callable, kwargs: dict[str, Any]):
    while True:
        print("Listening to", topics)
        msg = consumer.poll(3.0)

        if msg is None:
            sleep(2)
            continue

        if msg.error():
            print(msg.error())

            continue

        try:
            received = json.loads(msg.value())
        except json.JSONDecodeError:
            raise ValueError(f"Event [{msg.value()}] was not serialized as a propper JSON")

        print('RECEIVED', received)

        schema = registry.read_json_event_schema(received)
        if schema is not None:
            validate(received, schema)
        else:
            raise ValueError(f"No schema registred for event: {received}")
        
        try:
            args = {"event": model.parse_obj(received), **kwargs}
        except:
            raise ValueError(f"Event model is not compatible with an actual event: {received}")

        print(args)
        callback(**args)
        consumer.commit()


def subscribe(topics: list[str], model: Type[BaseModel], callback: Callable, kwargs: dict[str, Any]):
    consumer.subscribe(topics)
    thread = Thread(target=_subscribe, args=[topics, model, callback, kwargs], daemon=True)
    thread.start()


