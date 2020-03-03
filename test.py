import os, dotenv
import telebot

dotenv.load_dotenv()
token = os.environ['dev_token']
bot = telebot.TeleBot(token)
keyboard = telebot.types.InlineKeyboardMarkup()
test_button = telebot.types.InlineKeyboardButton(text="test1",
                                                 callback_data="testing1")
keyboard.add(test_button)
test_button = telebot.types.InlineKeyboardButton(text="test2",
                                                 callback_data="testing2")
keyboard.add(test_button)
test_button = telebot.types.InlineKeyboardButton(text="test3",
                                                 callback_data="exit")
keyboard.add(test_button)
keyboard_f_test = telebot.types.ReplyKeyboardMarkup(True)
keyboard_f_test.row('1', '2', '3')
print('start')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if 'testing' in call.data:
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.data,
                                    parse_mode='Markdown')
        msg = bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)
    else:
        bot.send_message(call.from_user.id, call.data, reply_markup=keyboard_f_test)
        # bot.register_next_step_handler_by_chat_id(call.from_user.id, test_f)


def test_f(message):
    # bot.send_message(message.chat.id, 'start', reply_markup=keyboard)
    if message.text in ['1', '2', '3']:
        bot.send_message(message.chat.id, message.text, reply_markup=keyboard)
    bot.register_next_step_handler(message, test_f)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'start', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    bot.send_message(message.chat.id, 'отправь еще раз')
    # bot.register_next_step_handler(message, test_f)


bot.polling()
