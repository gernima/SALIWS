import telebot
from keyboards import *
from random import randint
from base_var_and_func import *


def is_died(call):
    if saves[call.from_user.id]['fight']['hp'] <= 0:
        return True
    return False


def add_xp(call, xp):
    saves[call.from_user.id]['xp'] += xp


def check_lvl_up(call):
    if saves[call.from_user.id]["xp"] >= saves[call.from_user.id]["need_xp"]:
        return True
    return False


def level_up(call):
    saves[call.from_user.id]["lvl"] += 1
    if saves[call.from_user.id]["lvl"] % 5 == 0:
        saves[call.from_user.id]["inventory_max_n"] += 1
    saves[call.from_user.id]["need_xp"] = calc_xp_for_next_lvl(call)
    update_char(call)


def check_enemy_died_and_killed_logic(call, enemy, bot):
    text = ''
    if enemy.you_died_tf():
        saves[call.from_user.id]['buffer']['enemies'].remove(enemy)
        bonus_tf = False
        if enemy.lvl > saves[call.from_user.id]['lvl']:
            percent = abs(enemy.lvl - saves[call.from_user.id]['lvl']) * 0.1
            xp = round(percent * enemy.xp + enemy.xp, 1)
            text += f"Вы убили {enemy.skin} превосходящее вас по уровню за это вы получаете на {percent * 100}% больше опыта"
            bonus_tf = True
        elif enemy.lvl == saves[call.from_user.id]['lvl']:
            xp = enemy.xp
        else:
            xp = round((1 - abs(saves[call.from_user.id]['lvl'] - enemy.lvl) * 0.1) * enemy.xp, 1)
        add_xp(call, xp)
        if check_lvl_up(call):
            level_up(call)
            saves[call.from_user.id]["char"]["free_char"] += 10
            if bonus_tf:
                text += f'Вы получаете {xp} ед.опыта\nВы повысили уровень, за это вы получаете 10 очков характеристик, ваш уровень {saves[call.from_user.id]["lvl"]}\nДо следующего уровня осталось {round(saves[call.from_user.id]["need_xp"] - saves[call.from_user.id]["xp"], 1)} ед.опыта'
            else:
                text += f'Вы убили {enemy.skin}, вы получаете {xp} ед.опыта\nВы повысили уровень, за это вы получаете 10 очков характеристик, ваш уровень {saves[call.from_user.id]["lvl"]}\nДо следующего уровня осталось {round(saves[call.from_user.id]["need_xp"] - saves[call.from_user.id]["xp"], 1)} ед.опыта'
        else:
            text += f'Вы убили {enemy.skin}, вы получаете {xp} ед.опыта\nДо следующего уровня осталось {round(saves[call.from_user.id]["need_xp"] - saves[call.from_user.id]["xp"], 1)} ед.опыта'
        saves[call.from_user.id]['buffer']['fight_text']['text'] = text + '\n'
        drop_from_enemy(call, enemy, bot)
        return True
    return False


def drop_from_enemy(call, enemy, bot):
    text = ''
    saves[call.from_user.id]['buffer']['fight_text']['keyboard'] = get_keyboard_drop_from_enemy(call)
    saves[call.from_user.id]['buffer']["drop_items"] = []
    gold_edit = randint(-1 * ENEMIES[enemy.name]['drop_gold_edit'], ENEMIES[enemy.name]['drop_gold_edit'])
    gold_drop = ENEMIES[enemy.name]['drop_gold'] + gold_edit
    saves[call.from_user.id]["gold"] += gold_drop
    text += f"Выпало {gold_drop} золота\nВаш баланс: {saves[call.from_user.id]['gold']}"
    for item in ENEMIES[enemy.name]['drop_items'].keys():
        chance = randint(1, 100)
        if chance <= ENEMIES[enemy.name]['drop_items'][item]['chance']:
            for _ in range(ENEMIES[enemy.name]['drop_items'][item]['n']):
                saves[call.from_user.id]['buffer']["drop_items"].append(item)
    if len(saves[call.from_user.id]['buffer']["drop_items"]) != 0:
        text += '\n' + f"Выберите предметы:"
    saves[call.from_user.id]['buffer']['fight_text']['text'] += text


def drop_from_enemy_checker(call, bot):
    if len(saves[call.from_user.id]['inventory'].keys()) != saves[call.from_user.id]['inventory_max_n']:
        text = call.data[16:]
        item = saves[call.from_user.id]['buffer']['drop_items'].pop(int(text))
        inventory_add_item(call, item)
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы подобрали {item}'
        send_fight_text(call, bot)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text=f'Ваш инвентарь полон')


def inventory_add_item(call, item):
    if item in saves[call.from_user.id]["inventory"]:
        saves[call.from_user.id]["inventory"][item] += 1
    else:
        saves[call.from_user.id]["inventory"][item] = 1


def mp_regen(call):
    if saves[call.from_user.id]['fight']["mp"] < saves[call.from_user.id]['fight']['max_mp']:
        if saves[call.from_user.id]['fight']["mp"] + saves[call.from_user.id]["fight"]["mp_regen"] < saves[call.from_user.id]['fight']['max_mp']:
            saves[call.from_user.id]['fight']["mp"] += saves[call.from_user.id]["fight"]["mp_regen"]
        else:
            saves[call.from_user.id]['fight']["mp"] = saves[call.from_user.id]['fight']['max_mp']


def death(call, bot):
    max_hp = get_hp_from_stamina(saves[call.from_user.id]["char"]["stamina"])
    saves[call.from_user.id]['fight']['hp'] = max_hp
    max_mp = get_mp_from_intelligence(saves[call.from_user.id]["char"]["intelligence"])
    saves[call.from_user.id]['mp'] = max_mp
    minus_xp = 0.1 * saves[call.from_user.id]['xp']
    if saves[call.from_user.id]['xp'] - minus_xp >= 0:
        saves[call.from_user.id]['xp'] -= minus_xp
    else:
        saves[call.from_user.id]['xp'] = 0
    saves[call.from_user.id]['pos']['map'] = 'town_Bram'
    saves[call.from_user.id]['pos']['x'] = 5
    saves[call.from_user.id]['pos']['y'] = 2
    saves[call.from_user.id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
    saves[call.from_user.id]['buffer']['fight_text']['text'] = ''
    saves[call.from_user.id]['fight']['enemies'] = []
    # bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
    #                       text=f'Вы мертвы\n{load_map(call.from_user.id)}', reply_markup=ok_fight_keyboard)


def check_death(call, bot):
    if is_died(call):
        death(call, bot)
        return True
    return False


def fight_spells_checker(call, bot):
    if len(saves[call.from_user.id]['buffer']['enemies']) != 0:
        text = call.data
        enemy = saves[call.from_user.id]['buffer']['enemies'][int(call.data.split('_')[1])]
        if 'return_to_fight' in text:
            saves[call.from_user.id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
            send_fight_text(call, bot)
        elif 'усиленный удар' in text:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы использовали {text}'
            attack(call, enemy, saves[call.from_user.id]["fight"]["damage"] * 1.1, bot)
    else:
        send_fight_text(call, bot)


def damaging(damage, call):
    if saves[call.from_user.id]['fight']['block'] > 0:
        saves[call.from_user.id]['fight']['hp'] = round(saves[call.from_user.id]['fight']['hp'] - damage + saves[call.from_user.id]['fight']['block'], 1)
    else:
        saves[call.from_user.id]['fight']['hp'] = round(saves[call.from_user.id]['fight']['hp'] - damage, 1)
    saves[call.from_user.id]['fight']['block'] = 0


def attack(call, enemy, attack_damage, bot):
    damage = round(attack_damage - enemy.block, 1)
    enemy.damaging(attack_damage)
    if enemy.block >= attack_damage:
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Блок противника поглотил весь урон'
    else:
        if enemy.hp < 0:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, противник мертв'
        else:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, осталось {enemy.hp}❤'
        if not check_enemy_died_and_killed_logic(call, enemy, bot):
            enemy.fight(call=call, chance_per_percent=0.5)
            tf = True
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if check_death(call, bot):
                        tf = False
                    elif tf:
                        enemy.fight(call=call, chance_per_percent=0.5)
                enemy.you_skip_step_n = 0
            if tf:
                if check_death(call, bot):
                    pass


def fight_block(call, enemy, bot):
    # damage = round(saves[call.from_user.id]["fight"]["damage"] - enemy.block, 1)
    saves[call.from_user.id]["fight"]["block"] += saves[call.from_user.id]["fight"]["block_add"]
    saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы защищаетесь'
    if not check_enemy_died_and_killed_logic(call, enemy, bot):
        if not check_death(call, bot):
            enemy.fight(call=call, chance_per_percent=0.5)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if not check_death(call, bot):
                        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Вы пропускаете ход'
                        enemy.fight(call=call, chance_per_percent=0.5)
                        enemy.block = 0
                        # if self.check_death(get_move_keyboard(), call):
                        #     bot.register_next_step_handler(call, self.hero_move)
                enemy.you_skip_step_n = 0
            saves[call.from_user.id]['fight']['block'] = 0
            if check_death(call, bot):
                pass  # просто проверить мертв ли
                # send_map(call, bot)
            # else:
            #     bot.register_next_step_handler(call, self.fight, enemy)


def fight_dodge(call, enemy, bot):
    dodge_chance = randint(1, 100)
    if dodge_chance <= saves[call.from_user.id]["fight"]["dodge"]:
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Вы смогли уклониться и сумели контратаковать'
        damage = round(saves[call.from_user.id]["fight"]["damage"] - enemy.block, 1)
        enemy.damaging(saves[call.from_user.id]["fight"]["damage"])
        if enemy.block >= saves[call.from_user.id]["fight"]["damage"]:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Блок противника поглотил весь урон'
        else:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'Вы нанесли {damage}❤, осталось {enemy.hp}❤'
            if not check_enemy_died_and_killed_logic(call, enemy, bot):
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if not check_death(call, bot):
                            # send_map(call, bot)
                            # bot.send_call(call.from_user.id, 'Вы пропускаете ход', reply_markup=get_fight_keyboard())
                            enemy.fight(call=call, chance_per_percent=0.5)
                enemy.you_skip_step_n = 0
                if check_death(call, bot):
                    pass
                    # send_map(call, bot)
                # else:
                #     bot.register_next_step_handler(call, self.fight, enemy)
    else:
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Вы не смогли уклониться'
        if not check_enemy_died_and_killed_logic(call, enemy, bot):
            enemy.fight(call=call, chance_per_percent=0.5)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if not check_death(call, bot):
                        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Вы пропускаете ход'
                        enemy.fight(call=call, chance_per_percent=0.5)
            if check_death(call, bot):
                pass
                # send_map(call, bot)
            # else:
            #     bot.register_next_step_handler(call, self.fight, enemy)


def send_fight_text(call, bot):
    if len(saves[call.from_user.id]['buffer']["drop_items"]) == 0:
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=saves[call.from_user.id]['buffer']['fight_text']['text'],
                              reply_markup=saves[call.from_user.id]['buffer']['fight_text']['keyboard'])
    else:
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=saves[call.from_user.id]['buffer']['fight_text']['text'],
                              reply_markup=get_keyboard_drop_from_enemy(call))


def clear_fight_logs(chat_id):
    saves[chat_id]['buffer']['fight_text']['text'] = ''
    saves[chat_id]['buffer']['fight_text']['keyboard'] = get_fight_keyboard()
    saves[chat_id]['buffer']["drop_items"] = []


def fight_checker(call, bot):
    if call.data == 'fight_ready':
        send_map(call, bot)
        clear_fight_logs(call.from_user.id)
        save_to_db(call.from_user.id)
    elif len(saves[call.from_user.id]['buffer']['enemies']) != 0:
        enemy = saves[call.from_user.id]['buffer']['enemies'][int(call.data.split('_')[2])]
        if 'attack' in call.data:
            attack(call, enemy, float(saves[call.from_user.id]["fight"]["damage"]), bot)
            send_fight_text(call, bot)
        elif 'block' in call.data:
            fight_block(call, enemy, bot)
            send_fight_text(call, bot)
        elif 'dodge' in call.data:
            fight_dodge(call, enemy, bot)
            send_fight_text(call, bot)
        elif 'spells' in call.data:
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='Вот ваши способности', reply_markup=get_spells_keyboard(call))
        elif 'inv' in call.data:
            send_inventory(call, bot)
        else:
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=call.message.text + '\n' + 'Из-за своей оплошности вы пропустили ход', reply_markup=get_fight_keyboard())
        mp_regen(call)
    else:
        send_map(call, bot)
