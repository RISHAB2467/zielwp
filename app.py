from flask import Flask, request, jsonify
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming webhook:", data)

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages")

                if messages:
                    for message in messages:
                        sender = message.get("from")
                        text = message.get("text", {}).get("body")

                        print("Sender:", sender)
                        print("Message:", text)

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)