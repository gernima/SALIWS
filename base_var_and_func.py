from sqlite3 import connect
from char import *


def from_db_dict_to_normal_dict(what, name):
    inv = {}
    b = cur.execute(f"""Select {what} from enemies where name = '{name}'""").fetchone()[0].split(';')
    if len(b) > 0 and b[0] != '':
        for i in [x.split(':') for x in b]:
            inv[i[0]] = int(i[1])
    return inv


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
    enemies_in_db = [x[0] for x in cur.execute(f"""Select name from enemies""").fetchall()]
    for enemy_name in enemies_in_db:
        ENEMIES[enemy_name] = ENEMIES['example']
        tables = ['name', 'skin', 'des', 'xp', 'drop_gold', 'drop_gold_edit', 'lvl']
        dict_tables = ['char']
        items = cur.execute(f"""Select drop_item from enemies where name = '{enemy_name}'""").fetchone()[0].split(';')
        for i in [x.split(':') for x in items]:
            ENEMIES[enemy_name]['drop_items'][i[0]] = {}
            ENEMIES[enemy_name]['drop_items'][i[0]]['n'] = int(i[1])
            ENEMIES[enemy_name]['drop_items'][i[0]]['chance'] = int(i[2])
        ENEMIES['skins'].append(cur.execute(f"""Select skin from enemies where name = '{enemy_name}'""").fetchone()[0])
        for table in tables:
            ENEMIES[enemy_name][table] = cur.execute(f"""Select {table} from enemies where name = '{enemy_name}'""").fetchone()[0]
        for dict_table in dict_tables:
            ENEMIES[enemy_name][dict_table] = from_db_dict_to_normal_dict(dict_table, enemy_name)


def save_to_db(chat_id, name=''):
    if chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        inventory = ';'.join([f'{x}:{saves[chat_id]["inventory"][x]}' for x in saves[chat_id]['inventory'].keys()])
        pos = ';'.join([f'{x}:{saves[chat_id]["pos"][x]}' for x in saves[chat_id]['pos'].keys()])
        equip_items = ';'.join(
            [f'{x}:{saves[chat_id]["equip_items"][x]}' for x in saves[chat_id]['equip_items'].keys()])
        fight_db = ';'.join([f'{x}:{saves[chat_id]["fight"][x]}' for x in saves[chat_id]['fight'].keys()])
        char = ';'.join([f'{x}:{saves[chat_id]["char"][x]}' for x in saves[chat_id]['char'].keys()])
        cur.execute(f"""UPDATE users SET gold = ?,
                lvl = ?, pos = ?, inventory = ?, skin = ?, xp = ?, need_xp = ?, spells = ?, 
                quests = ?, inventory_max_n = ?, equip_items = ?, fight = ?, 
                char = ? WHERE chat_id = ?""", (saves[chat_id]['gold'], saves[chat_id]['lvl'], pos,
                    inventory, saves[chat_id]['skin'],
                saves[chat_id]['xp'], saves[chat_id]['need_xp'], ';'.join(saves[chat_id]['spells']),
                ';'.join(saves[chat_id]['quests']), saves[chat_id]['inventory_max_n'], equip_items, fight_db, char, chat_id))
    else:
        saves[chat_id] = saves['example']
        update_char(chat_id)
        saves[chat_id]['name'] = name
        inventory = ';'.join([f'{x}:{saves[chat_id]["inventory"][x]}' for x in saves[chat_id]['inventory'].keys()])
        pos = ';'.join([f'{x}:{saves[chat_id]["pos"][x]}' for x in saves[chat_id]['pos'].keys()])
        equip_items = ';'.join(
            [f'{x}:{saves[chat_id]["equip_items"][x]}' for x in saves[chat_id]['equip_items'].keys()])
        fight_db = ';'.join([f'{x}:{saves[chat_id]["fight"][x]}' for x in saves[chat_id]['fight'].keys()])
        char = ';'.join([f'{x}:{saves[chat_id]["char"][x]}' for x in saves[chat_id]['char'].keys()])
        q = f"""Insert into users Values({('?,'*15)[:-1]})"""
        cur.execute(q, (chat_id, saves[chat_id]['name'], saves[chat_id]['gold'],
                    saves[chat_id]['lvl'], pos, inventory, saves[chat_id]['skin'],
                    saves[chat_id]['xp'], saves[chat_id]['need_xp'], ';'.join(saves[chat_id]['spells']),
                    ';'.join(saves[chat_id]['quests']), saves[chat_id]['inventory_max_n'], equip_items, fight_db, char))
    con.commit()


def get_data_from_db(chat_id, name=''):
    saves[chat_id] = saves['example']
    if chat_id not in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        save_to_db(chat_id, name)
    else:
        tables = ['name', 'gold', 'lvl', 'skin', 'xp', 'need_xp', 'spells', 'quests', 'inventory_max_n']
        dict_tables = ['pos', 'inventory', 'equip_items', 'fight', 'char']
        for table in tables:
            saves[chat_id][table] = cur.execute(f"""Select {table} from users where {chat_id}""").fetchone()[0]
        for table in dict_tables:
            z = {}
            b = cur.execute(f"""Select {table} from users where chat_id = {chat_id}""").fetchone()[0].split(';')
            if len(b) > 0 and b[0] != '':
                for i in [x.split(':') for x in b]:
                    if i[1].isdigit():
                        z[i[0]] = int(i[1])
                    else:
                        z[i[0]] = i[1]
                saves[chat_id][table] = z
        con.commit()


con = connect("saves.db", check_same_thread=False)
cur = con.cursor()
saves = {'example': {'name': '', 'gold': 0, 'lvl': 1, 'pos': {'map': 'town_Bram', 'x': 5, 'y': 4}, 'inventory': {}, 'skin': '😀',
                     'need_xp': 0, 'xp': 0, 'spells': [], 'quests': [], 'inventory_max_n': 3,
                     'buffer': {'enemies': [], 'drop_items': [], 'inventory_page': 0, 'inventory_slice': 20, 'fight_text': {'text': '', 'keyboard': ''}},
                     'equip_items': {'head': '', 'body': '', 'pants': '', 'boots': ''},
                     'fight': {'damage': 0, 'block': 0, 'dodge': 0, 'chance_of_loot': 0, 'hp_regen': 0, 'mp_regen': 0,
                               'crit': 0, 'block_add': 0, 'hp': 0, 'mp': 0, 'max_hp': 0, 'max_mp': 0},
                     'char': {'strength': 1, 'agility': 1, 'lucky': 1, 'intelligence': 1, 'wisdom': 1, 'stamina': 1, 'free_char': 5}}}
ENEMIES_ITEM_TEMPLATE = {'example': {'n': 0, 'chance': 0}}
ENEMIES = {'skins': [], 'example': {'char': {}, 'des': '', 'spells': {}, 'xp': 0, 'lvl': 0, 'skin': '', 'drop_items': {}, 'drop_gold': 0, 'drop_gold_edit': 0}}
get_enemies_data_from_db()