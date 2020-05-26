import telebot
from keyboards import *
from pickle import load
from base_var_and_func import *


#
# def get_map_list(chat_id, saves):
#     with open(f'levels/{saves[chat_id]["pos"]["map"]}.txt', 'rb') as f:
#         map_list = load(f)
#         map_list[saves[chat_id]["pos"]['y']][saves[chat_id]["pos"]['x']] = saves[chat_id]["skin"]
#         return map_list
#
#
# def load_map(chat_id, saves):
#     return '\n'.join(''.join(x) for x in get_map_list(chat_id, saves))


def edit_message(bot, call, text, keyboard):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=text,
                          reply_markup=keyboard)


def yes_or_no_skins(call, bot):
    spell = call.data.split('_')[4:]
    if 'sewer_skins_shop_yes' in call.data:
        edit_message(bot, call, f'Вы приобрели {spell}', keyboard_sewer_skins_shop(call))
    else:
        edit_message(bot, call, 'Может быть вы хотите что-то еще?', get_ke)


def librarian(call, bot):
    if call.data == 'librarian_talk_hi':
        edit_message(bot, call, 'Здравствуйте!', get_librarian_keyboard())
    elif call.data == "librarian_talk_bye":
        edit_message(bot, call, load_map(call.from_user.id, saves), get_move_keyboard())
    elif call.data == 'librarian_spells_shop':
        pass
    return saves


def sewer(call, bot):
    if call.data == 'sewer_spells_shop':
        edit_message(bot, call.from_user.id, 'Прикупишь нарядик?)', get_sewer_skins_shop_keyboard(call))
    elif call.data == 'sewer_talk_hi':
        edit_message(bot, call, 'Приветики!', get_sewer_keyboard())
    elif call.data == 'sewer_talk_bye':
        edit_message(bot, call, load_map(call.from_user.id), get_move_keyboard())
    elif 'sewer_quest_spider_web' == call.data:
        # edit_message(bot, call, 'Выбирай', None)
        pass
    return saves
