import telebot
from keyboards import *
from random import randint
from base_var_and_func import *


def is_died(chat_id):
    if saves[chat_id]['fight']['hp'] <= 0:
        return True
    return False


def add_xp(chat_id, xp):
    saves[chat_id]['xp'] += xp


def check_enemy_died_and_killed_logic(call, enemy, bot):
    text = ''
    chat_id = call.from_user.id
    if enemy.you_died_tf():
        saves[chat_id]['buffer']['enemies'].remove(enemy)
        bonus_tf = False
        if enemy.lvl > saves[chat_id]['lvl']:
            percent = abs(enemy.lvl - saves[chat_id]['lvl']) * 0.1
            xp = round(percent * enemy.xp + enemy.xp, 1)
            text += f"Вы убили {enemy.skin} превосходящее вас по уровню за это вы получаете на {percent * 100}% больше опыта"
            bonus_tf = True
        elif enemy.lvl == saves[chat_id]['lvl']:
            xp = enemy.xp
        else:
            xp = round((1 - abs(saves[chat_id]['lvl'] - enemy.lvl) * 0.1) * enemy.xp, 1)
        add_xp(chat_id, xp)
        if check_lvl_up(chat_id):
            level_up(chat_id)
            saves[chat_id]["char"]["free_char"] += 10
            if bonus_tf:
                text += f'Вы получаете {xp} ед.опыта\nВы повысили уровень, за это вы получаете 10 очков характеристик, ваш уровень {saves[chat_id]["lvl"]}\nДо следующего уровня осталось {round(saves[chat_id]["need_xp"] - saves[chat_id]["xp"], 1)} ед.опыта'
            else:
                text += f'Вы убили {enemy.skin}, вы получаете {xp} ед.опыта\nВы повысили уровень, за это вы получаете 10 очков характеристик, ваш уровень {saves[chat_id]["lvl"]}\nДо следующего уровня осталось {round(saves[chat_id]["need_xp"] - saves[chat_id]["xp"], 1)} ед.опыта'
        else:
            text += f'Вы убили {enemy.skin}, вы получаете {xp} ед.опыта\nДо следующего уровня осталось {round(saves[chat_id]["need_xp"] - saves[chat_id]["xp"], 1)} ед.опыта'
        saves[chat_id]['buffer']['fight_text']['text'] = text + '\n'
        drop_from_enemy(call, enemy, bot)
        return True
    return False


def drop_from_enemy(call, enemy, bot):
    text = ''
    chat_id = call.from_user.id
    saves[chat_id]['buffer']["drop_items"] = []
    gold_edit = randint(-1 * ENEMIES[enemy.name]['drop_gold_edit'], ENEMIES[enemy.name]['drop_gold_edit'])
    gold_drop = ENEMIES[enemy.name]['drop_gold'] + gold_edit
    saves[chat_id]["gold"] += gold_drop
    text += f"Выпало {gold_drop} золота\nВаш баланс: {saves[chat_id]['gold']}"
    for item in ENEMIES[enemy.name]['drop_items'].keys():
        chance = randint(1, 100)
        if chance <= ENEMIES[enemy.name]['drop_items'][item]['chance']:
            for _ in range(ENEMIES[enemy.name]['drop_items'][item]['n']):
                saves[chat_id]['buffer']["drop_items"].append(item)
    if len(saves[chat_id]['buffer']["drop_items"]) != 0:
        text += '\n' + f"Выберите предметы:"
    saves[chat_id]['buffer']['fight_text']['text'] += text


def drop_from_enemy_checker(call, bot):
    chat_id = call.from_user.id
    print(call.data, saves[chat_id]['buffer']['drop_items'])
    if saves[chat_id]['buffer']['drop_items']:
        if len(saves[chat_id]['inventory'].keys()) != saves[chat_id]['inventory_max_n']:
            text = call.data[16:]
            item = saves[chat_id]['buffer']['drop_items'].pop(int(text))
            inventory_add_item(chat_id, item, 1)
            saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы подобрали {item}'
            send_fight_text(call, bot)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text=f'Ваш инвентарь полон')
    else:
        send_map(call, bot)


def mp_regen(chat_id):
    if saves[chat_id]['fight']["mp"] < saves[chat_id]['fight']['max_mp']:
        if saves[chat_id]['fight']["mp"] + saves[chat_id]["fight"]["mp_regen"] < saves[chat_id]['fight']['max_mp']:
            saves[chat_id]['fight']["mp"] += saves[chat_id]["fight"]["mp_regen"]
        else:
            saves[chat_id]['fight']["mp"] = saves[chat_id]['fight']['max_mp']


def death(chat_id, bot):
    max_hp = get_hp_from_stamina(saves[chat_id]["char"]["stamina"])
    saves[chat_id]['fight']['hp'] = max_hp
    max_mp = get_mp_from_intelligence(saves[chat_id]["char"]["intelligence"])
    saves[chat_id]['mp'] = max_mp
    minus_xp = 0.1 * saves[chat_id]['xp']
    if saves[chat_id]['xp'] - minus_xp >= 0:
        saves[chat_id]['xp'] -= minus_xp
    else:
        saves[chat_id]['xp'] = 0
    saves[chat_id]['pos']['map'] = 'town_Bram'
    saves[chat_id]['pos']['x'] = 5
    saves[chat_id]['pos']['y'] = 2
    saves[chat_id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
    saves[chat_id]['buffer']['fight_text']['text'] = ''
    saves[chat_id]['fight']['enemies'] = []


def check_death(chat_id, bot):
    if is_died(chat_id):
        death(chat_id, bot)


def fight_spells_checker(call, bot):
    chat_id = call.from_user.id
    if len(saves[chat_id]['buffer']['enemies']) != 0:
        data = call.data
        enemy = saves[chat_id]['buffer']['enemies'][int(data.split('_')[1])]
        if 'return_to_fight' in data:
            if 'arena' in data:
                pass
            else:
                saves[chat_id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
                send_fight_text(call, bot)
        elif 'усиленный удар' in data:
            if 'arena' in data:
                pass
            else:
                saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы использовали {data}'
                attack(call, enemy, saves[chat_id]["fight"]["damage"] * 1.1, bot)
    else:
        send_fight_text(call, bot)


def damaging(damage, chat_id):
    if saves[chat_id]['fight']['block'] > 0:
        saves[chat_id]['fight']['hp'] = round(saves[chat_id]['fight']['hp'] - damage + saves[chat_id]['fight']['block'], 1)
    else:
        saves[chat_id]['fight']['hp'] = round(saves[chat_id]['fight']['hp'] - damage, 1)
    saves[chat_id]['fight']['block'] = 0


def attack(call, enemy, attack_damage, bot, arena=False):
    chat_id = call.from_user.id
    damage = round(attack_damage - enemy.block, 1)
    if arena:
        damaging(damage, enemy)
    else:
        enemy.damaging(attack_damage)
    if enemy.block >= attack_damage:
        saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Блок противника поглотил весь урон'
    else:
        if (type(enemy) == int and (arena and saves[enemy]['hp'] < 0)) or (type(enemy) != int and (not arena and enemy.hp < 0)):
            saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, противник мертв'
        else:
            if type(enemy) == int:
                hp = saves[enemy]['hp']
            else:
                hp = enemy.hp
            saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, осталось {hp}❤'
        if not arena and not check_enemy_died_and_killed_logic(call, enemy, bot):
            enemy.fight(call=chat_id, chance_per_percent=0.5)
            tf = True
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if check_death(chat_id, bot):
                        tf = False
                    elif tf:
                        enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
                enemy.you_skip_step_n = 0
            if tf:
                if check_death(chat_id, bot):
                    pass
        elif arena:
            saves[chat_id]['buffer']['fight_text']['keyboard'] = get_arena_fight_keyboard(enemy, your_step=False)


def fight_block(call, enemy, bot, arena=False):
    chat_id = call.from_user.id
    # damage = round(saves[chat_id]["fight"]["damage"] - enemy.block, 1)
    saves[chat_id]["fight"]["block"] += saves[chat_id]["fight"]["block_add"]
    saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы защищаетесь'
    if not arena and not check_enemy_died_and_killed_logic(call, enemy, bot):
        if not check_death(chat_id, bot):
            enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if not check_death(chat_id, bot):
                        saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Вы пропускаете ход'
                        enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
                        enemy.block = 0
                enemy.you_skip_step_n = 0
            saves[chat_id]['fight']['block'] = 0
            if check_death(chat_id, bot):
                pass  # просто проверить мертв ли
    elif arena:
        saves[chat_id]['buffer']['fight_text']['keyboard'] = get_arena_fight_keyboard(enemy, your_step=False)


def fight_dodge(call, enemy, bot, arena=False):
    chat_id = call.from_user.id
    dodge_chance = randint(1, 100)
    if dodge_chance <= saves[chat_id]["fight"]["dodge"]:
        saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Вы смогли уклониться и сумели контратаковать'
        if arena:
            damage = round(saves[chat_id]["fight"]["damage"] - saves[enemy]['block'], 1)
        else:
            damage = round(saves[chat_id]["fight"]["damage"] - enemy.block, 1)
        enemy.damaging(damage)
        if (not arena and (enemy.block >= saves[chat_id]["fight"]["damage"])) or \
                (arena and (saves[enemy]['block'] >= saves[chat_id]["fight"]["damage"])):
            saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Блок противника поглотил весь урон'
        else:
            if arena:
                enemy_hp = saves[enemy]['hp']
            else:
                enemy_hp = enemy.hp
            saves[chat_id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, осталось {enemy_hp}❤'
            if not arena and not check_enemy_died_and_killed_logic(call, enemy, bot):
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if not check_death(chat_id, bot):
                            enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
                enemy.you_skip_step_n = 0
                if check_death(chat_id, bot):
                    pass
    else:
        saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Вы не смогли уклониться'
        if not arena and not check_enemy_died_and_killed_logic(call, enemy, bot):
            enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if not check_death(chat_id, bot):
                        saves[chat_id]['buffer']['fight_text']['text'] += '\n' + 'Вы пропускаете ход'
                        enemy.fight(chat_id=chat_id, chance_per_percent=0.5)
            if check_death(chat_id, bot):
                pass


def send_fight_text(call, bot):
    chat_id = call.from_user.id
    if saves[chat_id]['buffer']["enemies"]:
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=saves[chat_id]['buffer']['fight_text']['text'],
                              reply_markup=saves[chat_id]['buffer']['fight_text']['keyboard'])
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=saves[chat_id]['buffer']['fight_text']['text'],
                              reply_markup=get_keyboard_drop_from_enemy(call))


def clear_fight_logs(chat_id):
    saves[chat_id]['buffer']['fight_text']['text'] = ''
    saves[chat_id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
    saves[chat_id]['buffer']["drop_items"] = []


def fight_checker(call, bot):
    chat_id = call.from_user.id
    if call.data == 'fight_ready':
        send_map(call, bot)
        clear_fight_logs(chat_id)
        save_to_db(chat_id)
    elif len(saves[chat_id]['buffer']['enemies']) != 0:
        enemy = saves[chat_id]['buffer']['enemies'][int(call.data.split('_')[2])]
        if 'attack' in call.data:
            attack(call, enemy, float(saves[chat_id]["fight"]["damage"]), bot)
            send_fight_text(call, bot)
        elif 'block' in call.data:
            fight_block(call, enemy, bot)
            send_fight_text(call, bot)
        elif 'dodge' in call.data:
            fight_dodge(call, enemy, bot)
            send_fight_text(call, bot)
        elif 'spells' in call.data:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text='Вот ваши способности', reply_markup=get_spells_keyboard(call))
        elif 'inv' in call.data:
            send_inventory(call, bot)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=call.message.text + '\n' + 'Из-за своей оплошности вы пропустили ход', reply_markup=get_fight_keyboard())
        mp_regen(chat_id)
    else:
        send_map(call, bot)
