from brokereg.registry import update_schema

update_schema(domain="tasks", event_name="TaskCreated", version=1, schema='{"task": "Task"}')

