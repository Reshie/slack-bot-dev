import os
import json
import time
import base64
import requests
import functions_framework
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from cloudevents.http import CloudEvent

project_id = os.environ["GCLOUD_PROJECT_ID"] 
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
        data_b64 = cloud_event.data["message"]["data"]
        data = json.loads(base64.b64decode(data_b64).decode("utf-8"))
        headers = data["headers"]
        body = data["body"]
        message_data = data["payload"]

        if not is_valid_request(headers, body):
            return {"status": "invalid request"}
        
        # メッセージの更新に必要な情報を取得
        channel_id = message_data["container"]["channel_id"]
        ts = message_data["container"]["message_ts"]
        action_data = json.loads(message_data["actions"][0]["value"])
        text = action_data["text"]
        url = action_data["url"]

        # 外部URLにリクエストを送信
        response = requests.get(url)

        # 更新するメッセージの内容を構築
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
            text=text
        )

        print("Message was updated.")
        return {"status": "success"}

    except Exception as e:
        print(f"Error updating message: {e}")
        raise