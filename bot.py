import telebot
from dotenv import load_dotenv
from os import environ
from char import *
# from keyboards import *
from fight import *
from pickle import load
from enemies import *
import dialogs
from base_var_and_func import *


load_dotenv()
# if str(input('1 is main, another dev: ')) == '1':
#     token = environ['main_token']
# else:
token = environ['dev_token']
bot = telebot.TeleBot(token)


def check_arena_queue():
    while True:
        if len(arena_queue) >= 2:
            opponents = sample(arena_queue, 2)
            arena_queue.remove(opponents[0])
            arena_queue.remove(opponents[1])
            if randint(0, 1) == 0:
                who_first = opponents[0]
            else:
                who_first = opponents[1]
            edit_message(bot, opponents[0], f'Начат бой против {saves[opponents[0]]["name"]}', get_arena_fight_keyboard(opponents[0], who_first))
            edit_message(bot, opponents[1], f'Начат бой против {saves[opponents[1]]["name"]}', get_arena_fight_keyboard(opponents[1], who_first))
            print(f'arena_fight {opponents[0]} {saves[opponents[0]]["name"]} vs {opponents[1]} {saves[opponents[1]]["name"]}')


@bot.callback_query_handler(func=lambda call: 'fight' in call.data.split('_')[0])
def fight(call):
    fight_checker(call, bot)


@bot.callback_query_handler(func=lambda call: 'quest_' in call.data and '_quest_' not in call.data)
def quest_yes_or_no(call):
    dialogs.yes_or_no_quest(call, bot)


@bot.callback_query_handler(func=lambda call: 'sewer_skins_shop_yes' in call.data or 'sewer_skins_shop_no' in call.data)
def yes_or_no_skins(call):
    if 'town_Bram' in saves[call.from_user.id]['pos']['map']:
        dialogs.yes_or_no_skins(call, bot)


@bot.callback_query_handler(func=lambda call: 'librarian' in call.data.split('_')[0])
def librarian(call):
    if 'town_Bram' in saves[call.from_user.id]['pos']['map']:
        dialogs.librarian(call, bot)


@bot.callback_query_handler(func=lambda call: 'sewer' in call.data.split('_')[0])
def sewer(call):
    if 'town_Bram' in saves[call.from_user.id]['pos']['map']:
        dialogs.sewer(call, bot)


@bot.callback_query_handler(func=lambda call: 'arena' in call.data.split('_')[0])
def arena_man(call):
    if 'town_Bram' in saves[call.from_user.id]['pos']['map']:
        dialogs.arena(call, bot)


@bot.callback_query_handler(func=lambda call: 'char_' in call.data)
def char_update(call):
    if call.data.split('_')[1] in CHARACTERISTICS:
        if saves[call.from_user.id]['char']['free_char'] > 0:
            if call.data.split('_')[1] == 'strength':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко силы')
                saves[call.from_user.id]['char']['strength'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            elif call.data.split('_')[1] == 'agility':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко ловкости')
                saves[call.from_user.id]['char']['agility'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            elif call.data.split('_')[1] == 'intelligence':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко интеллекта')
                saves[call.from_user.id]['char']['intelligence'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            elif call.data.split('_')[1] == 'lucky':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко удачи')
                saves[call.from_user.id]['char']['lucky'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            elif call.data.split('_')[1] == 'wisdom':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко мудрости')
                saves[call.from_user.id]['char']['wisdom'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            elif call.data.split('_')[1] == 'stamina':
                bot.answer_callback_query(callback_query_id=call.id, text='+1 очко выносливости')
                saves[call.from_user.id]['char']['stamina'] += 1
                saves[call.from_user.id]['char']['free_char'] -= 1
            update_char(call.from_user.id)
            send_hero_char(call, bot)
        else:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text='У вас нет очков характеристик, повысьте ваш уровень')
    elif call.data == 'char_return':
        send_map(call, bot)
        save_to_db(call.from_user.id)


@bot.callback_query_handler(func=lambda call: 'drop_from_enemy_' in call.data)
def drop_from_enemy(call):
    drop_from_enemy_checker(call, bot)


@bot.callback_query_handler(func=lambda call: 'spell' in call.data.split('_')[0])
def spell(call):
    fight_spells_checker(call, bot)


@bot.callback_query_handler(func=lambda call: 'mode' in call.data.split('_')[0])
def choice_mode(call):
    if call.data == 'mode_single':
        load_mode(call)


def load_mode(call, is_call=True):
    if is_call:
        get_data_from_db(call.from_user.id, name=call.from_user.username)
        clear_fight_logs(call.from_user.id)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=load_map(call.from_user.id),
                              reply_markup=get_move_keyboard())
    else:
        get_data_from_db(call.chat.id, name=call.from_user.username)
        clear_fight_logs(call.chat.id)
        bot.send_message(chat_id=call.chat.id, text=load_map(call.chat.id), reply_markup=get_move_keyboard())


@bot.callback_query_handler(func=lambda call: 'inventory' in call.data.split('_')[0])
def inventory(call):
    if 'return' in call.data:
        if len(saves[call.from_user.id]['buffer']['enemies']) != 0:
            send_fight_text(call, bot)
        else:
            send_map(call, bot)
    elif 'page' in call.data:
        if call.data == 'inventory_next_page':
            if len(saves[call.from_user.id]['inventory']) > (saves[call.from_user.id]['buffer']['inventory_page'] + 1) * saves[call.from_user.id]['buffer']['inventory_slice']:
                saves[call.from_user.id]['buffer']['inventory_page'] += 1
        elif call.data == 'inventory_prev_page':
            if saves[call.from_user.id]['buffer']['inventory_page'] - 1 >= 0:
                saves[call.from_user.id]['buffer']['inventory_page'] -= 1
        send_inventory(call, bot)
    elif 'item' in call.data:
        item = call.data.split('_')[2]
        info = cur.execute("""Select des, used from items where name = ?""", (item, )).fetchall()
        des, used = info[0][0], info[0][1]
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Название: {item}\n\nОписание:{des}',
                              reply_markup=get_inventory_item_keyboard(call, used))


@bot.callback_query_handler(func=lambda call: 'move' in call.data.split('_')[0])
def move(call):
    if 'up' in call.data or 'down' in call.data or 'left' in call.data or 'right' in call.data:
        y = saves[call.from_user.id]['pos']['y']
        x = saves[call.from_user.id]['pos']['x']
        prev_map_str = load_map(call.from_user.id)
        if 'up' in call.data:
            y -= 1
        elif 'down' in call.data:
            y += 1
        elif 'left' in call.data:
            x -= 1
        elif 'right' in call.data:
            x += 1
        if not check_cell(call, x, y):
            if prev_map_str != load_map(call.from_user.id):
                send_map(call, bot)
    elif call.data == 'move_chars':
        send_hero_char(call, bot)
    elif call.data == 'move_inventory':
        send_inventory(call, bot)


def check_cell(call, x, y):
    this_map = saves[call.from_user.id]['pos']['map']
    new_map = saves[call.from_user.id]['pos']['map']
    cell = get_map_list(call.from_user.id)[y][x]
    if cell[0] in ENEMIES['skins']:
        if cell[0] == '🕷':
            text = 'Начат бой против: '
            saves[call.from_user.id]['buffer']['enemies'].append(
                Spider(name='Обычный Паук', enhancement_n=0, x=x, y=y, bot=bot))
            for i in saves[call.from_user.id]['buffer']['enemies']:
                text += f'{i.name} {i.hp}♥ {i.mp}💙 '
            saves[call.from_user.id]['buffer']['fight_text']['text'] += text
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=get_fight_keyboard())
        return True
    else:
        if this_map == 'town_Bram':
            if cell == '🚪':
                new_map = 'level1'
                y = 1
                x = 1
            elif cell == '🧵':
                new_map = 'town_Bram_sewing'
                y = 1
                x = 5
            elif cell == '📚':
                new_map = 'town_Bram_library'
                y = 9
                x = 5
            elif cell == '⚔':
                new_map = 'town_Bram_arena'
                y = 1
                x = 5
        elif this_map == 'town_Bram_arena':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 4
                x = 5
            elif cell == '🧔':
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text='Новая кровь, чего ждешь?', reply_markup=get_arena_man_keyboard())
                save_to_db(call.from_user.id)
                return True
        elif this_map == 'town_Bram_sewing':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 4
            elif cell == '👰🏼':
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text='Да?', reply_markup=get_sewer_keyboard(call))
                save_to_db(call.from_user.id)
                return True
        elif this_map == 'town_Bram_library':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 6
            elif cell == '👩🏼‍🏫':
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text='Хм?', reply_markup=get_librarian_keyboard())
                save_to_db(call.from_user.id)
                return True
        elif this_map == 'level1':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 5
        saves[call.from_user.id]['pos']['y'] = y
        saves[call.from_user.id]['pos']['x'] = x
        if saves[call.from_user.id]['pos']['map'] != new_map:
            save_to_db(call.from_user.id)
        saves[call.from_user.id]['pos']['map'] = new_map
    return False


@bot.message_handler(commands=['start', 'help', 'restart'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Выберите режим игры', reply_markup=choice_mode_keyboard)
    elif message.text == '/help':
        bot.send_message(message.chat.id, 'Помощь? Я мало с чем могу помочь. Ты в башне, она разделена на множество этажей, в каждый этаж универсален. Вокруг башни мы построили город, в нем есть много всего. Возвращаться каждый в город не удобно, так что мы смогли некоторые этажи превратить в мини-города. Вроде как все! Ах да, после 5 этажа, башня каждый раз генерируется случайной, так что надейся на удачу.', reply_markup=choice_mode_keyboard)
    elif message.text == '/restart':
        cur.execute(f"""Delete from auction where chat_id={message.chat.id}""")
        cur.execute(f"""Delete from promocodes where chat_id={message.chat.id}""")
        cur.execute(f"""Delete from users_shop where chat_id={message.chat.id}""")
        cur.execute(f"""Delete from users where chat_id={message.chat.id}""")
        del saves[message.chat.id]
        load_mode(message, is_call=False)


# thread_arena_queue = Thread(target=check_arena_queue(), args=(bot))
# thread_arena_queue.start()
thread_check_quest = Thread(target=check_quest_complete)
thread_check_quest.start()
print('thread_check_quest started')
thread_update_data_from_db = Thread(target=update_data_from_db_constant)
thread_update_data_from_db.start()
print('thread_update_data started')
thread_check_arena_fight_queue = Thread(target=check_arena_queue)
thread_check_arena_fight_queue.start()
print('thread_check_arena_fight_queue started')
print('bot start')
# try:
bot.polling()
# except Exception as e:
#     print(f'bot.polling {e}')
