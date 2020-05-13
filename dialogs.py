import telebot
from keyboards import *

SEWER_SKINS_SHOP = {'🤡': 100, '😒': 100, '😡': 100, '🤓': 100, '😀': 100, '😈': 100,
                    '💩': 100, '👻': 100, '👺': 100, '👹': 100, '👿': 100, '💀': 100}


def edit_message(bot, call, text, keyboard):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=text,
                          reply_markup=keyboard)


def librarian(call, bot, saves):
    if call.data == 'librarian_talk_hi':
        edit_message(bot, call, 'Здравствуйте!', get_librarian_keyboard())
    elif call.data == "librarian_talk_bye":
        edit_message(bot, call, 'До свидания!', get_move_keyboard())
    elif call.data == 'librarian_spells_shop':
        pass
    return saves


def sewer(call, bot, saves):
    if call.data == 'sewer_spells_shop':
        # edit_message(bot, call.from_user.id, 'Все, что я могу предложить:', )
        pass
    elif call.data == 'sewer_talk_hi':
        edit_message(bot, call, 'Приветики!', get_sewer_keyboard())
    elif call.data == 'sewer_talk_bye':
        edit_message(bot, call, 'Пока!', get_move_keyboard())
    elif 'sewer_quest_spider_web' == call.data:
        # edit_message(bot, call, 'Выбирай', None)
        pass
    return saves
