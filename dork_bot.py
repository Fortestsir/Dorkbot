
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

admin_id = 123456789  # Replace with your Telegram ID

# Predefined dork categories
dork_categories = {
    "Admin Panels": [
        'site:{target} inurl:admin',
        'site:{target} inurl:login',
        'site:{target} intitle:"admin login"'
    ],
    "File Leaks": [
        'site:{target} ext:sql | ext:db | ext:log',
        'site:{target} filetype:env',
        'site:{target} filetype:pdf'
    ],
    "Indexes": [
        'site:{target} intitle:"index of /"',
        'site:{target} intitle:"index of" passwd',
        'site:{target} intitle:"index of" config'
    ]
}

user_states = {}
last_dork_sent = {}
user_favorites = {}  # chat_id: [dork1, dork2, ...]
user_engine_choice = {}  # chat_id: 'google' or 'duck'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    for cat in dork_categories:
        markup.add(InlineKeyboardButton(cat, callback_data=cat))
    markup.add(InlineKeyboardButton("Custom Dork", callback_data="custom"))
    bot.send_message(message.chat.id, "Welcome to the Dorking Bot!\nChoose a category:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    category = call.data

    if category == "custom":
        user_states[chat_id] = "awaiting_custom"
        bot.send_message(chat_id, "Send in this format:\n`domain keyword filetype`\nExample: `example.com password txt`", parse_mode="Markdown")
    else:
        user_states[chat_id] = f"awaiting_target_{category}"
        bot.send_message(chat_id, f"Send target domain for `{category}`:", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_input(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    engine = user_engine_choice.get(chat_id, 'google')
    base_url = "https://www.google.com/search?q=" if engine == 'google' else "https://duckduckgo.com/?q="

    if state.startswith("awaiting_target_"):
        category = state.split("_", 2)[2]
        target = message.text.strip()

        dorks = dork_categories[category]
        response = f"**{category} Dorks for `{target}`:**\n\n"
        for d in dorks:
            q = d.format(target=target)
            link = f"{base_url}{q.replace(' ', '+')}"
            response += f"- [{q}]({link})\n"
        last_dork_sent[chat_id] = q
        bot.send_message(chat_id, response, parse_mode="Markdown")
        user_states.pop(chat_id)

    elif state == "awaiting_custom":
        try:
            domain, keyword, filetype = message.text.strip().split()
            dork = f'site:{domain} intext:"{keyword}" filetype:{filetype}'
            link = f"{base_url}{dork.replace(' ', '+')}"
            response = f"**Custom Dork:**\n[{dork}]({link})"
            last_dork_sent[chat_id] = dork
            bot.send_message(chat_id, response, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "Invalid format. Try again like:\n`example.com password txt`", parse_mode="Markdown")
        user_states.pop(chat_id)

@bot.message_handler(commands=['save'])
def save_dork(message):
    chat_id = message.chat.id
    if chat_id in last_dork_sent:
        user_favorites.setdefault(chat_id, []).append(last_dork_sent[chat_id])
        bot.send_message(chat_id, "Dork saved to your favorites.")
    else:
        bot.send_message(chat_id, "No dork to save yet.")

@bot.message_handler(commands=['mydorks'])
def show_favorites(message):
    chat_id = message.chat.id
    favs = user_favorites.get(chat_id, [])
    if favs:
        engine = user_engine_choice.get(chat_id, 'google')
        base_url = "https://www.google.com/search?q=" if engine == 'google' else "https://duckduckgo.com/?q="
        response = "**Your Saved Dorks:**\n\n"
        for d in favs:
            link = f"{base_url}{d.replace(' ', '+')}"
            response += f"- [{d}]({link})\n"
        bot.send_message(chat_id, response, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "You have no saved dorks.")

@bot.message_handler(commands=['engine'])
def set_engine(message):
    chat_id = message.chat.id
    if 'duck' in message.text.lower():
        user_engine_choice[chat_id] = 'duck'
        bot.send_message(chat_id, "Switched to DuckDuckGo.")
    else:
        user_engine_choice[chat_id] = 'google'
        bot.send_message(chat_id, "Switched to Google.")

@bot.message_handler(commands=['updatedork'])
def update_dorks(message):
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "Only the admin can update dorks.")
        return
    try:
        parts = message.text.split(None, 2)
        category, new_dorks = parts[1], parts[2].split('|')
        dork_categories[category] = [d.strip() for d in new_dorks]
        bot.send_message(message.chat.id, f"Dorks for `{category}` updated.")
    except:
        bot.send_message(message.chat.id, "Format: `/updatedork Category dork1 | dork2 | dork3`", parse_mode="Markdown")

bot.polling()
