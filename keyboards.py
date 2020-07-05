from telebot import types
from fight import *
from base_var_and_func import *
from pickle import load
from time import time

choice_mode_keyboard = types.InlineKeyboardMarkup()  # перед началом игры, после /start
choice_mode_keyboard.add(types.InlineKeyboardButton('Одиночная игра', callback_data='mode_single'))
# choice_mode_keyboard.add(types.InlineKeyboardButton('Сетевая игра (В идеи)', callback_data='mode_multiplayer'))


def send_hero_char(call, bot):
    # print(call.from_user.id, saves[call.from_user.id])
    text = f"Ник: {saves[call.from_user.id]['name']}\n" \
           f"Опыт: {saves[call.from_user.id]['xp']}/{saves[call.from_user.id]['need_xp']}\n" \
           f"Золота: {saves[call.from_user.id]['gold']}\n" \
           f"Способности: ({', '.join(saves[call.from_user.id]['spells'])})\n" \
           f"Скин: {saves[call.from_user.id]['skin']}\n" \
           f"Квесты: ({', '.join(saves[call.from_user.id]['quests'])})\n" \
           f"Прокачка характеристик:"
    # try:
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=text,
                          reply_markup=get_keyboard_characteristic(call))
    # except:
    #     print('char too long', text)


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
    try:
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Вметимость инвентаря: {saves[call.from_user.id]["inventory_max_n"]}',
                              reply_markup=get_inventory_keyboard(call))
    except:
        pass


def get_keyboard_characteristic(call):
    keyboard = types.InlineKeyboardMarkup()
    # reset_button = types.InlineKeyboardButton(text="Сброс", callback_data="reset")
    keyboard.add(types.InlineKeyboardButton(
        text="Очки характеристик {}".format(saves[call.from_user.id]['char']['free_char']), callback_data='points'))
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


def get_yes_or_no_reg_name_keyboard(name):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Да', callback_data=f'reg_name_yes_{name}'),
                 types.InlineKeyboardButton('Нет', callback_data=f'reg_name_no_{name}'))
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


def get_arena_man_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Зарегистрироваться на бой", callback_data="arena_man_reg"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data="arena_man_bye"))
    return keyboard


def get_arena_reg_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    if call.from_user.id not in arena_queue:
        keyboard.add(types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="arena_man_reg_yes"))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Уйти с очереди", callback_data="arena_man_reg_no"))
    keyboard.add(types.InlineKeyboardButton(text="Может что-то другое?", callback_data="arena_man_reg_leave"))
    return keyboard


def get_arena_fight_keyboard(your_step=True):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Сдаться", callback_data=f'arena_fight_leave'))
    if your_step:
        keyboard.add(types.InlineKeyboardButton("Ваш ход", callback_data=f'arena_fight_your_step'))
        keyboard.add(types.InlineKeyboardButton('Атака', callback_data=f'arena_fight_attack'),
                     types.InlineKeyboardButton('Уклонение', callback_data=f'arena_fight_dodge'),
                     types.InlineKeyboardButton('Блок', callback_data=f'arena_fight_block'))
        keyboard.add(types.InlineKeyboardButton("Способности", callback_data=f'arena_fight_spells'),
                     types.InlineKeyboardButton('Инвентарь', callback_data=f'arena_fight_inv'))
    else:
        keyboard.add(types.InlineKeyboardButton("Ход противника", callback_data=f'arena_fight_opponent_step'))
    return keyboard


def get_librarian_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"librarian_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин способностей", callback_data=f"librarian_spells_shop"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data=f"librarian_talk_bye"))
    return keyboard


def get_shop_man_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Магазин", callback_data=f"shop_man_shop"))
    keyboard.add(types.InlineKeyboardButton(text="Уйти", callback_data=f"sewer_talk_bye"))
    return keyboard


def get_shop_items_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'shop_man_shop_return'))
    for item in list(SHOP.keys())[1:][saves[call.from_user.id]['buffer']['shop_page'] * saves[call.from_user.id]['buffer']['shop_page_slice']:
                (1 + saves[call.from_user.id]['buffer']['shop_page']) * saves[call.from_user.id]['buffer']['shop_page_slice']]:
        keyboard.add(types.InlineKeyboardButton(f'{item} x {SHOP[item]["n"]}',
                                                callback_data=f'shop_man_shop_{item}'))
    keyboard.add(types.InlineKeyboardButton('След', callback_data=f'shop_man_shop_next_page'),
                 types.InlineKeyboardButton('Пред', callback_data=f'shop_man_shop_prev_page'))
    return keyboard


def get_shop_buy_sell_nothing_keyboard(item):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f'Купить за {SHOP[item]["cost_buy"]}', callback_data=f'shop_man_shop_buy_{item}'))
    keyboard.add(types.InlineKeyboardButton(f'Продать за {SHOP[item]["cost_sell"]}', callback_data=f'shop_man_shop_sell_{item}'))
    keyboard.add(types.InlineKeyboardButton(f'Назад', callback_data=f'shop_man_shop_items_return'))
    return keyboard


def get_keyboard_drop_from_enemy(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    for item_i in range(len(saves[chat_id]['buffer']["drop_items"])):
        keyboard.add(types.InlineKeyboardButton(text=saves[chat_id]['buffer']["drop_items"][item_i],
                                                callback_data=f"drop_from_enemy_{item_i}"))
    keyboard.add(types.InlineKeyboardButton('Готово!', callback_data='fight_ready'))
    return keyboard


def get_spells_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='назад', callback_data=f"spell_{0}_return_to_fight"))
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


def show_quest(chat_id, quest):
    if (quest in saves[chat_id]['quests_time']) and (int(time()) - saves[chat_id]['quests_time'][quest] >= QUESTS[quest]['time']):
        del saves[chat_id]['quests_time'][quest]
    return ((QUESTS[quest]['need_lvl'] <= saves[chat_id]['lvl']) and (quest not in saves[chat_id]['quests']) and
            (quest not in saves[chat_id]['quests_time'])) or \
           ((QUESTS[quest]['need_lvl'] <= saves[chat_id]['lvl']) and (quest in saves[chat_id]['quests_time']) and
             (int(time()) - saves[chat_id]['quests_time'][quest] >= QUESTS[quest]['time'])) or quest in saves[chat_id]['quests']


def get_sewer_keyboard(call, show_quest_tf=True):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"sewer_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин скинов", callback_data=f"sewer_skins_shop"))
    if show_quest(call.from_user.id, 'Сбор паутины для швеи') and show_quest_tf:
        keyboard.add(types.InlineKeyboardButton(text="Помощь не требуется?", callback_data=f"sewer_quest_Сбор паутины для швеи"))
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



