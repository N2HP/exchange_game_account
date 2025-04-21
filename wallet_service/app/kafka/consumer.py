# from confluent_kafka import Consumer, KafkaError
# import logging
# from fastavro import schemaless_reader
# import io

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Consumer configuration
# conf = {
#     'bootstrap.servers': '157.66.218.191:9092',
#     'group.id': 'wallet_consumer_group_test',
#     'auto.offset.reset': 'earliest'
# }


# avro_schema = {
#   "type": "record",
#   "name": "TransactionEvent",
#   "namespace": "TransactionService.Kafka",
#   "fields": [
#     {
#       "name": "TransactionId",
#       "type": "string"
#     },
#     {
#       "name": "Participants",
#       "type": {
#         "type": "array",
#         "items": "string"
#       }
#     }
#   ]
# }

# # Create Consumer instance
# consumer = Consumer(conf)

# # Subscribe to the topic
# consumer.subscribe(['transaction.wallet.hold'])

# # def process_transaction(transaction_data):
# #     """
# #     Process the incoming transaction
# #     """
# #     user_id = transaction_data.get('user_id')
# #     amount = transaction_data.get('amount')
# #     transaction_type = transaction_data.get('type')
    
# #     logger.info(f"Processing transaction: User ID: {user_id}, Amount: {amount}, Type: {transaction_type}")
    
# #     # Add your business logic here
# #     # For example:
# #     # if transaction_type == "deposit":
# #     #     update_user_balance(user_id, amount)
# #     # elif transaction_type == "withdraw":
# #     #     update_user_balance(user_id, -amount)





# def start_consuming():
#     try:
#         while True:
#             msg = consumer.poll(1.0)
#             if msg is None:
#                 continue
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     logger.info(f"Reached end of partition: {msg.topic()} [{msg.partition()}]")
#                 else:
#                     logger.error(f"Error: {msg.error()}")
#             else:
#                 try:
#                     value = msg.value()
#                     if not value:
#                         logger.error("Received empty message value")
#                         continue
#                     # Nếu dùng Confluent Schema Registry, bỏ qua 5 byte đầu
#                     bytes_reader = io.BytesIO(value[5:])
#                     transaction_data = schemaless_reader(bytes_reader, avro_schema)
#                     logger.info(f"Received Avro message: {transaction_data}")
#                 except Exception as e:
#                     logger.error(f"Error processing Avro message: {e}")
#     except KeyboardInterrupt:
#         logger.info("Stopped by user")
#     finally:
#         consumer.close()


# if __name__ == "__main__":
#     logger.info("Starting Kafka consumer for wallet transactions...")
#     start_consuming()



from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
import logging
from fastavro import schemaless_reader
import io
import json
from app.services.transaction_service import escrow_hold_money, release_escrow_to_seller

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Consumer configuration
conf = {
    'bootstrap.servers': '157.66.218.191:9092',
    'group.id': 'wallet_consumer_group_test_1',
    'auto.offset.reset': 'earliest'
}

# Schema Registry config
schema_registry_conf = {'url': 'http://157.66.218.191:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

def get_schema_for_topic(topic):
    subject = f"{topic}-value"
    schema_obj = schema_registry_client.get_latest_version(subject).schema
    return json.loads(schema_obj.schema_str)

# List các topic cần lắng nghe
topics = ['transaction.wallet.hold', 'transaction.wallet.release']

# Create Consumer instance
consumer = Consumer(conf)
consumer.subscribe(topics)

def start_consuming():
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"Reached end of partition: {msg.topic()} [{msg.partition()}]")
                else:
                    logger.error(f"Error: {msg.error()}")
            else:
                try:
                    value = msg.value()
                    if not value:
                        logger.error("Received empty message value")
                        continue
                    avro_schema = get_schema_for_topic(msg.topic())
                    bytes_reader = io.BytesIO(value[5:])
                    transaction_data = schemaless_reader(bytes_reader, avro_schema)
                    logger.info(f"Received Avro message from {msg.topic()}: {transaction_data}")

                    # Gọi hàm xử lý nếu đúng topic
                    if msg.topic() == "transaction.wallet.hold":
                        escrow_hold_money(transaction_data)
                    elif msg.topic() == "transaction.wallet.release":
                        release_escrow_to_seller(transaction_data['TransactionId'])

                except Exception as e:
                    logger.error(f"Error processing Avro message: {e}")
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        consumer.close()

if __name__ == "__main__":
    logger.info("Starting Kafka consumer for wallet transactions...")
    start_consuming()