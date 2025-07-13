import telebot
from telebot import types
import json
import time
import threading
from datetime import datetime, timedelta
import schedule

API_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7797725626
UPI_ID = "7797725626@axl"
CHANNEL_LINKS = [
    ("Telegram", "https://t.me/RDX_REDEEM"),
    ("YouTube", "https://youtube.com/@rdxgamer900"),
    ("WhatsApp", "https://whatsapp.com/channel/0029VbAtCRs6GcGJbYqUvC38")
]

DATA_FILE = 'users.json'

def load_users():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

def is_premium(user_id):
    user = users.get(str(user_id), {})
    exp = user.get("premium_expiry")
    if exp:
        expiry = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
        return expiry > datetime.now()
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"premium_expiry": None}
        save_users(users)

    text = f"""
ðŸ‘‹ Welcome to *RDX Redeem Bot*

ðŸ”¥ Get Free & Premium Redeem Codes daily!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸš¨ *IMPORTANT NOTICE* ðŸš¨  
âš ï¸ This bot works only between:  
ðŸ•˜ *9:00 PM to 9:30 PM* every night  
â›” Outside this time, no redeem codes will be delivered!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸª™ *Premium Plans*:
ðŸ’° â‚¹30 = 7 Days  
ðŸ’° â‚¹70 = 15 Days  
ðŸ’° â‚¹100 = 30 Days  
ðŸŽ 10 Rare Redeem Codes Daily for Premium Users (MP40, Gun Skins, Emotes, Bundles)

ðŸ”“ *Free Users* get:  
ðŸ“¤ 20 Public Redeem Codes every hour

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“¢ *Join Channels to Continue (Free Users Only):*
""" + ''.join([f'ðŸ”— [{name}]({link})\n' for name, link in CHANNEL_LINKS]) + f"""
ðŸ“ž *Support:* 7797725626  
ðŸ’° *UPI:* {UPI_ID}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ Use /plan â€“ View Premium Benefits  
ðŸ’¡ Use /buy â€“ Upgrade Now  
ðŸ’¡ Use /status â€“ Check Validity  
"""

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = str(message.from_user.id)
    if is_premium(user_id):
        expiry = datetime.strptime(users[user_id]["premium_expiry"], "%Y-%m-%d %H:%M:%S")
        remaining = expiry - datetime.now()
        bot.reply_to(message, f"âœ… You are a premium user.\nâ³ Time left: {remaining.days} days {remaining.seconds // 3600} hours")
    else:
        bot.reply_to(message, "âŒ You are not a premium user. Use /buy to upgrade.")

@bot.message_handler(commands=['buy', 'plan'])
def show_plans(message):
    plans = """
ðŸª™ *Premium Plans:*
ðŸ’° â‚¹30 = 7 Days  
ðŸ’° â‚¹70 = 15 Days  
ðŸ’° â‚¹100 = 30 Days  

ðŸŽ 10 Rare Redeem Codes Daily for Premium Users (MP40, Gun Skins, Emotes, Bundles)

To upgrade, pay via UPI:
ðŸ†” *UPI ID:* `7797725626@axl`

Then send payment proof and your Telegram ID to:
ðŸ‘¤ Admin: @RDX_A_D_M_I_N
"""
    bot.reply_to(message, plans, parse_mode="Markdown")

@bot.message_handler(commands=['approve'])
def approve_user(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, uid, days = message.text.split()
        uid = str(uid)
        days = int(days)
        expiry = datetime.now() + timedelta(days=days)
        if uid not in users:
            users[uid] = {}
        users[uid]["premium_expiry"] = expiry.strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        bot.reply_to(message, f"âœ… Approved user {uid} for {days} days.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast", "").strip()
    count = 0
    for uid in users.keys():
        try:
            bot.send_message(uid, f"ðŸ“¢ Broadcast:\n{text}")
            count += 1
        except:
            continue
    bot.reply_to(message, f"ðŸ“¤ Message sent to {count} users.")

def auto_expire_premium():
    changed = False
    for uid in users:
        if is_premium(uid):
            expiry = datetime.strptime(users[uid]["premium_expiry"], "%Y-%m-%d %H:%M:%S")
            if expiry < datetime.now():
                users[uid]["premium_expiry"] = None
                changed = True
    if changed:
        save_users(users)

def schedule_runner():
    schedule.every(10).minutes.do(auto_expire_premium)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=schedule_runner, daemon=True).start()
bot.polling()
