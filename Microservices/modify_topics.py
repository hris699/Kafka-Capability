from confluent_kafka.admin import AdminClient, NewPartitions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka AdminClient configuration
conf = {'bootstrap.servers': '18.117.231.177:9092'}
admin_client = AdminClient(conf)

# Define topics and their new partition counts
topics_to_update = [
    {'topic': 'order-events', 'new_partitions': 5},  # High throughput for orders
    {'topic': 'payment-events', 'new_partitions': 3},  # Moderate throughput
    {'topic': 'product-events', 'new_partitions': 3},  # Balanced for inventory
]

# Create NewPartitions objects for each topic
new_partitions_list = [
    NewPartitions(
        topic=topic_config['topic'],
        new_total_count=topic_config['new_partitions']  # Corrected parameter name
    )
    for topic_config in topics_to_update
]

# Update partitions for all topics
try:
    result = admin_client.create_partitions(new_partitions_list)
    for topic, future in result.items():
        try:
            future.result()  # Wait for operation to complete
            logger.info(f"Topic '{topic}' updated to {topics_to_update[[t['topic'] for t in topics_to_update].index(topic)]['new_partitions']} partitions")
        except Exception as e:
            logger.error(f"Failed to update partitions for '{topic}': {e}")
except Exception as e:
    logger.error(f"Error in partition modification: {e}")