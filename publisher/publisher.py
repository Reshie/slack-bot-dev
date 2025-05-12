import os
from google.cloud import pubsub_v1
from flask import Flask, request

app = Flask(__name__)

project_id = os.environ["PUBSUB_PROJECT_ID"]
topic_id = os.environ["PUBSUB_TOPIC_ID"]

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

@app.route('/publish', methods=['POST'])
def publish_message():
    future = publisher.publish(topic_path, request.data)
    future.result()
    return 'Message published.'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)