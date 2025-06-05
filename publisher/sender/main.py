import os
import json
import functions_framework
from slack_sdk import WebClient
from jsonschema import validate, ValidationError
from .schemas import request_schema

@functions_framework.http
def send_message(request):
    try:
        data = request.json
        # スキーマ検証
        validate(instance=data, schema=request_schema)
        
        channel = data["channel"]
        text = data["text"]
        mentions = data["mentions"]
        yes_data = data["buttons"]["yes"]
        no_data = data["buttons"]["no"]
        
    except ValidationError as e:
        return f'Schema validation error: {e.message}\n', 400
    except Exception as e:
        return f'Error parsing request: {e}\n', 400

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    blocks = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"{' '.join([f'<@{m}>' for m in mentions])} {text}" if mentions else text
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": f"Yes"
					},
					"style": "primary",
					"value": json.dumps(yes_data),
					"action_id": "action_yes"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": f"No"
					},
					"style": "danger",
					"value": json.dumps(no_data),
					"action_id": "action_no"
				}
			]
		}
	]

    try:
        client.chat_postMessage(
            channel=channel,
            blocks=blocks
        )
    except Exception as e:
        return f'Error sending message: {e}\n', 500
    
    return 'Message has been sent.', 200