import taskiq_redis
from taskiq import BrokerMessage, AsyncBroker

# TODO localhost to docker container_name
broker = taskiq_redis.ListQueueBroker("redis://localhost:6379")