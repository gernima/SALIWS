import telebot
from keyboards import *
from pickle import load
from base_var_and_func import *
from threading import Thread
from time import time


def check_quest_complete():
    while True:
        if len(saves.keys()) != 1:
            for chat_id in saves.keys():
                for quest in saves[chat_id]['quests'].keys():
                    time_plus = cur.execute(f"""Select time from quests where name = '{quest}'""").fetchone()[0]
                    # TODO: check items for quest complete
                    # if time() - saves[chat_id]['quests'][quest]['time'] > time_plus and not saves[chat_id]['quests'][quest]['completed']:
                    #     saves[chat_id]['quests'][quest]['completed'] = True


thread_check_quest = Thread(target=check_quest_complete)
thread_check_quest.start()


def edit_message(bot, call, text, keyboard):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=text,
                          reply_markup=keyboard)


def yes_or_no_skins(call, bot):
    spell = call.data.split('_')[4:]
    if 'sewer_skins_shop_yes' in call.data:
        edit_message(bot, call, f'Вы приобрели {spell}', get_sewer_skins_shop_keyboard(call))
    else:
        edit_message(bot, call, 'Может быть вы хотите что-то еще?', get_sewer_skins_shop_keyboard(call))


def yes_or_no_quest(call, bot):
    if 'yes' in call.data:
        quest = call.data.split('_')[1]
        saves[call.from_user.id]['quests'][quest] = QUESTS_TEMPLATE
        saves[call.from_user.id]['quests'][quest]['time'] = time()
        edit_message(bot, call, 'Вы приняли квест!', saves[call.from_user.id]['buffer']['quest_keyboard'])
    else:
        edit_message(bot, call, 'Вы отказались от квеста!', saves[call.from_user.id]['buffer']['quest_keyboard'])
    saves[call.from_user.id]['buffer']['quest_keyboard'] = None


def librarian(call, bot):
    if call.data == 'librarian_talk_hi':
        edit_message(bot, call, 'Здравствуйте!', get_librarian_keyboard())
    elif call.data == "librarian_talk_bye":
        edit_message(bot, call, load_map(call.from_user.id), get_move_keyboard())
    elif 'librarian_spells_shop' == call.data:
        edit_message(bot, call, 'Что-то хотите?', get_librarian_spells_shop_keyboard(call))
    elif 'librarian_spells_shop_' in call.data:
        spell = call.data.split('_')[3]
        if 'yes' in call.data:
            if saves[call.from_user.id]['gold'] >= \
                    SPELLS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])][spell]:
                saves[call.from_user.id]['spells'].append(spell)
                saves[call.from_user.id]['gold'] -= \
                SPELLS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])][spell]
                save_to_db(call.from_user.id)
                edit_message(bot, call, 'Что-то еще?', get_librarian_spells_shop_keyboard(call))
            else:
                bot.answer_callback_query(callback_query_id=call.id, text='Недостаточно золота')
                edit_message(bot, call, 'Жаль, может другое?',
                             get_librarian_spells_shop_keyboard(call))
        elif 'no' in call.data:
            edit_message(bot, call, 'Может быть тогда что-то другое?',
                         get_librarian_spells_shop_keyboard(call))
        elif 'return' in call.data:
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='Есть какие-то еще вопросы?', reply_markup=get_librarian_keyboard())
        else:
            des = cur.execute(f"""Select des from spells where name='{spell}'""").fetchone()[0]
            edit_message(bot, call, f'{spell}\n\n{des}\nЦена: {SPELLS_SHOP["_".join(saves[call.from_user.id]["pos"]["map"].split("_")[:2])][spell]} золота\nКупить?', get_librarian_spells_shop_item_keyboard(spell))
    return saves


def get_quest_des_message(name):
    return '\n'.join(cur.execute(f"""Select des from quests where name='{name}'""").fetchone()[0].split(';'))


def sewer(call, bot):
    if call.data == 'sewer_skins_shop':
        edit_message(bot, call, 'Прикупишь нарядик?)', get_sewer_skins_shop_keyboard(call))
    elif call.data == 'sewer_talk_hi':
        edit_message(bot, call, 'Приветики!', get_sewer_keyboard(call))
    elif call.data == 'sewer_talk_bye':
        edit_message(bot, call, load_map(call.from_user.id), get_move_keyboard())
    elif 'sewer_quest_Сбор паутины для швеи' == call.data:
        saves[call.from_user.id]['buffer']['quest_keyboard'] = get_sewer_keyboard(call)
        edit_message(bot, call, get_quest_des_message(call.data.split('_')[2]), get_quest_keyboard(call.data.split('_')[2]))
    elif 'sewer_skins_shop_' in call.data:
        skin = call.data.split('_')[3]
        if 'yes' in call.data:
            if saves[call.from_user.id]['gold'] >= SKINS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])][skin]:
                saves[call.from_user.id]['skin'] = skin
                saves[call.from_user.id]['gold'] -= SKINS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])][skin]
                save_to_db(call.from_user.id)
                edit_message(bot, call, 'А тебе идет, может подойдет что-то еще?',
                             get_sewer_skins_shop_keyboard(call))
            else:
                bot.answer_callback_query(callback_query_id=call.id,
                                          text='Недостаточно золота')
                edit_message(bot, call, 'Может быть тогда другой тебе подойдет тебе лучше',
                             get_sewer_skins_shop_keyboard(call))
        elif 'no' in call.data:
            edit_message(bot, call, 'Может быть тогда другой тебе подойдет тебе лучше', get_sewer_skins_shop_keyboard(call))
        elif 'return' in call.data:
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='Есть какие-то еще вопросы?', reply_markup=get_sewer_keyboard(call))
        else:
            edit_message(bot, call, f'Желаете купить {skin}, в данный момент у вас {saves[call.from_user.id]["skin"]}', get_sewer_skins_shop_yes_or_no_keyboard(skin))
