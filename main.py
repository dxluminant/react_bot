import telebot
import json
import os
import random
import threading

MAIN_BOT_TOKEN = "8214380019:AAEOPG5ZwmzTNAwGf33n1dPyZJxjnyHHWYE"
TOKENS_FILE = "tokens.json"
REACTION_POOL = ["❤️", "😂", "🔥", "😎", "👏", "🎉", "👍", "🤖"]

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except json.JSONDecodeError:
            return []
    return []

def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f)

main_bot = telebot.TeleBot(MAIN_BOT_TOKEN)
bot_tokens = load_tokens()

@main_bot.message_handler(commands=['start'])
def start(message):
    main_bot.reply_to(message,
        "Main Bot ready!\n"
        "/addtoken – Add a bot token\n"
        "/listtokens – List saved tokens\n"
        "/deltoken – Delete a bot token")

@main_bot.message_handler(commands=['addtoken'])
def cmd_addtoken(message):
    msg = main_bot.reply_to(message, "Send the bot token:")
    main_bot.register_next_step_handler(msg, save_token)

def save_token(message):
    token = message.text.strip()
    if token not in bot_tokens:
        bot_tokens.append(token)
        save_tokens(bot_tokens)
        main_bot.reply_to(message, "✅ Bot token saved!")
    else:
        main_bot.reply_to(message, "⚠️ Token already added or invalid.")

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
    msg = main_bot.reply_to(message, f"Send the number of the token to delete:\n{text}")
    main_bot.register_next_step_handler(msg, delete_token)

def delete_token(message):
    try:
        idx = int(message.text.strip()) - 1
        if 0 <= idx < len(bot_tokens):
            removed = bot_tokens.pop(idx)
            save_tokens(bot_tokens)
            main_bot.reply_to(message, f"✅ Removed token:\n{removed}")
        else:
            main_bot.reply_to(message, "⚠️ Invalid number.")
    except:
        main_bot.reply_to(message, "⚠️ Please send a valid number.")

def bot_reply(token, chat_id, message_id):
    try:
        b = telebot.TeleBot(token)
        emoji = random.choice(REACTION_POOL)
        b.send_message(chat_id=chat_id, text=emoji, reply_to_message_id=message_id)
    except Exception as e:
        print(f"Error with bot {token}: {e}")

@main_bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup", "channel"])
def handle_new_message(message):
    for token in bot_tokens:
        threading.Thread(target=bot_reply, args=(token, message.chat.id, message.message_id)).start()

if __name__ == "__main__":
    print("Main bot is running...")
    main_bot.infinity_polling()
