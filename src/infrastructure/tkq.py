import taskiq_redis
# TODO localhost to docker container_name
broker = taskiq_redis.ListQueueBroker("redis://localhost:6379")