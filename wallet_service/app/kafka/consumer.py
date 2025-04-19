from confluent_kafka import Consumer, KafkaError
import json
import logging
from fastavro import schemaless_reader
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Consumer configuration
conf = {
    'bootstrap.servers': '157.66.218.191:9092',
    'group.id': 'wallet_consumer_group_v1',
    'auto.offset.reset': 'earliest'
}

# avro_schema = {
#     "type": "record",
#     "name": "Transaction",
#     "fields": [
#         {"name": "user_id", "type": "string"},
#         {"name": "amount", "type": "double"},
#         {"name": "type", "type": "string"}
#     ]
# }


avro_schema = {
  "type": "record",
  "name": "OtpEvModel",
  "namespace": "com.gin.wegd.common.events",
  "fields": [
    {"name": "email", "type": "string"},
    {"name": "userName", "type": "string"},
    {"name": "otp", "type": "string"}
  ]
}

# Create Consumer instance
consumer = Consumer(conf)

# Subscribe to the topic
consumer.subscribe(['auth.ev.otp'])

# def process_transaction(transaction_data):
#     """
#     Process the incoming transaction
#     """
#     user_id = transaction_data.get('user_id')
#     amount = transaction_data.get('amount')
#     transaction_type = transaction_data.get('type')
    
#     logger.info(f"Processing transaction: User ID: {user_id}, Amount: {amount}, Type: {transaction_type}")
    
#     # Add your business logic here
#     # For example:
#     # if transaction_type == "deposit":
#     #     update_user_balance(user_id, amount)
#     # elif transaction_type == "withdraw":
#     #     update_user_balance(user_id, -amount)





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
                    # Nếu dùng Confluent Schema Registry, bỏ qua 5 byte đầu
                    bytes_reader = io.BytesIO(value[5:])
                    transaction_data = schemaless_reader(bytes_reader, avro_schema)
                    logger.info(f"Received Avro message: {transaction_data}")
                except Exception as e:
                    logger.error(f"Error processing Avro message: {e}")
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        consumer.close()


# def start_consuming():
#     """
#     Start consuming messages from Kafka
#     """
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
#                     # Giải mã Avro
#                     bytes_reader = io.BytesIO(value[5:])
#                     transaction_data = schemaless_reader(bytes_reader, avro_schema)
#                     logger.info(f"Received Avro message: {transaction_data}")
#                     # process_transaction(transaction_data)
#                 except Exception as e:
#                     logger.error(f"Error processing Avro message: {e}")
#     except KeyboardInterrupt:
#         logger.info("Stopped by user")
#     finally:
#         consumer.close()












# def start_consuming():
#     """
#     Start consuming messages from Kafka
#     """
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
#                     # Parse the message value
#                     # transaction_data = json.loads(msg.value().decode('utf-8'))
#                     # logger.info(f"Received message: {transaction_data}")
                    
#                     # Process the transaction
#                     # process_transaction(transaction_data)
#                     print(f"Processing transaction: {msg.value().decode('utf-8')}")                    
#                 except Exception as e:
#                     logger.error(f"Error processing message: {e}")
    
#     except KeyboardInterrupt:
#         logger.info("Stopped by user")
#     finally:
#         # Close down consumer to commit final offsets
#         consumer.close()

if __name__ == "__main__":
    logger.info("Starting Kafka consumer for wallet transactions...")
    start_consuming()