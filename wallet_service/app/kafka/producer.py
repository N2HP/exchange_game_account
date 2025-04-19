from confluent_kafka.avro import AvroProducer
import avro.schema

# ✅ Cấu hình AvroProducer
conf = {
    'bootstrap.servers': '157.66.218.191:9092',
    'schema.registry.url': 'http://157.66.218.191:8081'  # ✅ phải có http://
}

# ✅ Khai báo schema (dùng đúng hàm `parse`)
value_schema_str = """
{
  "namespace": "wallet_v2",
  "type": "record",
  "name": "Transaction",
  "fields": [
    {"name": "user_id", "type": "int"},
    {"name": "amount", "type": "double"},
    {"name": "type", "type": "string"}
  ]
}
"""
value_schema = avro.schema.parse(value_schema_str)

# ✅ Tạo AvroProducer
producer = AvroProducer(
    conf,
    default_value_schema=value_schema
)

# ✅ Callback sau khi gửi thành công hoặc lỗi
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

# ✅ Hàm gửi Avro message
def send_transaction(user_id, amount, type):
    data = {
        "user_id": user_id,
        "amount": amount,
        "type": type
    }

    producer.produce(topic='wallet_transaction', value=data, callback=delivery_report)
    producer.flush()
