import telebot
from keyboards import *
from pickle import load

SEWER_SKINS_SHOP = {'🤡': 100, '😒': 100, '😡': 100, '🤓': 100, '😀': 100, '😈': 100,
                    '💩': 100, '👻': 100, '👺': 100, '👹': 100, '👿': 100, '💀': 100}


def get_map_list(chat_id, saves):
    with open(f'levels/{saves[chat_id]["pos"]["map"]}.txt', 'rb') as f:
        map_list = load(f)
        map_list[saves[chat_id]["pos"]['y']][saves[chat_id]["pos"]['x']] = saves[chat_id]["skin"]
        return map_list


def load_map(chat_id, saves):
    return '\n'.join(''.join(x) for x in get_map_list(chat_id, saves))


def edit_message(bot, call, text, keyboard):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=text,
                          reply_markup=keyboard)


def librarian(call, bot, saves):
    if call.data == 'librarian_talk_hi':
        edit_message(bot, call, 'Здравствуйте!', get_librarian_keyboard())
    elif call.data == "librarian_talk_bye":
        edit_message(bot, call, load_map(call.from_user.id, saves), get_move_keyboard())
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
        edit_message(bot, call, load_map(call.from_user.id, saves), get_move_keyboard())
    elif 'sewer_quest_spider_web' == call.data:
        # edit_message(bot, call, 'Выбирай', None)
        pass
    return saves
