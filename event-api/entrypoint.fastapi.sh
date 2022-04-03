#!/bin/sh

if [ "$SETTINGS" = "dev" ]
then
    echo "Waiting for broker Kafka..."
    while ! nc -z $KAFKA_HOST $KAFKA_PORT; do
      sleep 0.1
    done
    echo "Broker KAFKA started"
    echo "Waiting 60 sec before start application..."
    sleep 60
fi

python app/main.py

exec "$@"