from flask import Flask, request
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

CLASS_LINKS = {
    "class6": "https://drive.google.com/YOUR_CLASS6_LINK",
    "class7": "https://drive.google.com/YOUR_CLASS7_LINK",
    "class8": "https://drive.google.com/YOUR_CLASS8_LINK",
    "class9": "https://drive.google.com/YOUR_CLASS9_LINK",
    "class10": "https://drive.google.com/YOUR_CLASS10_LINK"
}

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change["value"]

                if "messages" in value:
                    msg = value["messages"][0]
                    sender = msg["from"]

                    if msg.get("button"):
                        class_id = msg["button"]["id"]
                        send_drive_link(sender, class_id)
                    else:
                        send_welcome(sender)

    return "ok", 200

def send_welcome(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Welcome to Ziel Classes! Please choose your child's class:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "class6", "title": "Class 6"}},
                    {"type": "reply", "reply": {"id": "class7", "title": "Class 7"}},
                    {"type": "reply", "reply": {"id": "class8", "title": "Class 8"}},
                    {"type": "reply", "reply": {"id": "class9", "title": "Class 9"}},
                    {"type": "reply", "reply": {"id": "class10", "title": "Class 10"}}
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)

def send_drive_link(to, class_id):
    link = CLASS_LINKS.get(class_id)
    if not link:
        return

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": f"Here are your materials:\n{link}"}
    }

    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)