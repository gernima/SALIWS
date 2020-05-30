from telebot import types
from fight import *
from base_var_and_func import *
from pickle import load
from time import time

choice_mode_keyboard = types.InlineKeyboardMarkup()  # перед началом игры, после /start
choice_mode_keyboard.add(types.InlineKeyboardButton('Одиночная игра', callback_data='mode_single'))
# choice_mode_keyboard.add(types.InlineKeyboardButton('Сетевая игра (В идеи)', callback_data='mode_multiplayer'))


def send_hero_char(call, bot):
    try:
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f"Ник: {saves[call.from_user.id]['name']}\n"
                                   f"Опыт: {saves[call.from_user.id]['xp']}/{saves[call.from_user.id]['need_xp']}\n"
                                   f"Способности: ({', '.join(saves[call.from_user.id]['spells'])})\n"
                                   f"Скин: {saves[call.from_user.id]['skin']}\n"
                                   f"Квесты: ({', '.join(saves[call.from_user.id]['quests'])})\n"
                                   f"Прокачка характеристик:",
                              reply_markup=get_keyboard_characteristic(call))
    except:
        print('char too long', f"Ник: {saves[call.from_user.id]['name']}\n"
                               f"Опыт: {saves[call.from_user.id]['xp']}/{saves[call.from_user.id]['need_xp']}\n"
                               f"Способности: ({', '.join(saves[call.from_user.id]['spells'])})\n"
                               f"Скин: {saves[call.from_user.id]['skin']}\n"
                               f"Квесты: ({', '.join(saves[call.from_user.id]['quests'])})\n"
                               f"Прокачка характеристик:")


def get_map_list(chat_id):
    with open(f'levels/{saves[chat_id]["pos"]["map"]}.txt', 'rb') as f:
        map_list = load(f)
        map_list[saves[chat_id]["pos"]['y']][saves[chat_id]["pos"]['x']] = saves[chat_id]["skin"]
        return map_list


def load_map(chat_id):
    a = get_map_list(chat_id)
    for i in range(len(a)):
        for j in range(len(a[i])):
            if ':' in a[i][j]:
                a[i][j] = a[i][j].split(':')[0]
    return '\n'.join(''.join(x) for x in a)


def send_map(call, bot):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=load_map(call.from_user.id),
                          reply_markup=get_move_keyboard())


def send_inventory(call, bot):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text='💼💼💼💼💼',
                          reply_markup=get_inventory_keyboard(call))


def get_keyboard_characteristic(call):
    keyboard = types.InlineKeyboardMarkup()
    # reset_button = types.InlineKeyboardButton(text="Сброс", callback_data="reset")
    keyboard.add(types.InlineKeyboardButton(
        text="Очки характеристик {}".format(saves[call.from_user.id]['char']['free_char']),
        callback_data='points'))
    keyboard.add(types.InlineKeyboardButton(text="Сила ({}) | + 1".format(saves[call.from_user.id]['char']['strength']),
                                                         callback_data="char_strength"))
    keyboard.add(types.InlineKeyboardButton(text="Ловкость ({}) | + 1".format(saves[call.from_user.id]['char']['agility']),
                                                         callback_data="char_agility"))
    keyboard.add(types.InlineKeyboardButton(text="Удача ({}) | + 1".format(saves[call.from_user.id]['char']['lucky']),
                                                         callback_data="char_lucky"))
    keyboard.add(types.InlineKeyboardButton(text="Интеллект ({}) | + 1".format(saves[call.from_user.id]['char']['intelligence']),
                                                         callback_data="char_intelligence"))
    keyboard.add(types.InlineKeyboardButton(text="Мудрость ({}) | + 1".format(saves[call.from_user.id]['char']['wisdom']),
                                                         callback_data="char_wisdom"))
    keyboard.add(types.InlineKeyboardButton(text="Выносливость ({}) | + 1".format(saves[call.from_user.id]['char']['stamina']),
                                                         callback_data="char_stamina"))
    keyboard.add(
        types.InlineKeyboardButton(text="Назад".format(saves[call.from_user.id]['char']['stamina']),
                                   callback_data="char_return"))
    # keyboard.add(reset_button)
    return keyboard


def get_inventory_item_keyboard(call, used=False):
    keyboard = types.InlineKeyboardMarkup()
    item = call.data.split('_')[2]
    if used:
        keyboard.add(types.InlineKeyboardButton('Использовать', callback_data=f'inventory_item__use_{item}'),
                     types.InlineKeyboardButton('Назад', callback_data=f'inventory_item_return'))
    else:
        keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'inventory_item_return'))
    return keyboard


def get_inventory_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'inventory_return'))
    for item in list(saves[call.from_user.id]['inventory'].keys())[saves[call.from_user.id]['buffer']['inventory_page'] *
                saves[call.from_user.id]['buffer']['inventory_slice']:
                (1 + saves[call.from_user.id]['buffer']['inventory_page']) * saves[call.from_user.id]['buffer']['inventory_slice']]:
        keyboard.add(types.InlineKeyboardButton(f'{item} x {saves[call.from_user.id]["inventory"][item]}', callback_data=f'inventory_item_{item}'))
    keyboard.add(types.InlineKeyboardButton('След', callback_data=f'inventory_next_page'),
                 types.InlineKeyboardButton('Пред', callback_data=f'inventory_prev_page'))
    return keyboard


def get_move_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📚', callback_data=f'move_chars'),
                 types.InlineKeyboardButton('⬆', callback_data=f'move_up'),
                 types.InlineKeyboardButton('💼', callback_data=f'move_inventory'))
    keyboard.add(types.InlineKeyboardButton('⬅', callback_data=f'move_left'),
                 types.InlineKeyboardButton('⬇', callback_data=f'move_down'),
                 types.InlineKeyboardButton('➡', callback_data=f'move_right'))
    keyboard.add(types.InlineKeyboardButton('Главное меню', callback_data=f'move_main_menu'))
    return keyboard


def get_fight_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Атака', callback_data=f'fight_attack_{0}'),
                 types.InlineKeyboardButton('Уклонение', callback_data=f'fight_dodge_{0}'),
                 types.InlineKeyboardButton('Блок', callback_data=f'fight_block_{0}'))
    keyboard.add(types.InlineKeyboardButton("Способности", callback_data=f'fight_spells_{0}'),
                 types.InlineKeyboardButton('Инвентарь', callback_data=f'fight_inv_{0}'),
                 types.InlineKeyboardButton('Сбежать', callback_data=f'fight_away_{0}'))
    return keyboard


def get_librarian_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"librarian_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин способностей", callback_data=f"librarian_spells_shop"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data=f"librarian_talk_bye"))
    return keyboard


def get_keyboard_drop_from_enemy(call):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(saves[call.from_user.id]['buffer']["drop_items"])):
        keyboard.add(types.InlineKeyboardButton(text=saves[call.from_user.id]['buffer']["drop_items"][i], callback_data=f"drop_from_enemy_{i}"))
    keyboard.add(types.InlineKeyboardButton('Готово!', callback_data='fight_ready'))
    return keyboard


def get_spells_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='назад',
                                            callback_data=f"spell_{0}_return_to_fight"))
    for spell in saves[call.from_user.id]['spells']:
        keyboard.add(types.InlineKeyboardButton(text=spell, callback_data=f"spell_{0}_use_{spell}"))
    return keyboard


def get_sewer_skins_shop_keyboard(call):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data="sewer_skins_shop_return"))
    a = []
    n = 0
    for skin, cost in SKINS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])].items():
        if skin != saves[call.from_user.id]['skin']:
            n += 1
            a.append(types.InlineKeyboardButton(text=f'{skin} | {cost}', callback_data=f"sewer_skins_shop_{skin}"))
        if n == 5:
            keyboard.add(a[0], a[1], a[2], a[3], a[4])
            a = []
            n = 0
    return keyboard


def get_keyboard_enemies_fight(call):
    keyboard = types.InlineKeyboardMarkup()
    # splited_data = len(get_map_list(call.from_user.id)[saves[call.from_user.id]['pos']['y']][saves[call.from_user.id]['pos']['x']].split(':'))
    # if splited_data > 1:
    #     for enemy in
    #     enemies_n = splited_data - 1
    # else:
    #     enemies_n = 1
    # for enemy in enemies_n:
    #     keyboard.add(types.InlineKeyboardButton(text=, callback_data=f"fight_select_enemy_{enemy}"))
    return keyboard


def get_librarian_spells_shop_item_keyboard(spell):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"librarian_spells_shop_{spell}_yes"),
                 types.InlineKeyboardButton(text="Нет", callback_data=f"librarian_spells_shop_{spell}_no"))
    return keyboard


def get_librarian_spells_shop_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data="librarian_spells_shop_return"))
    new_spells = list(SPELLS_SHOP['_'.join(saves[call.from_user.id]['pos']['map'].split('_')[:2])].keys())
    for spell in saves[call.from_user.id]['spells']:
        if spell in new_spells:
            new_spells.remove(spell)
    for spell in new_spells:
        keyboard.add(types.InlineKeyboardButton(text=spell, callback_data=f"librarian_spells_shop_{spell}"))
    return keyboard


def show_quest(chat_id, name):
    if name in saves[chat_id]['quests'].keys():
        for quest in saves[chat_id]['quests'].keys():
            a = cur.execute(f"""Select time, need_lvl, need_items from quests where name = '{quest}'""").fetchall()
            tf = True
            for item in a[2]:
                if item in saves[chat_id]['inventory'] and tf:
                    tf = True
                elif tf:
                    tf = False
                    break
            if saves[chat_id]['quests'][quest]['completed'] or (a[1] <= saves[chat_id]['lvl'] and tf):
                return True
            if time() - saves[chat_id]['quests'][quest]['time'] < a[0]:
                return False
    return True


def get_sewer_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"sewer_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин скинов", callback_data=f"sewer_skins_shop"))
    if show_quest(call.from_user.id, 'sewer'):
        keyboard.add(types.InlineKeyboardButton(text="Сбор паутины", callback_data=f"sewer_quest_Сбор паутины для швеи"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data=f"sewer_talk_bye"))
    return keyboard


def get_sewer_skins_shop_yes_or_no_keyboard(skin):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"sewer_skins_shop_{skin}_yes"),
                 types.InlineKeyboardButton(text="Нет", callback_data=f"sewer_skins_shop_{skin}_no"))
    return keyboard


def get_quest_keyboard(quest):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Принять", callback_data=f"quest_{quest}_yes"),
                 types.InlineKeyboardButton(text="Отказаться", callback_data=f"quest_{quest}_no"))
    return keyboard



