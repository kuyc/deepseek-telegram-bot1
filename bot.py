import os
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MS_API_KEY = os.getenv("MS_API_KEY")

if not BOT_TOKEN or not MS_API_KEY:
    raise RuntimeError("Нет BOT_TOKEN или MS_API_KEY")

# DeepSeek client
client = OpenAI(
    base_url="https://api-inference.modelscope.ai/v1",
    api_key=MS_API_KEY,
)

def ask_deepseek(text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[{"role": "user", "content": text}],
        extra_body={"enable_thinking": False}
    )
    return response.choices[0].message.content.strip()

# ================== ЛИЧКА ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "✅ Бот работает.\n"
            "Можете добавлять меня в канал как администратора."
        )

# ================== КАНАЛ ==================

async def channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post

    # Игнорируем пустые и сервисные
    if not message or not message.text:
        return

    text = message.text.strip()
    if not text:
        return

    try:
        answer = ask_deepseek(text)
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=answer,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=f"Ошибка: {e}"
        )

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start в личке
    app.add_handler(CommandHandler("start", start))

    # сообщения в канале
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_message))

    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
