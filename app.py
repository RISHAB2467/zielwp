from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# ---------------- ROOT ROUTE ----------------
@app.route("/")
def home():
    return "Bot is running successfully 🚀"

# ---------------- WEBHOOK VERIFY ----------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook Verified ✅")
        return challenge, 200
    else:
        return "Verification failed ❌", 403

# ---------------- WEBHOOK RECEIVE ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming webhook:", json.dumps(data, indent=2))

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages")

                if messages:
                    for message in messages:
                        sender = message.get("from")
                        msg_type = message.get("type")

                        # If user sends text
                        if msg_type == "text":
                            send_button_message(sender)

                        # If user clicks button
                        if msg_type == "interactive":
                            button_reply = message["interactive"]["button_reply"]["id"]
                            handle_button_reply(sender, button_reply)

    return "EVENT_RECEIVED", 200


# ---------------- SEND BUTTON MESSAGE ----------------
def send_button_message(to):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "📚 Welcome to Ziel Coaching!\n\nChoose your class:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "class6",
                            "title": "Class 6"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "class7",
                            "title": "Class 7"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "class8",
                            "title": "Class 8"
                        }
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=data)


# ---------------- HANDLE BUTTON CLICK ----------------
def handle_button_reply(to, button_id):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    links = {
        "class6": "https://drive.google.com/your-class6-link",
        "class7": "https://drive.google.com/your-class7-link",
        "class8": "https://drive.google.com/your-class8-link"
    }

    message_text = links.get(button_id, "Invalid option")

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": f"Here is your link:\n{message_text}"
        }
    }

    requests.post(url, headers=headers, json=data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)