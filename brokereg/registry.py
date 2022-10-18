import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError
from pydantic import SecretStr
from brokereg.event import Event
from dotenv import load_dotenv

load_dotenv()


REGISTRY_SERVER_URL = os.getenv("PROVIDER_URL", "https://storage.yandexcloud.net")
BUCKET = os.getenv("BUCKET", "schemas")

ACCESS_KEY = os.getenv("ACCESS_TOKEN", "")
SECRET_KEY = SecretStr(os.getenv("SECRET_ACCESS_TOKEN", ""))
REGION_NAME = os.getenv("REGION_NAME", "ru-central1")


s3_client = boto3.client(service_name='s3', region_name=REGION_NAME,
                         endpoint_url=REGISTRY_SERVER_URL,
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY.get_secret_value())


def read(key: str) -> dict[str, Any] | None:
    try:
        result = s3_client.get_object(Bucket=BUCKET, Key=key)
        return json.loads(result['Body'].read().decode())

    except ClientError:
        return


def write_dict(key: str, data: dict[str, Any]):
    write_raw(key, json.dumps(data))


def write_raw(key: str, data: str):
    result = s3_client.put_object(
            Body=data.encode('UTF-8'),
            Bucket=BUCKET,
            Key=key)

    if not result:
        raise RuntimeError("Registry unavailable")


def build_key(domain: str, event_name: str, version: int) -> str:
    return f"{domain}/{event_name}/v{version}.json"


def update_event_schema(event: Event):
    update_schema(event.domain, event.name, event.version, event.schema_json())


def update_schema(domain: str, event_name: str, version: int, schema: str):
    s3_key = build_key(domain, event_name, version)
    existing = read(key=s3_key)

    schema_obj = json.loads(schema)
    print(event_name, 'SCHEMA', schema_obj)

    if existing == schema_obj:
        return

    if existing and existing['version'] == schema_obj['version']:
        raise ValueError(f"Version conflict in schemas for event: {schema_obj['name']}")

    write_raw(s3_key, schema)


def read_schema(domain: str, event_name: str, version: int) -> dict[str, Any] | None:
    s3_key = build_key(domain, event_name, version)
    return read(key=s3_key)


def read_json_event_schema(event: dict[str, Any]) -> dict[str, Any] | None:
    return read_schema(event.get('domain', ''), event.get('name', ''), event.get('version', 0))
