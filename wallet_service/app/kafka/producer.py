# from confluent_kafka import Producer
# import json

# conf = {
#     'bootstrap.servers': 'localhost:9092'
# }

# producer = Producer(conf)

# def delivery_report(err, msg):
#     if err is not None:
#         print(f"❌ Delivery failed: {err}")
#     else:
#         print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

# def send_transaction(user_id, amount, action):
#     data = {
#         "user_id": user_id,
#         "amount": amount,
#         "action": action
#     }

#     json_data = json.dumps(data).encode('utf-8')

#     producer.produce('wallet_transaction', value=json_data, callback=delivery_report)
#     producer.flush()
