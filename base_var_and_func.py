from sqlite3 import connect
from char import *
from threading import Thread, Lock
from random import sample
from time import sleep, time
from copy import deepcopy


lock = Lock()
print('base_var_and_func starting')


def check_quest_complete():
    while True:
        if len(saves.keys()) != 1:
            for chat_id in saves.keys():
                if chat_id not in saves.keys():
                    break
                quest_copy = saves[chat_id]['quests'].copy()
                for quest in quest_copy:
                    if quest in saves[chat_id]['quests'] and not saves[chat_id]['quests'][quest]:
                        tf = True
                        for item, val in QUESTS[quest]['need_items'].items():
                            if item in saves[chat_id]['inventory'] and saves[chat_id]['inventory'][item] >= int(val) and tf:
                                tf = True
                            elif tf:
                                tf = False
                                break
                        if tf:
                            saves[chat_id]['quests'][quest] = True


def from_db_dict_to_normal_dict(what, name, db_table_name):
    res = {}
    b = cur.execute(f"""Select {what} from {db_table_name} where name = '{name}'""").fetchone()[0]
    if b and len(b.split(';')) > 0 and b.split(';')[0] != '':
        for i in [x.split(':') for x in b.split(';')]:
            if i[1].isdigit():
                res[i[0]] = int(i[1])
            else:
                res[i[0]] = i[1]
    return res


def check_lvl_up(chat_id):
    if saves[chat_id]["xp"] >= saves[chat_id]["need_xp"]:
        level_up(chat_id)
        return True
    return False


def level_up(chat_id):
    saves[chat_id]["lvl"] += 1
    if saves[chat_id]["lvl"] % 5 == 0:
        saves[chat_id]["inventory_max_n"] += 1
    saves[chat_id]["need_xp"] = calc_xp_for_next_lvl(chat_id)
    update_char(chat_id)


def inventory_add_item(chat_id, item, n):
    if item in saves[chat_id]["inventory"]:
        saves[chat_id]["inventory"][item] += n
    else:
        saves[chat_id]["inventory"][item] = n


def inventory_del_item(chat_id, item, n):
    if saves[chat_id]["inventory"][item] - n > 0:
        saves[chat_id]["inventory"][item] -= n
    else:
        del saves[chat_id]["inventory"][item]


def update_char(chat_id):
    saves[chat_id]['need_xp'] = calc_xp_for_next_lvl(chat_id)
    saves[chat_id]["fight"]["hp"] = get_hp_from_stamina(saves[chat_id]["char"]["stamina"])
    saves[chat_id]["fight"]["max_hp"] = get_hp_from_stamina(saves[chat_id]["char"]["stamina"])
    saves[chat_id]["fight"]["mp"] = get_mp_from_intelligence(saves[chat_id]["char"]["intelligence"])
    saves[chat_id]["fight"]["max_mp"] = get_mp_from_intelligence(saves[chat_id]["char"]["intelligence"])
    saves[chat_id]["fight"]["mp_regen"] = get_mp_regen_from_intelligence(saves[chat_id]["char"]["intelligence"]) + \
                                          get_mp_regen_from_wisdom(saves[chat_id]["char"]["wisdom"])
    saves[chat_id]["fight"]["damage"] = get_damage_from_strength(saves[chat_id]["char"]["strength"])
    saves[chat_id]["fight"]["block_add"] = get_block_from_stamina(saves[chat_id]["char"]["stamina"])
    saves[chat_id]["fight"]["dodge"] = get_dodge_from_agility(saves[chat_id]["char"]["agility"])
    saves[chat_id]["fight"]["crit"] = get_crit_from_lucky(saves[chat_id]["char"]["lucky"])
    saves[chat_id]["fight"]["chance_of_loot"] = get_chance_of_loot_from_lucky(saves[chat_id]["char"]["lucky"])


def calc_xp_for_next_lvl(chat_id):
    return round((saves[chat_id]["lvl"] * 10) ** 1.5, 1)


def get_enemies_data_from_db():
    global ENEMIES
    try:
        lock.acquire(True)
        enemies_in_db = [x[0] for x in cur.execute(f"""Select name from enemies""").fetchall()]
        ENEMIES = get_data_db_not_users(db_table_name='enemies', template=ENEMIES['example'], res=ENEMIES, tables=['skin', 'des', 'xp', 'drop_gold', 'drop_gold_edit', 'lvl'], dict_tables=['char'])
        for enemy_name in enemies_in_db:
            items = cur.execute(f"""Select drop_item from enemies where name = '{enemy_name}'""").fetchone()[0].split(';')
            for i in [x.split(':') for x in items]:
                ENEMIES[enemy_name]['drop_items'][i[0]] = {}
                ENEMIES[enemy_name]['drop_items'][i[0]]['n'] = int(i[1])
                ENEMIES[enemy_name]['drop_items'][i[0]]['chance'] = int(i[2])
            ENEMIES['skins'].append(cur.execute(f"""Select skin from enemies where name = '{enemy_name}'""").fetchone()[0])
    finally:
        lock.release()


def get_saves_data_to_db(chat_id):
    inventory = ';'.join([f'{x}:{saves[chat_id]["inventory"][x]}' for x in saves[chat_id]['inventory'].keys()])
    pos = ';'.join([f'{x}:{saves[chat_id]["pos"][x]}' for x in saves[chat_id]['pos'].keys()])
    equip_items = ';'.join([f'{x}:{saves[chat_id]["equip_items"][x]}' for x in saves[chat_id]['equip_items'].keys()])
    fight_db = ';'.join([f'{x}:{saves[chat_id]["fight"][x]}' for x in saves[chat_id]['fight'].keys()])
    char = ';'.join([f'{x}:{saves[chat_id]["char"][x]}' for x in saves[chat_id]['char'].keys()])
    quests = ';'.join([f'{x}:{saves[chat_id]["quests"][x]}' for x in saves[chat_id]['quests'].keys()])
    quests_time = ';'.join([f'{x}:{saves[chat_id]["quests_time"][x]}' for x in saves[chat_id]['quests_time'].keys()])
    return pos, inventory, quests, quests_time, equip_items, fight_db, char, chat_id


def save_to_db(chat_id, name=''):
    if chat_id not in saves:
        saves[chat_id] = deepcopy(get_user_example())
        update_char(chat_id)
        saves[chat_id]['name'] = name
    pos, inventory, quests, quests_time, equip_items, fight_db, char, chat_id = get_saves_data_to_db(chat_id)
    if chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        cur.execute(f"""UPDATE users SET gold = ?,
                lvl = ?, pos = ?, inventory = ?, skin = ?, xp = ?, need_xp = ?, spells = ?, 
                quests = ?, quests_time=?, inventory_max_n = ?, equip_items = ?, fight = ?, char = ? WHERE chat_id = ?""",
                    (saves[chat_id]['gold'], saves[chat_id]['lvl'], pos, inventory, saves[chat_id]['skin'],
                saves[chat_id]['xp'], saves[chat_id]['need_xp'], ';'.join(saves[chat_id]['spells']),
                quests, quests_time, saves[chat_id]['inventory_max_n'], equip_items, fight_db, char, chat_id))
    else:
        q = f"""Insert into users Values({('?,'*16)[:-1]})"""
        cur.execute(q, (chat_id, saves[chat_id]['name'], saves[chat_id]['gold'], saves[chat_id]['lvl'], pos, inventory,
                        saves[chat_id]['skin'], saves[chat_id]['xp'], saves[chat_id]['need_xp'],
                        ';'.join(saves[chat_id]['spells']),
                    quests, quests_time, saves[chat_id]['inventory_max_n'], equip_items, fight_db, char))
    con.commit()


def get_data_from_db(chat_id, name=''):
    # try:
    #     lock.acquire(True)

    if chat_id not in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        save_to_db(chat_id, name)
    else:
        saves[chat_id] = deepcopy(get_user_example())
        # print(saves[chat_id])
        tables = ['name', 'gold', 'lvl', 'skin', 'xp', 'need_xp', 'inventory_max_n']
        dict_tables = ['pos', 'equip_items', 'fight', 'char']
        list_tables = ['spells']
        b = cur.execute(f"""Select inventory from users where chat_id = {chat_id}""").fetchone()[0]
        if b and len(b.split(';')) > 0 and b.split(';')[0].strip() != '':
            for i in [x.split(':') for x in b.split(';')]:
                saves[chat_id]['inventory'][i[0]] = int(i[1])
        b = cur.execute(f"""Select quests_time from users where chat_id = {chat_id}""").fetchone()[0]
        if b and len(b.split(';')) > 0 and b.split(';')[0].strip() != '':
            for i in [x.split(':') for x in b.split(';')]:
                saves[chat_id]['quests_time'][i[0]] = int(i[1])
        b = cur.execute(f"""Select quests from users where chat_id = {chat_id}""").fetchone()[0]
        if b and len(b.split(';')) > 0 and b.split(';')[0].strip() != '':
            for j in [x.split(':') for x in b.split(';')]:
                if j[1] == 'True':
                    saves[chat_id]['quests'][j[0]] = True
                elif j[1] == 'False':
                    saves[chat_id]['quests'][j[0]] = False
                else:
                    saves[chat_id]['quests'][j[0]] = j[1]
        for table in list_tables:
            b = cur.execute(f"""Select {table} from users where chat_id = {chat_id}""").fetchone()[0]
            if b and len(b.split(';')) > 0 and b.split(';')[0] != '':
                for i in b:
                    saves[chat_id][table].append(i)
        for table in tables:
            saves[chat_id][table] = cur.execute(f"""Select {table} from users where {chat_id}""").fetchone()[0]
        for table in dict_tables:
            b = cur.execute(f"""Select {table} from users where chat_id = {chat_id}""").fetchone()[0]
            if b and len(b.split(';')) > 0 and b.split(';')[0] != '':
                for i in [x.split(':') for x in b.split(';')]:
                    if i[1].isdigit():
                        saves[chat_id][table][i[0]] = int(i[1])
                    elif '.' in i[1]:
                        saves[chat_id][table][i[0]] = float(i[1])
                    else:
                        saves[chat_id][table][i[0]] = i[1]


def edit_message(bot, call, text, keyboard):
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text, reply_markup=keyboard)


def get_data_db_not_users(db_table_name, res={}, tables=[], dict_tables=[], list_tables=[], template=None, db_table_for_count='name'):
    count_in_db = [x[0] for x in cur.execute(f"""Select {db_table_for_count} from {db_table_name}""").fetchall()]
    for name in count_in_db:
        if template:
            res[name] = template.copy()
        for table in tables:
            res[name][table] = cur.execute(f"""Select {table} from {db_table_name} where {db_table_for_count} = '{name}'""").fetchone()[0]
        for dict_table in dict_tables:
            res[name][dict_table] = from_db_dict_to_normal_dict(dict_table, name, db_table_name)
        for table in list_tables:
            for i in cur.execute(f"""Select {table} from {db_table_name} where name = '{name}'""").fetchone()[0].split(';'):
                if i[1].isdigit():
                    res[name][table][i[0]] = int(i[1])
                else:
                    res[name][table][i[0]] = i[1]
    return res


def get_quests_from_db():
    global QUESTS
    QUESTS = get_data_db_not_users(db_table_name='quests', res={}, tables=['name', 'des', 'time', 'map', 'need_lvl',
                  'rewards_xp', 'who_accept', 'text_complete'], dict_tables=['add_items', 'rewards_items', 'need_items'], template=QUESTS_DB_TEMPLATE)


def get_spells_from_db():
    global SPELLS
    SPELLS = get_data_db_not_users(db_table_name='spells', res={}, tables=['name', 'des'], template=SPELLS_DB_TEMPLATE)


def get_users_shop_from_db():
    global USERS_SHOP
    USERS_SHOP = get_data_db_not_users(db_table_name='users_shop', res=USERS_SHOP, tables=['chat_id', 'cost', 'n'], template=USERS_SHOP['item'], db_table_for_count='item')


def get_shop_from_db():
    global SHOP
    SHOP = get_data_db_not_users(db_table_name='shop', template=SHOP['item'], res=SHOP,
                                 tables=['cost_sell', 'cost_buy', 'n'], db_table_for_count='item')


def check_auction_winners(res, db=False):
    for item in list(res.keys())[1:]:
        if res[item]['time_start'] + res[item]['time_continue'] <= time():
            winner = res[item]['who_up_last']
            if winner in saves:
                saves[winner]['inventory'][item] = res[item]['n']
                saves[winner]['gold'] += res[item]['cost']
            else:
                try:
                    lock.acquire(True)
                    inv = {}
                    b = cur.execute(f"""Select inventory from users where chat_id = {winner}""").fetchone()[0]
                    if b and len(b.split(';')) > 0 and b.split(';')[0].strip() != '':
                        for i in [x.split(':') for x in b.split(';')]:
                            inv[i[0]] = int(i[1])
                    inv[item] = res[item]['n']
                    inventory = ';'.join([f'{x}:{inv[x]}' for x in inv.keys()])
                    gold = cur.execute(f"""Select gold from users where chat_id = {winner}""").fetchone()[0] + res[item]['cost']
                    cur.execute(f"""UPDATE users SET inventory='{inventory}', gold={gold} WHERE chat_id = {winner}""")
                finally:
                    lock.release()
            if db:
                try:
                    lock.acquire(True)
                    cur.execute(f"""Delete from auction where item='{item}'""")
                finally:
                    lock.release()
            del res[item]
    return res


def get_auction_from_db():
    global AUCTION
    res = get_data_db_not_users(db_table_name='auction', template=AUCTION['item'], res=AUCTION,
                                tables=['cost', 'n', 'time_continue', 'time_start', 'who_up_last', 'item'], db_table_for_count='item')
    AUCTION = check_auction_winners(res, True)


def get_items_from_db():
    global ITEMS
    ITEMS = get_data_db_not_users(db_table_name='items', template=ITEMS_TEMPLATE, res=ITEMS,
                                  tables=['des', 'used'], db_table_for_count='name')


def update_data_from_db_constant():
    while True:
        get_quests_from_db()
        get_spells_from_db()
        get_shop_from_db()
        get_items_from_db()
        print('Quests, Spells, Shop, Items updated')
        check_auction_winners(AUCTION)
        print('check auctions winners finished')
        sleep(3600)


def get_user_example():
    USER_EXAMPLE = {'name': '', 'gold': 0, 'lvl': 1, 'pos': {'map': 'town_Bram', 'x': 5, 'y': 4}, 'inventory': {},
                    'skin': '😀',
                    'need_xp': 0, 'xp': 0, 'spells': [], 'quests': {}, 'quests_time': {}, 'inventory_max_n': 3,
                    'buffer': {'enemies': [], 'drop_items': [], 'inventory_page': 0, 'inventory_slice': 10,
                               'fight_text': {'text': '', 'keyboard': ''}, 'quest_keyboard_accept': None,
                               'quest_keyboard_decline': None,
                               'shop_page': 0, 'shop_page_slice': 20, 'arena_opponent_call': None},
                    'equip_items': {'head': '', 'body': '', 'pants': '', 'boots': '', 'backpack': ''},
                    'fight': {'damage': 0, 'block': 0, 'dodge': 0, 'chance_of_loot': 0, 'hp_regen': 0, 'mp_regen': 0,
                              'crit': 0, 'block_add': 0, 'hp': 0, 'mp': 0, 'max_hp': 0, 'max_mp': 0},
                    'char': {'strength': 1, 'agility': 1, 'lucky': 1, 'intelligence': 1, 'wisdom': 1, 'stamina': 1,
                             'free_char': 5}}
    # print(USER_EXAMPLE)
    return USER_EXAMPLE


con = connect("saves.db", check_same_thread=False, timeout=10)
cur = con.cursor()
CHARACTERISTICS = {'strength', 'agility', 'intelligence', 'lucky', 'wisdom', 'stamina'}
SKINS_SHOP = {'town_Bram': {'🤡': 100, '😒': 100, '😡': 100, '🤓': 100, '😀': 100, '😈': 100,
                            '💩': 100, '👻': 100, '👺': 100, '👹': 100, '👿': 100, '💀': 100}}
SPELLS_SHOP = {'town_Bram': {'Усиленный удар': 100}}
saves = {}
ENEMIES_ITEM_TEMPLATE = {'example': {'n': 0, 'chance': 0}}
ENEMIES = {'skins': [], 'example': {'char': {}, 'des': '', 'spells': {}, 'xp': 0, 'lvl': 0, 'skin': '', 'drop_items': {}, 'drop_gold': 0, 'drop_gold_edit': 0}}
print('enemies ', end='')
get_enemies_data_from_db()
print('loaded')
QUESTS_DB_TEMPLATE = {'name': '', 'des': '', 'time': 0, 'map': '', 'need_lvl': 0, 'add_items': {}, 'rewards_items': {},
                      'rewards_xp': 0, 'who_accept': '', 'text_complete': ''}
SPELLS_DB_TEMPLATE = {'des': ''}
QUESTS = {}
get_quests_from_db()
get_spells_from_db()
SPELLS = {}
USERS_SHOP = {'item': {'chat_id': 0, 'cost': 0, 'n': 0}}
SHOP = {'item': {'cost': 0, 'n': 0, 'max_n': 0}}
AUCTION = {'item': {'chat_id': 0, 'cost': 0, 'who_up_last': 0, 'time': 0, 'n': 0}}
get_users_shop_from_db()
get_shop_from_db()
get_auction_from_db()
print('users_shop, auction, shop loaded')
ITEMS_TEMPLATE = {'des': '', 'used': 0}
ITEMS = {}
get_items_from_db()
# print(f'USERS_SHOP {USERS_SHOP}\n\nSHOP {SHOP}\n\nAUCTION {AUCTION}')
arena_queue = {}
try:
    lock.acquire(True)
    chat_ids = [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]
finally:
    lock.release()
if chat_ids:
    for i in chat_ids:
        get_data_from_db(i)
print('all users is connected')
print('base_var_and_func started')
