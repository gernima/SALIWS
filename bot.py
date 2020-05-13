import telebot
import sqlite3
from dotenv import load_dotenv
from os import environ
import sqlite3
from char import *
from keyboards import *
from pickle import load
import dialogs


load_dotenv()
# if str(input('1 is main, another dev: ')) == '1':
#     token = environ['main_token']
# else:
token = environ['dev_token']
bot = telebot.TeleBot(token)
print('start')
con = sqlite3.connect("saves.db", check_same_thread=False)
cur = con.cursor()
saves = {'example': {'name': '', 'gold': 0, 'lvl': 1, 'pos': {'map': 'town', 'x': 5, 'y': 4}, 'inventory': {}, 'skin': '😀',
                     'need_xp': 0, 'xp': 0, 'spells': [], 'quests': [], 'inventory_max_n': 0, 'hp': 0, 'mp': 0,
                     'equip_items': {'head': '', 'body': '', 'pants': '', 'boots': ''},
                     'fight': {'damage': 0, 'block': 0, 'dodge': 0, 'chance_of_loot': 0, 'hp_regen': 0, 'mp_regen': 0, 'crit': 0},
                     'char': {'strength': 1, 'agility': 1, 'lucky': 1, 'intelligence': 1, 'wisdom': 1, 'stamina': 1, 'free_char': 5}
                     }
         }


@bot.callback_query_handler(func=lambda call: 'mode' in call.data.split('_')[0])
def choice_mode(call):
    if call.data == 'mode_single':
        get_data_from_db(call.from_user.id, name=call.from_user.username)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=load_map(call.from_user.id),
                              reply_markup=get_move_keyboard())


@bot.callback_query_handler(func=lambda call: 'move' in call.data.split('_')[0])
def move(call):
    if 'up' in call.data or 'down' in call.data or 'left' in call.data or 'right' in call.data:
        if 'up' in call.data:
            if saves[call.from_user.id]['pos']['y'] - 1 == '🌫':
                saves[call.from_user.id]['pos']['y'] -= 1
        elif 'down' in call.data:
            if saves[call.from_user.id]['pos']['y'] + 1 == '🌫':
                saves[call.from_user.id]['pos']['y'] += 1
        elif 'left' in call.data:
            if saves[call.from_user.id]['pos']['x'] - 1 == '🌫':
                saves[call.from_user.id]['pos']['x'] -= 1
        elif 'right' in call.data:
            if saves[call.from_user.id]['pos']['x'] + 1 == '🌫':
                saves[call.from_user.id]['pos']['x'] += 1
        check_teleportation(get_map_list(call.from_user.id)[saves[call.from_user.id]['pos']['y']][saves[call.from_user.id]['pos']['x']], call)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=load_map(call.from_user.id),
                              reply_markup=get_move_keyboard())


def check_teleportation(cell, call):
    this_map = saves[call.from_user.id]['pos']['map']
    if this_map == 'town':
        if cell == '🚪':
            new_map = 'level1'
        elif cell == '🧵':
            new_map = 'sewer_town'
        elif cell == '📚':
            new_map = 'library_town'
        elif cell == '⚔':
            new_map = 'arena_town'
    elif this_map == 'arena_town':
        if cell == '🚪':
            new_map = 'town'
    elif this_map == 'sewing_town':
        if cell == '🚪':
            new_map = 'town'
    elif this_map == 'library_town':
        if cell == '🚪':
            new_map = 'town'
        elif cell == '👩🏼‍🏫':
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='Хм?', reply_markup=get_librarian_keyboard())
    try:
        saves[call.from_user.id]['pos']['map'] = new_map
    except:
        pass


def get_map_list(chat_id):
    with open(f'levels/{saves[chat_id]["pos"]["map"]}.txt', 'rb') as f:
        map_list = load(f)
        map_list[saves[chat_id]["pos"]['y']][saves[chat_id]["pos"]['x']] = saves[chat_id]["skin"]
        return map_list


def load_map(chat_id):
    return '\n'.join(''.join(x) for x in get_map_list(chat_id))


def save_to_db(chat_id, name=''):
    if chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        inventory = ';'.join([f'{x}:{saves[chat_id]["inventory"][x]}' for x in saves[chat_id]['inventory'].keys()])
        pos = ';'.join([f'{x}:{saves[chat_id]["pos"][x]}' for x in saves[chat_id]['pos'].keys()])
        equip_items = ';'.join(
            [f'{x}:{saves[chat_id]["equip_items"][x]}' for x in saves[chat_id]['equip_items'].keys()])
        fight = ';'.join([f'{x}:{saves[chat_id]["fight"][x]}' for x in saves[chat_id]['fight'].keys()])
        char = ';'.join([f'{x}:{saves[chat_id]["char"][x]}' for x in saves[chat_id]['char'].keys()])
        q = f"""UPDATE users SET chat_id = {chat_id}, name = {saves[chat_id]['name']}, gold = {saves[chat_id]['gold']}, 
                lvl = {saves[chat_id]['lvl']}, pos = {pos}, inventory = {inventory}, skin = {saves[chat_id]['skin']}, 
                xp = {saves[chat_id]['xp']}, need_xp = {saves[chat_id]['need_xp']}, spells = {';'.join(saves[chat_id]['spells'])}, 
                quests = {';'.join(saves[chat_id]['quests'])}, inventory_max_n = {saves[chat_id]['inventoru_max_n']}, 
                hp = {saves[chat_id]['hp']}, mp = {saves[chat_id]['mp']}, equip_items = {equip_items}, fight = {fight}, 
                char = {char} WHERE chat_id = {chat_id}"""
        cur.execute(q)
    else:
        saves[chat_id] = saves['example']
        saves[chat_id]['name'] = name
        inventory = ';'.join([f'{x}:{saves[chat_id]["inventory"][x]}' for x in saves[chat_id]['inventory'].keys()])
        pos = ';'.join([f'{x}:{saves[chat_id]["pos"][x]}' for x in saves[chat_id]['pos'].keys()])
        equip_items = ';'.join(
            [f'{x}:{saves[chat_id]["equip_items"][x]}' for x in saves[chat_id]['equip_items'].keys()])
        fight = ';'.join([f'{x}:{saves[chat_id]["fight"][x]}' for x in saves[chat_id]['fight'].keys()])
        char = ';'.join([f'{x}:{saves[chat_id]["char"][x]}' for x in saves[chat_id]['char'].keys()])
        q = f"""Insert into users Values({('?,'*17)[:-1]})"""
        cur.execute(q, (chat_id, saves[chat_id]['name'], saves[chat_id]['gold'],
                    saves[chat_id]['lvl'], pos, inventory, saves[chat_id]['skin'],
                    saves[chat_id]['xp'], saves[chat_id]['need_xp'], ';'.join(saves[chat_id]['spells']),
                    ';'.join(saves[chat_id]['quests']), saves[chat_id]['inventory_max_n'],
                    saves[chat_id]['hp'], saves[chat_id]['mp'], equip_items, fight, char))
    con.commit()


def get_data_from_db(chat_id, name=''):
    saves[chat_id] = saves['example']
    if chat_id not in [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]:
        save_to_db(chat_id, name)
    else:
        tables = ['name', 'gold', 'lvl', 'skin', 'xp', 'need_xp', 'spells', 'quests', 'inventory_max_n', 'hp', 'mp']
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


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Выберите режим игры', reply_markup=choice_mode_keyboard)
    elif message.text == '/help':
        bot.send_message(message.chat.id, 'Помощь? Я мало с чем могу помочь. Ты в башне, она разделена на множество этажей, в каждый этаж универсален. Вокруг башни мы построили город, в нем есть много всего. Возвращаться каждый в город не удобно, так что мы смогли некоторые этажи превратить в мини-города. Вроде как все! Ах да, после 5 этажа, башня каждый раз генерируется случайной, так что надейся на удачу.', reply_markup=choice_mode_keyboard)


try:
    bot.polling(none_stop=True, interval=0)
except Exception as e:
    print(f'bot.polling {e}')
