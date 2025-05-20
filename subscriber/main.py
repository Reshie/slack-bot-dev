import os
import json
import time
import hmac
import hashlib
from pprint import pprint
import functions_framework
from google.cloud import pubsub_v1
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from cloudevents.http import CloudEvent

project_id = os.environ["PUBSUB_PROJECT_ID"] 
subscription_id = os.environ["PUBSUB_SUBSCRIPTION_ID"]
topic_id = os.environ["PUBSUB_TOPIC_ID"]
signing_secret = os.environ["SLACK_SIGNING_SECRET"]

def is_valid_request(headers, body):
    try:
        timestamp = headers.get("X-Slack-Request-Timestamp")
        slack_signature = headers.get("X-Slack-Signature")

        if not timestamp or not slack_signature:
            print("Missing required headers")
            return False

        # リクエストと現在時刻に5分以上差があれば無効
        if abs(time.time() - int(timestamp)) > 60 * 5:
            print("Request timestamp is too old")
            return False
        
        # 署名が有効かどうかを確認
        signature_verifier = SignatureVerifier(signing_secret)
        if not signature_verifier.is_valid_request(body, headers):
            print("Invalid signature")
            return False

        return True

    except Exception as e:
        print(f"Error validating request: {str(e)}")
        return False

@functions_framework.cloud_event
def handle_pubsub_message(cloud_event: CloudEvent):
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

        # CloudEventからデータを抽出
        data = json.loads(cloud_event.data.decode("utf-8"))
        headers = data["headers"]
        body = data["body"]
        message_data = data["payload"]

        if not is_valid_request(headers, body):
            return {"status": "invalid request"}
        
        # メッセージの更新に必要な情報を取得
        channel_id = message_data["container"]["channel_id"]
        ts = message_data["container"]["message_ts"]
        selected_option = message_data["actions"][0]["value"]

        # 更新するメッセージの内容を構築
        text = f"Button {selected_option} was pressed!"
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": text
                }
            }
        ]

        # Slackのメッセージを更新
        client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=blocks,
            text=f"Button {selected_option} was pressed!"
        )

        print("Message was updated.")
        return {"status": "success"}

    except Exception as e:
        print(f"Error updating message: {e}")
        raise

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
