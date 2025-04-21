# from confluent_kafka.avro import AvroProducer
# import avro.schema

# # ✅ Cấu hình AvroProducer
# conf = {
#     'bootstrap.servers': '157.66.218.191:9092',
#     'schema.registry.url': 'http://157.66.218.191:8081',  # ✅ phải có http://
# }

# # ✅ Khai báo schema (dùng đúng hàm `parse`)
# value_schema_str = """
# {
#   "namespace": "wallet_v3",
#   "type": "record",
#   "name": "Transaction",
#   "fields": [
#     {"name": "user_id", "type": "int"},
#     {"name": "amount", "type": "double"},
#     {"name": "type", "type": "string"}
#   ]
# }
# """
# value_schema = avro.schema.parse(value_schema_str)

# # ✅ Tạo AvroProducer
# producer = AvroProducer(
#     conf,
#     default_value_schema=value_schema
# )

# # ✅ Callback sau khi gửi thành công hoặc lỗi
# def delivery_report(err, msg):
#     if err is not None:
#         print(f"❌ Delivery failed: {err}")
#     else:
#         print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

# # ✅ Hàm gửi Avro message
# def send_notification(user_id, amount, type):
#     data = {
#         "user_id": user_id,
#         "amount": amount,
#         "type": type
#     }

#     producer.produce(topic='wallet.notification.events', value=data, callback=delivery_report)
#     producer.flush()

# def send_hold_notification(transaction_id, participants):
#     data = {
#         "TransactionId": transaction_id,
#         "Participants": participants
#     }

#     producer.produce(topic='transaction.wallet.hold', value=data, callback=delivery_report)
#     producer.flush()

# def send_release_notification(transaction_id, participants):
#     data = {
#         "TransactionId": transaction_id,
#         "Participants": participants
#     }

#     producer.produce(topic='transaction.wallet.release', value=data, callback=delivery_report)
#     producer.flush()



from confluent_kafka.avro import AvroProducer
import avro.schema

conf = {
    'bootstrap.servers': '157.66.218.191:9092',
    'schema.registry.url': 'http://157.66.218.191:8081',
}

# Khai báo các schema
notification_schema_str = """
{
  "namespace": "wallet_v4",
  "type": "record",
  "name": "Transaction",
  "fields": [
    {"name": "user_id", "type": "int"},
    {"name": "amount", "type": "double"},
    {"name": "type", "type": "string"},
    {"name": "condition", "type": ["null", "string"], "default": null}
  ]
}
"""
hold_schema_str = """
{
  "type": "record",
  "name": "TransactionEvent",
  "namespace": "TransactionService.Kafka",
  "fields": [
    {"name": "TransactionId", "type": "string"},
    {"name": "Amount", "type": "double"},
    {"name": "Status", "type": "string"}
  ]
}
"""

hold_schema = avro.schema.parse(hold_schema_str)



notification_schema = avro.schema.parse(notification_schema_str)

producer = AvroProducer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

def send_notification(user_id, amount, type, condition):
    data = {
        "user_id": user_id,
        "amount": amount,
        "type": type,
        "condition": condition  # or some default value
    }
    producer.produce(
        topic='wallet.notification.events',
        value=data,
        value_schema=notification_schema,
        callback=delivery_report
    )
    producer.flush()

def send_hold_notification(transaction_id, amount, status):
    data = {
        "TransactionId": transaction_id,
        "Amount": amount,
        "Status": status
    }
    producer.produce(
        topic='wallet.transaction.hold',
        value=data,
        value_schema=hold_schema,
        callback=delivery_report
    )
    producer.flush()

def send_release_notification(transaction_id, amount, status):
    data = {
        "TransactionId": transaction_id,
        "Amount": amount,
        "Status": status
    }
    producer.produce(
        topic='wallet.transaction.release',
        value=data,
        value_schema=hold_schema,
        callback=delivery_report
    )
    producer.flush()