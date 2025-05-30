import os
import json
import functions_framework
from google.cloud import pubsub_v1

@functions_framework.http
def publish_message(request):
    project_id = os.environ["GCLOUD_PROJECT_ID"]
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