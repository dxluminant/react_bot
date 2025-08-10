import logging
from telegram import Update, ReactionTypeEmoji
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from telegram.error import InvalidToken, TelegramError

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variable to store the controlled bot's application
controlled_bot_app = None

# Main bot handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "Hello! I'm @MyAdminBot. Send me another bot's token using /setbot <token> "
        "to give it the power to react to all messages in groups/channels where it's added."
    )

async def set_bot(update: Update, context: CallbackContext) -> None:
    """Handle the /setbot command to receive and validate another bot's token."""
    global controlled_bot_app

    # Check if the message is in a private chat
    if update.message.chat.type != "private":
        await update.message.reply_text("Please send the bot token in a private message.")
        return

    # Check if a token was provided
    if not context.args:
        await update.message.reply_text("Usage: /setbot <bot_token>")
        return

    bot_token = context.args[0].strip()

    try:
        # Validate the token by initializing a Bot instance
        test_bot = context.bot.__class__(bot_token)
        await test_bot.get_me()  # Test the token by fetching bot info
    except InvalidToken:
        await update.message.reply_text("Invalid bot token. Please check and try again.")
        return
    except TelegramError as e:
        await update.message.reply_text(f"Error validating token: {e}")
        return

    # Stop any existing controlled bot
    if controlled_bot_app:
        await controlled_bot_app.stop()
        controlled_bot_app = None

    # Initialize the controlled bot
    try:
        controlled_bot_app = Application.builder().token(bot_token).build()
        controlled_bot_app.add_handler(
            MessageHandler(Filters.all & ~Filters.command, handle_message)
        )
        await controlled_bot_app.initialize()
        await controlled_bot_app.start()
        await controlled_bot_app.updater.start_polling()
        await update.message.reply_text(
            f"Success! The bot {controlled_bot_app.bot.name} is now active and will "
            "react with 👍 to all messages in groups/channels where it's added. "
            "Ensure it has admin permissions in channels."
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to start the bot: {e}")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle new messages for the controlled bot and add a reaction."""
    try:
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
            reaction=[ReactionTypeEmoji("👍")],
            is_big=False
        )
        logger.info(f"Reacted to message {update.message.message_id} in chat {update.effective_chat.id}")
    except TelegramError as e:
        logger.error(f"Failed to react to message: {e}")
        # Optionally notify the main bot's creator in private chat
        if update.effective_chat.type == "private":
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Error reacting to message: {e}. Ensure the bot has admin permissions in channels."
            )

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Handle errors for the main bot."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again or contact support.")

def main() -> None:
    """Start the main bot."""
    app = Application.builder().token("8214380019:AAEOPG5ZwmzTNAwGf33n1dPyZJxjnyHHWYE").build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setbot", set_bot))
    app.add_error_handler(error_handler)

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
