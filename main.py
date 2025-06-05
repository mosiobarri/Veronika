import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم توکن‌ها و Assistant ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# تنظیم کلاینت OpenAI با هدر Assistants v2
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من بات شما با Assistant اختصاصی هستم. یه پیام بفرست!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # ایجاد Thread برای مکالمه
        thread = client.beta.threads.create()

        # افزودن پیام کاربر به Thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # اجرای Assistant در Thread
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # انتظار برای تکمیل پاسخ
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # دریافت پاسخ Assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_reply = messages.data[0].content[0].text.value

    except Exception as e:
        assistant_reply = f"خطا در ارتباط با Assistant: {str(e)}"

    # ارسال پاسخ به کاربر
    await update.message.reply_text(assistant_reply)

def main():
    # تنظیم بات تلگرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # افزودن دستورات و هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://veronika.onrender.com/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
