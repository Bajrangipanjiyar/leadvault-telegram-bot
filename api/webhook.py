# -*- coding: utf-8 -*-
"""
LeadVault India - Official Telegram Sales Bot Webhook (Vercel Serverless Edition)
Runs 24/7 on Vercel Serverless. Instant response, zero downtime, zero server rent.
"""

from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import time
import os
import re
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9253627827:AAGeXbfbet677MybEu8UwbETQJNMiN0mT48").strip()
ADMIN_UPI_ID = os.environ.get("ADMIN_UPI_ID", "9365520395@mbk").strip()
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "7854748403"))

# Locate project root directory (one level up from /api/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_FILE = os.path.join(BASE_DIR, "FREE_SAMPLE_20_Leads_Preview.csv")
BUNDLE_ZIP = os.path.join(BASE_DIR, "India_B2B_Leads_2026_Mega_Bundle.zip")
BANNER_IMG = os.path.join(BASE_DIR, "Product_Cover_Banner_1280x720.png")
QR_IMG = os.path.join(BASE_DIR, "Payment_QR_149.png")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def api_call(endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    if data is not None:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[API Error] {endpoint}: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo_by_id(chat_id, photo_id, caption="", reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "photo": photo_id,
        "parse_mode": "HTML"
    }
    if caption:
        payload["caption"] = caption
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def send_file(chat_id, file_path, endpoint="sendDocument", caption=""):
    if not os.path.exists(file_path):
        print(f"[File Missing] {file_path}")
        return None

    boundary = "LeadVaultVercelBoundary7MA4YW"
    filename = os.path.basename(file_path)

    crlf = "\r\n"
    body = bytearray()
    
    # chat_id field
    body.extend(f"--{boundary}{crlf}".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="chat_id"{crlf}{crlf}{chat_id}{crlf}'.encode("utf-8"))
    
    # caption field
    if caption:
        body.extend(f"--{boundary}{crlf}".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="caption"{crlf}{crlf}{caption}{crlf}'.encode("utf-8"))
        body.extend(f"--{boundary}{crlf}".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="parse_mode"{crlf}{crlf}HTML{crlf}'.encode("utf-8"))

    # file field
    field_name = "photo" if endpoint == "sendPhoto" else "document"
    body.extend(f"--{boundary}{crlf}".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"{crlf}'.encode("utf-8"))
    body.extend(f"Content-Type: application/octet-stream{crlf}{crlf}".encode("utf-8"))
    
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"{crlf}--{boundary}--{crlf}".encode("utf-8"))

    req = urllib.request.Request(
        f"{BASE_URL}/{endpoint}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[Upload Error] {endpoint}: {e}")
        return None

def get_welcome_markup():
    return {
        "inline_keyboard": [
            [
                {"text": "🎁 Download 20 Free Sample Leads", "callback_data": "free_sample"}
            ],
            [
                {"text": "⚡ Buy 1,000+ Full Bundle (₹149)", "callback_data": "buy_bundle"}
            ],
            [
                {"text": "📊 Category Breakdown", "callback_data": "breakdown"},
                {"text": "❓ FAQ & Proof", "callback_data": "faq"}
            ]
        ]
    }

def handle_start(chat_id, user_first_name):
    welcome_text = (
        f"👋 <b>Welcome {user_first_name} to LeadVault India!</b>\n\n"
        "🔥 <b>[2026 Edition] 1,037+ India B2B Leads, Ready to Call</b>\n"
        "Mobile & WhatsApp numbers of verified businesses in Delhi NCR, Mumbai, Pune, and Bangalore (Excel/CSV ready).\n\n"
        "<b>📦 What's included in this 4-in-1 Pack:</b>\n"
        "• 🏋️ <b>457 Gyms:</b> Fitness centers with calling numbers\n"
        "• 🦷 <b>299 Dentists:</b> Clinics with 'No Website' tag (prime for web pitching)\n"
        "• 🏢 <b>260 Brokers:</b> Real estate consultants\n"
        "• ☕ <b>Cafes & Restaurants:</b> High-traffic venue bonus list\n"
        "• 📊 <b>Master Combined Excel/CSV + Buyer Guide</b>\n\n"
        "👉 <i>Choose an option below to test the sample or unlock the full pack:</i>"
    )
    if os.path.exists(BANNER_IMG):
        send_file(chat_id, BANNER_IMG, endpoint="sendPhoto", caption=welcome_text)
        send_message(chat_id, "👇 <b>Select an option:</b>", reply_markup=get_welcome_markup())
    else:
        send_message(chat_id, welcome_text, reply_markup=get_welcome_markup())

def handle_buy_bundle(chat_id):
    buy_text = (
        "🔥 <b>GET THE FULL 1,000+ LEADS 4-IN-1 MEGA BUNDLE</b>\n\n"
        "• Regular Price: <s>₹1,499</s>\n"
        "• <b>Launch Offer: ₹149 ONLY (90% OFF)</b>\n\n"
        "💳 <b>HOW TO PAY VIA UPI (GPay / PhonePe / Paytm / BHIM):</b>\n"
        "1. Scan the official ₹149 QR code above\n"
        f"2. Or pay directly to UPI ID: <code>{ADMIN_UPI_ID}</code> <i>(Tap to copy)</i>\n"
        "3. Amount: <b>₹149</b>\n\n"
        "⚡ <b>NEXT STEP (DELIVERY):</b>\n"
        "Payment complete hone ke baad yahi chat me <b>Payment Screenshot</b> ya <b>12-digit UTR Number</b> send karein.\n\n"
        "✅ Verification ke turant baad bot aapko <b>Full 4-in-1 ZIP Bundle download file</b> send kar dega! 🚀"
    )
    if os.path.exists(QR_IMG):
        send_file(chat_id, QR_IMG, endpoint="sendPhoto", caption=buy_text)
    else:
        send_message(chat_id, buy_text)

def handle_payment_submission(customer_chat_id, customer_name, customer_username, photo_id=None, utr=None):
    # 1. Inform Customer
    cust_wait_text = (
        "⏳ <b>Payment Details Received!</b>\n\n"
        "Aapka payment proof submit ho gaya hai. Transaction verify kiya ja raha hai.\n\n"
        "✅ <b>Verification complete hote hi Full 1,037+ Leads ZIP Bundle isi chat me deliver ho jayega!</b> (Usually within 1-2 minutes)."
    )
    send_message(customer_chat_id, cust_wait_text)

    # 2. Alert Admin with 1-Click Approve / Reject Buttons
    admin_caption = (
        "🚨 <b>NEW ₹149 PAYMENT RECEIVED!</b>\n\n"
        f"👤 <b>Customer:</b> {customer_name} (@{customer_username})\n"
        f"🆔 <b>Chat ID:</b> <code>{customer_chat_id}</code>\n"
        f"🧾 <b>UTR Info:</b> <code>{utr if utr else 'In Screenshot'}</code>\n"
        f"⏰ <b>Time:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        "👉 <i>Check your PhonePe / GPay / Bank for ₹149:</i>"
    )
    admin_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve & Send ZIP", "callback_data": f"approve_{customer_chat_id}"},
                {"text": "❌ Reject (Fake)", "callback_data": f"reject_{customer_chat_id}"}
            ]
        ]
    }
    if photo_id:
        send_photo_by_id(ADMIN_CHAT_ID, photo_id, caption=admin_caption, reply_markup=admin_markup)
    else:
        send_message(ADMIN_CHAT_ID, admin_caption, reply_markup=admin_markup)

def handle_callback(chat_id, callback_id, data):
    if callback_id != "direct":
        api_call("answerCallbackQuery", {"callback_query_id": callback_id})

    # Admin 1-Click Verification Handlers
    if data.startswith("approve_"):
        target_customer_id = int(data.split("_")[1])
        thanks_text = (
            "🎉 <b>PAYMENT VERIFIED SUCCESSFULLY!</b>\n\n"
            "✅ Aapka ₹149 payment confirm ho gaya hai.\n\n"
            "📦 <b>Here is your Full 1,037+ All-India B2B Leads Mega Bundle 2026:</b>\n"
            "Extract the ZIP file to access all 4 categorized CSVs + Master Excel file.\n\n"
            "Thank you for choosing LeadVault India! 🚀"
        )
        send_file(target_customer_id, BUNDLE_ZIP, endpoint="sendDocument", caption=thanks_text)
        send_message(ADMIN_CHAT_ID, f"✅ <b>Order Approved!</b> Full ZIP bundle successfully delivered to customer (ID: <code>{target_customer_id}</code>).")

    elif data.startswith("reject_"):
        target_customer_id = int(data.split("_")[1])
        reject_text = (
            "❌ <b>Payment Verification Failed</b>\n\n"
            "Aapka payment verify nahi ho paya.\n\n"
            "👉 Please confirm karein ki payment successful hua hai aur screenshot me <b>UTR / Transaction ID</b> clearly dikh raha hai.\n"
            "Dubara valid screenshot yaha send karein."
        )
        send_message(target_customer_id, reject_text)
        send_message(ADMIN_CHAT_ID, f"❌ <b>Order Rejected.</b> Customer (ID: <code>{target_customer_id}</code>) has been notified.")

    elif data == "free_sample":
        send_message(chat_id, "⏳ <b>Sending your Free 20-Leads Sample preview...</b>")
        caption = (
            "🎁 <b>Here is your Free 20-Leads Preview!</b>\n\n"
            "• Open directly in Excel or Google Sheets.\n"
            "• Includes verified mobile numbers, Google ratings, and address.\n\n"
            "⚡ <b>Want the full 1,037+ verified leads database?</b>\n"
            "Click below to get the 4-in-1 Mega Pack for just <b>₹149</b>!"
        )
        send_file(chat_id, SAMPLE_FILE, endpoint="sendDocument", caption=caption)
        markup = {
            "inline_keyboard": [
                [{"text": "⚡ Buy Full 1,000+ Bundle (₹149)", "callback_data": "buy_bundle"}]
            ]
        }
        send_message(chat_id, "Ready to unlock the full database?", reply_markup=markup)

    elif data == "buy_bundle":
        handle_buy_bundle(chat_id)

    elif data == "breakdown":
        breakdown_text = (
            "📊 <b>DATABASE CATEGORY BREAKDOWN:</b>\n\n"
            "1. <b>Gyms & Fitness Centers:</b> 457 Leads\n"
            "   <i>Verified WhatsApp/Calling numbers, complete micro-addresses.</i>\n\n"
            "2. <b>Dental Clinics & Dentists:</b> 299 Leads\n"
            "   <i>Includes 'No Website' tag — Perfect for pitching ₹5,000-₹10,000 websites!</i>\n\n"
            "3. <b>Real Estate Brokers & Consultancies:</b> 260 Leads\n"
            "   <i>Gurgaon Cyber Hub, Noida Ext, Hinjewadi Pune, Whitefield Bangalore.</i>\n\n"
            "4. <b>Cafes, Bakeries & Eateries:</b> High-traffic venue contacts.\n\n"
            "5. <b>Master Combined CSV + Buyer Guide:</b> Deduplicated & 100% clean.\n\n"
            "⚡ <b>Launch Price: ₹149</b>"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "⚡ Buy Full Bundle (₹149)", "callback_data": "buy_bundle"}],
                [{"text": "🎁 Get Free 20-Leads Sample", "callback_data": "free_sample"}]
            ]
        }
        send_message(chat_id, breakdown_text, reply_markup=markup)

    elif data == "faq":
        faq_text = (
            "❓ <b>FREQUENTLY ASKED QUESTIONS (FAQ):</b>\n\n"
            "<b>Q1: Ye data kitna fresh hai?</b>\n"
            "A: Ye 2026 verified public business listings se extracted aur deduplicated hai. 95%+ active mobile numbers hain.\n\n"
            "<b>Q2: Main ise kaise open karunga?</b>\n"
            "A: Saari files clean CSV format me hain. Ye Microsoft Excel, Google Sheets aur kisi bhi CRM me direct 1-click me open hoti hain.\n\n"
            "<b>Q3: Web Designers ke liye ye faydemand kyun hai?</b>\n"
            "A: Dental aur Gym lists me 'No Website' tag hai. In businesses ko call karke ₹5,000 - ₹10,000 ki website pitch kar sakte ho. 1 client milte hi 50x ROI!\n\n"
            "<b>Q4: Delivery kaise hoti hai?</b>\n"
            "A: ₹149 UPI payment karne ke baad screenshot ya UTR number send karein, verification ke turant baad full ZIP file isi chat me receive ho jati hai!"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "⚡ Buy Full Bundle (₹149)", "callback_data": "buy_bundle"}],
                [{"text": "🎁 Download Free Sample", "callback_data": "free_sample"}]
            ]
        }
        send_message(chat_id, faq_text, reply_markup=markup)

def process_telegram_update(update):
    try:
        # 1. Messages
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            first_name = msg["chat"].get("first_name", "Friend")
            username = msg["chat"].get("username", "No_Username")
            text = msg.get("text", "").strip()

            if "photo" in msg:
                photo_id = msg["photo"][-1]["file_id"]
                handle_payment_submission(chat_id, first_name, username, photo_id=photo_id)
            elif re.search(r"\b\d{12}\b", text):
                utr_num = re.search(r"\b\d{12}\b", text).group(0)
                handle_payment_submission(chat_id, first_name, username, utr=utr_num)
            elif text.startswith("/start"):
                handle_start(chat_id, first_name)
            elif text.startswith("/faq"):
                handle_callback(chat_id, "direct", "faq")
            elif "buy" in text.lower() or "pay" in text.lower() or "price" in text.lower():
                handle_buy_bundle(chat_id)
            elif "sample" in text.lower() or "free" in text.lower():
                handle_callback(chat_id, "direct", "free_sample")
            else:
                send_message(
                    chat_id,
                    f"Hi {first_name}! Tap below to download the Free Sample or purchase the Full 1,000+ Leads Pack:",
                    reply_markup=get_welcome_markup()
                )

        # 2. Inline Callback Queries
        elif "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb["id"]
            chat_id = cb["message"]["chat"]["id"]
            cb_data = cb.get("data", "")
            handle_callback(chat_id, cb_id, cb_data)

    except Exception as e:
        print(f"[Process Error] {e}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            update = json.loads(post_data.decode("utf-8"))
            process_telegram_update(update)
        except Exception as e:
            print(f"[JSON Parse Error] {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>LeadVault Telegram Bot Status</title></head>
        <body style="font-family:sans-serif;background:#0f172a;color:#f8fafc;padding:40px;text-align:center;">
          <h1 style="color:#38bdf8;">⚡ LeadVault India Telegram Bot is LIVE on Vercel!</h1>
          <p>Serverless webhook is active and responding 24/7/365.</p>
          <p><a href="https://t.me/leadvault_leads_bot" style="color:#10b981;font-weight:bold;text-decoration:none;">👉 Open @leadvault_leads_bot on Telegram</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))
