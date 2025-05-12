import os
from google.cloud import pubsub_v1

project_id = os.environ["PUBSUB_PROJECT_ID"] 
subscription_id = os.environ["PUBSUB_SUBSCRIPTION_ID"]

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print(f"Received {message.data.decode('utf-8')}.")
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
    except Exception as e:
        print(e)
