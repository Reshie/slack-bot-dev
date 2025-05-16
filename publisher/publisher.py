import os
import json
from pprint import pprint
from google.cloud import pubsub_v1
from flask import Flask, request
from slack_sdk import WebClient

app = Flask(__name__)

@app.route('/message', methods=['GET'])
def send_message():
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Hello! Press any button😎",
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "A",
                    },
                    "value": "A",
                    "action_id": "action_a"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "B",
                    },
                    "value": "B",
                    "action_id": "action_b"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "C",
                    },
                    "value": "C",
                    "action_id": "action_c"
                }
            ]
        }
    ]

    try:
        client.chat_postMessage(
            channel="#general",
            blocks=blocks
        )
    except Exception as e:
        return f'Error sending message: {e}\n', 500
    
    return 'Message has been sent.', 200

@app.route('/publish', methods=['POST'])
def publish_message():
    project_id = os.environ["PUBSUB_PROJECT_ID"]
    topic_id = os.environ["PUBSUB_TOPIC_ID"]

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    try:
        message = {
            "headers": dict(request.headers),
            "body": request.get_data(as_text=True),
            "payload": json.loads(request.form.get('payload', '{}'))
        }
        data = json.dumps(message).encode('utf-8')
        future = publisher.publish(topic_path, data)
        future.result()
    except Exception as e:
        print(f'Error publishing message: {e}\n', flush=True)
        return f'Error publishing message: {e}', 500
    
    return 'Message was published.', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)