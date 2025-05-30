import os
from google.cloud import pubsub_v1
from subscriber.subscriber import handle_pubsub_message
from cloudevents.http import CloudEvent

project_id = os.environ["GCLOUD_PROJECT_ID"] 
subscription_id = os.environ["PUBSUB_SUBSCRIPTION_ID"]
topic_id = os.environ["PUBSUB_TOPIC_ID"]

##### for local testing #####

def create_cloud_event(message):
    attributes = {
        "datacontenttype": "application/json; charset=utf-8",
        "id": message.message_id,
        "source": f"//pubsub.googleapis.com/{topic_id}",
        "specversion": "1.0",
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "time": message.publish_time.isoformat(),
    }
    return CloudEvent(attributes, message.data)

def callback(message):
    cloud_event = create_cloud_event(message)
    handle_pubsub_message(cloud_event)
    message.ack()

if __name__ == "__main__":
    # Pub/Subのサブスクライバーを初期化
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # メッセージの受信を開始
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    with subscriber:
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
        except Exception as e:
            print(e)
