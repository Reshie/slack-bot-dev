import os
import functions_framework
from slack_sdk import WebClient

@functions_framework.http
def send_message(request):
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