#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telegram File Downloader Bot (v20.6 compatible)"""

import os
import re
import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام 👋\nکافیه لینک فایل رو بفرستی تا دانلود و با نام درست برات ارسال کنم.\nمثال:\nhttps://example.com/files/my-file-01.pdf"
    )

def sanitize_filename(url: str) -> str:
    filename = url.split("/")[-1] or "file"
    filename = re.sub(r"-", "_", filename)
    filename = re.sub(r"[^A-Za-z0-9_.]", "", filename)
    return filename

def handle_link(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if not re.match(r"^https?://", url):
        update.message.reply_text("❌ لطفاً لینک معتبر (http یا https) ارسال کن.")
        return

    update.message.reply_text("🔄 در حال دانلود فایل، لطفاً چند لحظه صبر کن...")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except Exception as e:
        update.message.reply_text(f"❌ خطا در دانلود فایل:\n{e}")
        return

    filename = sanitize_filename(url)
    try:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        update.message.reply_document(
            document=open(filename, "rb"),
            filename=filename,
            caption=f"✅ فایل با نام جدید ارسال شد:\n`{filename}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        update.message.reply_text(f"❌ خطا در ارسال فایل:\n{e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def main():
    TOKEN = os.getenv("TG_BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("⚠️ متغیر محیطی TG_BOT_TOKEN تنظیم نشده است!")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
