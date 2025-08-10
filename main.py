import telebot, json, os, random
from telebot.types import ReactionTypeEmoji

MAIN_BOT_TOKEN = "8214380019:AAEOPG5ZwmzTNAwGf33n1dPyZJxjnyHHWYE"
TOKENS_FILE = "tokens.json"
REACTION_POOL = ["❤️", "😂", "🔥", "😎", "👏", "🎉", "👍", "🤖"]

def load_tokens():
    return json.load(open(TOKENS_FILE)) if os.path.exists(TOKENS_FILE) else []

def save_tokens(tokens):
    json.dump(tokens, open(TOKENS_FILE, 'w'))

main_bot = telebot.TeleBot(MAIN_BOT_TOKEN)
bot_tokens = load_tokens()

@main_bot.message_handler(commands=['start'])
def start(message):
    main_bot.reply_to(message,
        "Main Bot ready!\n"
        "/addtoken – add a bot token\n"
        "/listtokens – see tokens\n"
        "/deltoken – delete a bot token")

@main_bot.message_handler(commands=['addtoken'])
def cmd_addtoken(message):
    msg = main_bot.reply_to(message, "Send the bot token:")
    main_bot.register_next_step_handler(msg, save_token)

def save_token(message):
    token = message.text.strip()
    if token not in bot_tokens:
        bot_tokens.append(token)
        save_tokens(bot_tokens)
        main_bot.reply_to(message, "Bot token saved!")
    else:
        main_bot.reply_to(message, "Token already added or invalid.")

@main_bot.message_handler(commands=['listtokens'])
def cmd_listtokens(message):
    if bot_tokens:
        text = "\n".join(f"{i+1}. {t}" for i, t in enumerate(bot_tokens))
    else:
        text = "No tokens saved."
    main_bot.reply_to(message, text)

@main_bot.message_handler(commands=['deltoken'])
def cmd_deltoken(message):
    if not bot_tokens:
        main_bot.reply_to(message, "No tokens to delete.")
        return
    text = "\n".join(f"{i+1}. {t}" for i, t in enumerate(bot_tokens))
    msg = main_bot.reply_to(message, f"Send a number to delete:\n{text}")
    main_bot.register_next_step_handler(msg, delete_token)

def delete_token(message):
    try:
        idx = int(message.text.strip()) - 1
        if 0 <= idx < len(bot_tokens):
            removed = bot_tokens.pop(idx)
            save_tokens(bot_tokens)
            main_bot.reply_to(message, f"Removed token: {removed}")
        else:
            main_bot.reply_to(message, "Invalid index.")
    except:
        main_bot.reply_to(message, "Send a valid number.")

@main_bot.channel_post_handler(func=lambda m: True)
@main_bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def react_any(message):
    for token in bot_tokens:
        try:
            b = telebot.TeleBot(token)
            emoji = random.choice(REACTION_POOL)
            b.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji)],
                is_big=False
            )
        except Exception as e:
            print(f"Error with bot {token}: {e}")

if __name__ == "__main__":
    main_bot.infinity_polling()
