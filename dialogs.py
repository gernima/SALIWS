import telebot
from keyboards import *
from pickle import load
from base_var_and_func import *
from time import time


def yes_or_no_skins(call, bot):
    spell = call.data.split('_')[4:]
    if 'sewer_skins_shop_yes' in call.data:
        edit_message(bot, call, f'Вы приобрели {spell}', get_sewer_skins_shop_keyboard(call))
    else:
        edit_message(bot, call, 'Может быть вы хотите что-то еще?', get_sewer_skins_shop_keyboard(call))


def yes_or_no_quest(call, bot):
    chat_id = call.from_user.id
    if 'yes' in call.data:
        quest = call.data.split('_')[1]
        saves[chat_id]['quests'][quest] = False
        saves[chat_id]['quests_time'][quest] = int(time())
        for i in [x.split(':') for x in QUESTS[quest]['add_items'].keys()]:
            inventory_add_item(chat_id, i[0], i[1])
        if saves[chat_id]['buffer']['quest_keyboard_accept'] is None:
            send_map(chat_id, bot)
        else:
            edit_message(bot, call, 'Вы приняли квест!', saves[chat_id]['buffer']['quest_keyboard_accept'])
        save_to_db(chat_id)
    else:
        if saves[chat_id]['buffer']['quest_keyboard_decline'] is None:
            send_map(chat_id, bot)
        else:
            edit_message(bot, call, 'Вы отказались от квеста!', saves[chat_id]['buffer']['quest_keyboard_decline'])
    saves[chat_id]['buffer']['quest_keyboard'] = None


def librarian(call, bot):
    chat_id = call.from_user.id
    if call.data == 'librarian_talk_hi':
        edit_message(bot, call, 'Здравствуйте!', get_librarian_keyboard())
    elif call.data == "librarian_talk_bye":
        edit_message(bot, call, load_map(chat_id), get_move_keyboard())
    elif 'librarian_spells_shop' == call.data:
        edit_message(bot, call, 'Что-то хотите?', get_librarian_spells_shop_keyboard(call))
    elif 'librarian_spells_shop_' in call.data:
        spell = call.data.split('_')[3]
        if 'yes' in call.data:
            if saves[chat_id]['gold'] >= SPELLS_SHOP['_'.join(saves[chat_id]['pos']['map'].split('_')[:2])][spell]:
                saves[chat_id]['spells'].append(spell)
                saves[chat_id]['gold'] -= \
                SPELLS_SHOP['_'.join(saves[chat_id]['pos']['map'].split('_')[:2])][spell]
                save_to_db(chat_id)
                edit_message(bot, call, 'Что-то еще?', get_librarian_spells_shop_keyboard(call))
            else:
                bot.answer_callback_query(callback_query_id=call.id, text='Недостаточно золота')
                edit_message(bot, call, 'Жаль, может другое?',
                             get_librarian_spells_shop_keyboard(call))
        elif 'no' in call.data:
            edit_message(bot, call, 'Может быть тогда что-то другое?',
                         get_librarian_spells_shop_keyboard(call))
        elif 'return' in call.data:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text='Есть какие-то еще вопросы?', reply_markup=get_librarian_keyboard())
        else:
            edit_message(bot, call, f'{spell}\n\n{SPELLS[spell]["des"]}\nЦена: {SPELLS_SHOP["_".join(saves[chat_id]["pos"]["map"].split("_")[:2])][spell]} золота\nКупить?', get_librarian_spells_shop_item_keyboard(spell))
    return saves


def get_quest_des_message(name):
    text = '\n'.join(QUESTS[name]['des'].split(';'))
    if QUESTS[name]['need_items']:
        text += '\n' + 'Требования:' + '\n' + '\n'.join([f"-{v} {k}" for k, v in QUESTS[name]['need_items'].items()])
    if QUESTS[name]['rewards_items']:
        text += '\n' + 'Награда:' + '\n' + '\n'.join([f"-{v} {k}" for k, v in QUESTS[name]['des'].items()])
    if QUESTS[name]['rewards_xp']:
        text += '\n' + f'Опыт: {QUESTS[name]["rewards_xp"]}'
    return text


def get_quest_des_complete_message(name):
    text = '\n'.join(QUESTS[name]['text_complete'].split(';'))
    if QUESTS[name]['rewards_items']:
        text += '\n' + 'Награда:' + '\n' + '\n'.join([f"-{x.split(':')[1]} {x.split(':')[0]}" for x in QUESTS[name]['rewards_items'].split(';')])
    if QUESTS[name]['rewards_xp']:
        text += '\n' + f'Опыт: {QUESTS[name]["rewards_xp"]}'
    return text


def check_quest_complete_and_logic(chat_id, quest, keyboard, bot, call, keyboard_accept, keyboard_decline):
    if quest in saves[chat_id]['quests'] and saves[chat_id]['quests'][quest]:
        del saves[chat_id]['quests'][quest]
        saves[chat_id]['quests_time'][quest] = int(time())
        if QUESTS[quest]['need_items']:
            for item, n in QUESTS[quest]['need_items'].items():
                inventory_del_item(chat_id, item, n)
        if QUESTS[quest]['rewards_items']:
            for item, n in QUESTS[quest]['rewards_items'].items():
                inventory_add_item(chat_id, item, n)
        if QUESTS[quest]['rewards_xp']:
            saves[chat_id]['xp'] += QUESTS[quest]['rewards_xp']
            check_lvl_up(chat_id)
        save_to_db(chat_id)
        edit_message(bot, call, get_quest_des_complete_message(quest), keyboard_accept)
    else:
        saves[chat_id]['buffer']['quest_keyboard_accept'] = keyboard_accept
        saves[chat_id]['buffer']['quest_keyboard_decline'] = keyboard_decline
        edit_message(bot, call, get_quest_des_message(quest), get_quest_keyboard(quest))


def sewer(call, bot):
    chat_id = call.from_user.id
    if call.data == 'sewer_skins_shop':
        edit_message(bot, call, 'Прикупишь нарядик?)', get_sewer_skins_shop_keyboard(call))
    elif call.data == 'sewer_talk_hi':
        edit_message(bot, call, 'Приветики!', get_sewer_keyboard(call))
    elif call.data == 'sewer_talk_bye':
        edit_message(bot, call, load_map(chat_id), get_move_keyboard())
    elif 'sewer_quest_Сбор паутины для швеи' == call.data:
        quest = call.data.split('_')[2]
        check_quest_complete_and_logic(chat_id=chat_id, quest=quest, keyboard=get_sewer_keyboard(call), bot=bot,
                                       call=call, keyboard_accept=get_sewer_keyboard(call, show_quest_tf=False),
                                       keyboard_decline=get_sewer_keyboard(call))
    elif 'sewer_skins_shop_' in call.data:
        skin = call.data.split('_')[3]
        if 'yes' in call.data:
            if saves[chat_id]['gold'] >= SKINS_SHOP['_'.join(saves[chat_id]['pos']['map'].split('_')[:2])][skin]:
                saves[chat_id]['skin'] = skin
                saves[chat_id]['gold'] -= SKINS_SHOP['_'.join(saves[chat_id]['pos']['map'].split('_')[:2])][skin]
                save_to_db(chat_id)
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
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text='Есть какие-то еще вопросы?', reply_markup=get_sewer_keyboard(call))
        else:
            edit_message(bot, call, f'Желаете купить {skin}, в данный момент у вас {saves[chat_id]["skin"]}', get_sewer_skins_shop_yes_or_no_keyboard(skin))


def arena(call, bot):
    chat_id = call.from_user.id
    rules = "В мои обязанности входит рассказать правила перед этим, так что буду краток. Твоя задача зарегестрироваться и ждать момента, когда тебе подберется соперник. Вы будете сражаться, нанося друг другу удары по очереди. Каждому на ход дается максимум 1 минута, не вложился в рамки? Тогда пропускаешь ход и он переходит противнику. Ах да! Насчет смерти, если умрешь на арене то умрешь по настоящему, так что береги жизнь. Мне нужны хорошие бойцы."
    if "reg" in call.data:
        if 'yes' in call.data:
            arena_queue.append(chat_id)
            edit_message(bot, call, 'Ищем соперника, жди...', get_arena_reg_keyboard(call))
        elif 'leave' in call.data:
            if chat_id in arena_queue:
                arena_queue.remove(chat_id)
            edit_message(bot, call, 'Ну?', get_arena_man_keyboard())
        elif 'no' in call.data:
            if chat_id in arena_queue:
                arena_queue.remove(chat_id)
            edit_message(bot, call, rules, get_arena_reg_keyboard(call))
        else:
            edit_message(bot, call, rules, get_arena_reg_keyboard(call))
    elif 'bye' in call.data:
        send_map(call, bot)
