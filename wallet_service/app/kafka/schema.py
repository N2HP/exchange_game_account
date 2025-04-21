from confluent_kafka.schema_registry import SchemaRegistryClient
import json

schema_registry_conf = {'url': 'http://157.66.218.191:8081'}
client = SchemaRegistryClient(schema_registry_conf)

subject = 'transaction.wallet.hold-value'
schema_obj = client.get_latest_version(subject).schema
avro_schema_str = schema_obj.schema_str
avro_schema_dict = json.loads(avro_schema_str)  # Dùng cho fastavro
print(avro_schema_dict)