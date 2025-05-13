import os
import json
from google.cloud import pubsub_v1
from slack_sdk import WebClient

project_id = os.environ["PUBSUB_PROJECT_ID"] 
subscription_id = os.environ["PUBSUB_SUBSCRIPTION_ID"]

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    data = json.loads(message.data.decode("utf-8"))

    channel_id = data["container"]["channel_id"]
    ts = data["container"]["message_ts"]
    selected_option = data["actions"][0]["value"]
    blocks = [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": f"Button {selected_option} was pressed!"
			}
		}
	]

    try:
        client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=blocks,
            text=f"Button {selected_option} was pressed!"
        )
    except Exception as e:
        print(f"Error updating message: {e}\n")

    print("Message was updated.\n")
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
