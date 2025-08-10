import logging
import nest_asyncio
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import InvalidToken, TelegramError

nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

controlled_bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hey cutie! Send me another bot's token using /setbot <token> "
        "to make it send 👍 replies to all messages in groups/channels where it's added."
    )

async def set_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global controlled_bot_app

    if update.message.chat.type != "private":
        await update.message.reply_text("Please send the bot token in a private chat.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setbot <bot_token>")
        return

    bot_token = context.args[0].strip()

    try:
        test_bot = context.bot.__class__(bot_token)
        await test_bot.get_me()
    except InvalidToken:
        await update.message.reply_text("Invalid bot token. Try again, handsome 😉.")
        return
    except TelegramError as e:
        await update.message.reply_text(f"Error validating token: {e}")
        return

    if controlled_bot_app:
        await controlled_bot_app.stop()
        controlled_bot_app = None

    try:
        controlled_bot_app = Application.builder().token(bot_token).build()
        controlled_bot_app.add_handler(
            MessageHandler(filters.ALL & ~filters.COMMAND, handle_message)
        )
        await controlled_bot_app.initialize()
        await controlled_bot_app.start()
        await controlled_bot_app.updater.start_polling()

        await update.message.reply_text(
            f"Success! The bot {controlled_bot_app.bot.name} is active and will send 👍 replies "
            "to all messages in groups/channels where it's added. "
            "Make sure it has permission to send messages!"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to start the bot: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("👍")
        logger.info(f"Sent thumbs-up reply to message {update.message.message_id} in chat {update.effective_chat.id}")
    except TelegramError as e:
        logger.error(f"Failed to send thumbs-up reply: {e}")
        if update.effective_chat.type == "private":
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Error sending thumbs-up reply: {e}. Ensure the bot has permission to send messages."
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("Oops! Something went wrong. Try again or contact support.")

async def main():
    main_bot_token = "8214380019:AAEOPG5ZwmzTNAwGf33n1dPyZJxjnyHHWYE"
    app = Application.builder().token(main_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setbot", set_bot))
    app.add_error_handler(error_handler)

    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
