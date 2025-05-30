from flask import Flask, request
from sender.main import send_message
from publisher.main import publish_message

##### for local testing #####

app = Flask(__name__)

@app.route('/message', methods=['GET'])
def flask_send_message():
    return send_message(request)

@app.route('/publish', methods=['POST'])
def flask_publish_message():
    return publish_message(request)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)