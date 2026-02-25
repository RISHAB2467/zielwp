from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Environment variables (set in Railway)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# Drive links for each class
CLASS_LINKS = {
    "class6": "https://drive.google.com/YOUR_CLASS6_LINK",
    "class7": "https://drive.google.com/YOUR_CLASS7_LINK",
    "class8": "https://drive.google.com/YOUR_CLASS8_LINK",
    "class9": "https://drive.google.com/YOUR_CLASS9_LINK",
    "class10": "https://drive.google.com/YOUR_CLASS10_LINK"
}

# ==============================
# 🔹 Webhook Verification (GET)
# ==============================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Webhook is live", 200


# ==============================
# 🔹 Webhook Listener (POST)
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change["value"]

                if "messages" in value:
                    msg = value["messages"][0]
                    sender = msg["from"]

                    # If user clicked a button
                    if msg.get("interactive"):
                        interactive = msg["interactive"]

                        if interactive.get("type") == "button_reply":
                            class_id = interactive["button_reply"]["id"]
                            send_drive_link(sender, class_id)
                    else:
                        # First message → send welcome buttons
                        send_welcome(sender)

    return "ok", 200


# ==============================
# 🔹 Send Welcome Buttons
# ==============================
def send_welcome(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Welcome to Ziel Classes!\n\nPlease choose your child's class:"
            },
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


# ==============================
# 🔹 Send Drive Link
# ==============================
def send_drive_link(to, class_id):
    link = CLASS_LINKS.get(class_id)

    if not link:
        return

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": f"Here are your materials:\n{link}"
        }
    }

    requests.post(url, headers=headers, json=payload)


# ==============================
# 🔹 Run App (Railway Compatible)
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)