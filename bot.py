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
CHARACTERISTICS = {'strength', 'agility', 'intelligence', 'lucky', 'wisdom', 'stamina'}
token = environ['dev_token']
bot = telebot.TeleBot(token)
print('start')


@bot.callback_query_handler(func=lambda call: 'sewer_skins_shop_yes' in call.data or 'sewer_skins_shop_no' in call.data)
def yes_or_no_skins(call):
    dialogs.yes_or_no_skins(call, bot)


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


@bot.callback_query_handler(func=lambda call: 'fight' in call.data.split('_')[0])
def fight(call):
    fight_checker(call, bot)


@bot.callback_query_handler(func=lambda call: 'mode' in call.data.split('_')[0])
def choice_mode(call):
    if call.data == 'mode_single':
        get_data_from_db(call.from_user.id, name=call.from_user.username)
        clear_fight_logs(call.from_user.id)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=load_map(call.from_user.id),
                              reply_markup=get_move_keyboard())


@bot.callback_query_handler(func=lambda call: 'librarian' in call.data.split('_')[0])
def librarian(call):
    dialogs.librarian(call, bot)


@bot.callback_query_handler(func=lambda call: 'sewer' in call.data.split('_')[0])
def sewer(call):
    dialogs.sewer(call, bot)


@bot.callback_query_handler(func=lambda call: 'inventory' in call.data.split('_')[0])
def inventory(call):
    if call.data == 'inventory_return':
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
        elif this_map == 'town_Bram_sewing':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 4
        elif this_map == 'town_Bram_library':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 6
            elif cell == '👩🏼‍🏫':
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text='Хм?', reply_markup=get_librarian_keyboard())
                return True
        elif this_map == 'level1':
            if cell == '🚪':
                new_map = 'town_Bram'
                y = 2
                x = 5
        saves[call.from_user.id]['pos']['y'] = y
        saves[call.from_user.id]['pos']['x'] = x
        saves[call.from_user.id]['pos']['map'] = new_map
        if cell == '🚪':
            save_to_db(call.from_user.id)
    return False


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Выберите режим игры', reply_markup=choice_mode_keyboard)
    elif message.text == '/help':
        bot.send_message(message.chat.id, 'Помощь? Я мало с чем могу помочь. Ты в башне, она разделена на множество этажей, в каждый этаж универсален. Вокруг башни мы построили город, в нем есть много всего. Возвращаться каждый в город не удобно, так что мы смогли некоторые этажи превратить в мини-города. Вроде как все! Ах да, после 5 этажа, башня каждый раз генерируется случайной, так что надейся на удачу.', reply_markup=choice_mode_keyboard)


chat_ids = [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]
if chat_ids:
    for i in chat_ids:
        get_data_from_db(i)


# try:
bot.polling(none_stop=True, interval=0)
# except Exception as e:
#     print(f'bot.polling {e}')
