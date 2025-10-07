#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram File Downloader Bot
نویسنده: شما ❤️
عملکرد:
- دریافت لینک از کاربر
- دانلود فایل
- جایگزینی "-" با "_" در نام فایل
- ارسال فایل به کاربر
"""

import os
import re
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# تنظیم لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "کافیه لینک فایل رو بفرستی تا دانلود و با نام درست برات ارسال کنم.\n\n"
        "مثال:\nhttps://example.com/files/my-file-01.pdf"
    )

# تابع اصلاح نام فایل
def sanitize_filename(url: str) -> str:
    filename = url.split("/")[-1] or "file"
    filename = re.sub(r"-", "_", filename)
    filename = re.sub(r"[^A-Za-z0-9_.]", "", filename)
    return filename

# هندلر لینک‌ها
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not re.match(r"^https?://", url):
        await update.message.reply_text("❌ لطفاً لینک معتبر (http یا https) ارسال کن.")
        return

    await update.message.reply_text("🔄 در حال دانلود فایل، لطفاً چند لحظه صبر کن...")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دانلود فایل:\n{e}")
        return

    filename = sanitize_filename(url)
    try:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        await update.message.reply_document(
            document=open(filename, "rb"),
            filename=filename,
            caption=f"✅ فایل با نام جدید ارسال شد:\n{filename}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال فایل:\n{e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

# اجرای اصلی ربات
def main():
    TOKEN = os.getenv("TG_BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("⚠️ متغیر محیطی TG_BOT_TOKEN تنظیم نشده است!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🤖 Bot is running...")
    app.run_polling()

if name == "main":

    main()
