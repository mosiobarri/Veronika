import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم توکن‌های API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# تنظیم کلاینت OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من بات شما هستم که با OpenAI Assistant کار می‌کنم. یه پیام بفرست تا بتونم باهات گپ بزنم!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # ارسال پیام به OpenAI Assistant
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # مدل Assistant (مثل gpt-4o یا gpt-3.5-turbo)
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        assistant_reply = response.choices[0].message.content
    except Exception as e:
        assistant_reply = f"خطا در ارتباط با OpenAI: {str(e)}"

    # ارسال پاسخ به کاربر در تلگرام
    await update.message.reply_text(assistant_reply)

def main():
    # تنظیم بات تلگرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # افزودن دستورات و هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع بات با Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://veronika.onrender.com/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
