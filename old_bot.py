import telebot
from pickle import load, dump
from random import randint, choice
from dotenv import load_dotenv
from os import environ
from time import sleep, time

load_dotenv()
if str(input('1 is main, another dev: ')) == '1':
    token = environ['main_token']
else:
    token = environ['dev_token']

CHARACTERISTICS = {'strength', 'agility', 'intelligence', 'lucky', 'wisdom', 'stamina'}

HERO = {'spells': {'Усиленный удар': {'librarian_gold': 100, 'cd': 3, 'mp': 5,
                                      'des': f"Вы используете свои силы, пытаясь как можно сильнее ударить противника\n"
                                             f"Наносите 110% вашего урона\nЦена: {100} золота"}}}

BASIC_CHARS = {'dodge': 5}

SEWER_SKINS_SHOP = {'🤡': 100, '😒': 100, '😡': 100, '🤓': 100, '😀': 100, '😈': 100,
                    '💩': 100, '👻': 100, '👺': 100, '👹': 100, '👿': 100, '💀': 100}

ITEMS = {'Паутина': {'des': {'Обычная паутина, которая может выпасть с паука'}, 'used': False}}

ENEMIES = {'skins': ['🕷'], 'Паук': {'spells': {'Защита паутиной': 10, 'Опутывание паутиной': 8}, 'xp': 5,
                                     'skin': '🕷', 'drop_item': {'Паутина': 1}, 'drop_gold': 10, 'drop_gold_edit': 3}}

QUESTS = {"Сбор паутины": {'things': {"Паутина": 5}, 'time_repeat': 3600, 'time_accept': 0, 'is_active': False,
                           'des': 'Не мог бы ты собрать для меня 5 паутинок?', 'xp': 20, 'reward': []}}


def write_class(chat_id, b):
    classes[chat_id] = b
    with open('saves/{}.txt'.format(chat_id), 'wb') as out:
        dump(b, out)


def read_class(chat_id):
    with open('saves/{}.txt'.format(chat_id), 'rb') as f:
        classes[chat_id] = load(f)


def get_damage_from_strength(strength):
    return strength * 0.5


def get_dodge_from_agility(agility):
    return 0.1 * agility


def get_chance_of_loot_from_lucky(lucky):
    return lucky * 0.1


def get_crit_from_lucky(lucky):
    return 0.2 * lucky


def get_mp_from_intelligence(intelligence):
    return intelligence * 5


def get_mp_regen_from_intelligence(intelligence):
    return 0.1 * intelligence


def get_mp_regen_from_wisdom(wisdom):
    return 1 * wisdom


def get_hp_from_stamina(stamina):
    return stamina * 2


def get_regen_hp_from_stamina(stamina):
    return stamina * 0.1


def get_block_from_stamina(stamina):
    a = stamina / 5
    return round(a, 1)


def message_cd():
    sleep(0)


class Enemy:
    def __init__(self, spells_list, lvl, xp, target, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                 name, enhancement_n, x, y):
        self.you_skip_step_n = 0
        self.name = name
        self.x = x
        self.y = y
        self.strength = strength
        self.agility = agility
        self.lucky = lucky
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.stamina = stamina
        self.hp = get_hp_from_stamina(stamina)
        self.max_hp = self.hp
        self.skin = skin
        self.mp = get_mp_from_intelligence(intelligence)
        self.max_mp = self.mp
        self.spells_list = spells_list
        self.lvl = lvl
        self.xp = xp
        self.target = target
        self.mp_regen = get_mp_regen_from_intelligence(intelligence) + get_mp_regen_from_wisdom(wisdom)
        self.damage = get_damage_from_strength(strength)
        self.block = 0
        self.block_add_int = get_block_from_stamina(stamina)
        self.dodge = get_dodge_from_agility(agility) + BASIC_CHARS['dodge']
        self.crit = get_crit_from_lucky(lucky)
        self.chance_of_loot = get_chance_of_loot_from_lucky(lucky)

    def random_move(self):
        pass

    def move_to_hero(self):
        pass

    def mp_regen(self):
        if self.mp < self.max_mp:
            if self.mp + self.mp_regen < self.max_mp:
                self.mp += self.mp_regen
            else:
                self.mp = self.max_mp

    def damaging(self, damage):
        # if self.block < damage:
        #     self.prev_damage = round(damage - self.block, 1)
        # else:
        #     self.prev_damage = round(self.block - damage, 1)
        if self.block > 0:
            self.hp = round(self.hp - damage + self.block, 1)
        else:
            self.hp = round(self.hp - damage + self.block, 1)
        self.block = 0

    def attack(self):
        self.target.get_damage(self.damage)

    def you_died_tf(self):
        if self.hp <= 0:
            return True
        return False

    def spell_use(self, name, chat_id):
        pass

    def attack_action(self):
        if self.target.block >= self.damage:
            bot.send_message(self.target.id, 'Ваш блок поглотил весь урон', reply_markup=keyboard_fight)
        else:
            damage = round(self.damage - self.target.block, 1)
            self.target.damaging(self.damage)
            bot.send_message(self.target.id, f'{self.skin} нанес вам {damage}❤ ед.урона, '
                                             f'у вас осталось {self.target.hp}❤',
                             reply_markup=keyboard_fight)
        message_cd()

    def block_action(self):
        self.block += self.block_add_int
        bot.send_message(self.target.id, f'{self.skin} защищается', reply_markup=keyboard_fight)
        message_cd()

    def dodge_action(self):
        dodge_chance = randint(1, 100)
        bot.send_message(self.target.id, f'{self.skin} пытается уклониться..', reply_markup=keyboard_fight)
        message_cd()
        if dodge_chance <= self.dodge:
            bot.send_message(self.target.id, f'{self.skin} смог уклониться и контатакует',
                             reply_markup=keyboard_fight)
            # attack
            self.attack_action()
        else:
            bot.send_message(self.target.id, f'{self.skin} не смог уклониться',
                             reply_markup=keyboard_fight)
        message_cd()

    def chance_actions(self, first_chance, second_chance):
        if first_chance:
            # attack
            self.attack_action()
        elif second_chance:
            # block
            self.block_action()
        else:
            # dodge
            self.dodge_action()
        self.mp_regen()

    def fight_actions(self, text, another_chance, chance_per_int, n):
        text = text.lower()
        if text == 'атака':
            self.chance_actions(n <= chance_per_int, n <= another_chance + chance_per_int)
        elif text == 'блок':
            self.chance_actions(n <= chance_per_int, 0 != 0)
        elif text == 'уклонение':
            self.chance_actions(n <= chance_per_int, n <= another_chance + chance_per_int)
        self.mp_regen()

    def fight(self, message, chance_per_percent, from_n=1, to_n=100):
        n = randint(from_n, to_n)
        chance_per_int = int(to_n * chance_per_percent)
        another_chance = (to_n - chance_per_int) / 2
        chance_of_spell = randint(0, 1)
        # chance_of_spell = 0
        if chance_of_spell == 0:
            if not self.spell_use(self.name, message.chat.id):
                self.fight_actions(message.text, another_chance, chance_per_int, n)
        else:
            self.fight_actions(message.text, another_chance, chance_per_int, n)


class Spider(Enemy):
    def __init__(self, spells_list, lvl, xp, target, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                 name, enhancement_n, x, y):
        super().__init__(spells_list, lvl, xp, target, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                         name, enhancement_n, x, y)

    def spell_use(self, name, chat_id):
        super().spell_use(name, chat_id)
        chance_of_activation = randint(1, 100)
        chance = 100 // len(ENEMIES[name]['spells'])
        n = 0
        for spell, spell_mp in ENEMIES[name]['spells'].items():
            n += 1
            if self.mp >= spell_mp:
                if n * chance >= chance_of_activation:
                    bot.send_message(chat_id, "{} использовал {}".format(name, spell), reply_markup=keyboard_fight)
                    if spell == 'Опутывание паутиной':
                        bot.send_message(chat_id,
                                         "Вас опутали паутиной, вы пытаетесь выбраться и кажется вам скоро удастся",
                                         reply_markup=keyboard_fight)
                        self.you_skip_step_n = 2
                    elif spell == 'Защита паутиной':
                        bot.send_message(chat_id,
                                         "Паук опутал себя паутиной в надежде защитить себя",
                                         reply_markup=keyboard_fight)
                        self.block += self.block_add_int
                    self.mp -= spell_mp
                    message_cd()
                    return True
        return False


class Logic:
    def __init__(self, message):
        # характеристики
        self.free_characters_points = 3

        self.strength = 1
        self.agility = 1
        self.lucky = 1
        self.intelligence = 1
        self.wisdom = 1
        self.stamina = 1
        #
        self.id = message.chat.id
        self.map = 'town'
        self.map_str = ''
        self.map_list = []

        self.x = 5
        self.y = 1

        self.hp = get_hp_from_stamina(self.stamina)
        self.max_hp = self.hp
        self.mp = get_mp_from_intelligence(self.intelligence)
        self.max_mp = self.mp
        self.mp_regen = get_mp_regen_from_intelligence(self.intelligence) + get_mp_regen_from_wisdom(self.wisdom)
        self.damage = get_damage_from_strength(self.strength)
        self.block_add_int = get_block_from_stamina(self.stamina)
        self.dodge = get_dodge_from_agility(self.agility) + BASIC_CHARS['dodge']
        self.active_dodge = False
        self.crit = get_crit_from_lucky(self.lucky)
        self.chance_of_loot = get_chance_of_loot_from_lucky(self.lucky)

        self.block = 0
        self.hero_lvl = 1
        self.hero_skin = '😐'
        self.xp = 0
        self.hero_need_xp = self.calc_xp_for_next_lvl()
        # self.hero_need_xp = 3
        self.spells_list = []
        self.gold = 0
        self.name = ''
        self.inventory = []
        self.inventory_max_slots = 10

        self.quests = QUESTS

        self.you_skip_step_n = 0

    def damaging(self, damage):
        if self.block > 0:
            self.hp = round(self.hp - damage + self.block, 1)
        else:
            self.hp = round(self.hp - damage, 1)
        self.block = 0

    def characteristic_keyboard(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        strength_button = telebot.types.InlineKeyboardButton(text="Сила ({}) | + 1".format(self.strength),
                                                             callback_data="strength")
        agility_button = telebot.types.InlineKeyboardButton(text="Ловкость ({}) | + 1".format(self.agility),
                                                            callback_data="agility")
        lucky_button = telebot.types.InlineKeyboardButton(text="Интеллект ({}) | + 1".format(self.intelligence),
                                                          callback_data="intelligence")
        intel_button = telebot.types.InlineKeyboardButton(text="Удача ({}) | + 1".format(self.lucky),
                                                          callback_data="lucky")
        wisdom_button = telebot.types.InlineKeyboardButton(text="Мудрость ({}) | + 1".format(self.wisdom),
                                                           callback_data="wisdom")
        stamina_button = telebot.types.InlineKeyboardButton(text="Выносливость ({}) | + 1".format(self.stamina),
                                                            callback_data="stamina")
        free_points_button = telebot.types.InlineKeyboardButton(
            text="Очки характеристик {}".format(self.free_characters_points), callback_data='points')
        # reset_button = telebot.types.InlineKeyboardButton(text="Сброс", callback_data="reset")
        keyboard.add(free_points_button)
        keyboard.add(strength_button)
        keyboard.add(agility_button)
        keyboard.add(lucky_button)
        keyboard.add(intel_button)
        keyboard.add(wisdom_button)
        keyboard.add(stamina_button)
        # keyboard.add(reset_button)
        return keyboard

    def calc_xp_for_next_lvl(self):
        return round((self.hero_lvl * 10) ** 1.5, 1)

    def level_up(self):
        self.hero_lvl += 1
        if self.hero_lvl % 5 == 0:
            self.inventory_max_slots += 1
        self.hero_need_xp = self.calc_xp_for_next_lvl()
        self.update_char()

    def update_char(self):
        self.hp = get_hp_from_stamina(self.stamina)
        self.max_hp = self.hp
        self.mp = get_mp_from_intelligence(self.intelligence)
        self.max_mp = self.mp
        self.mp_regen = get_mp_regen_from_intelligence(self.intelligence) + get_mp_regen_from_wisdom(self.wisdom)
        self.damage = get_damage_from_strength(self.strength)
        self.block_add_int = get_block_from_stamina(self.stamina)
        self.dodge = get_dodge_from_agility(self.agility)
        self.crit = get_crit_from_lucky(self.lucky)
        self.chance_of_loot = get_chance_of_loot_from_lucky(self.lucky)

    def add_xp(self, xp):
        self.xp += xp

    def get_xp(self):
        return self.xp

    def add_spell(self, name):
        self.spells_list.append(name)

    def check_lvl_up(self):
        if self.xp >= self.hero_need_xp:
            return True
        return False

    def death(self, message, keyboard):
        bot.send_message(message.chat.id, 'Вы умерли', reply_markup=keyboard)
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.xp -= 0.1 * self.xp
        self.load_map_move('town', x=5, y=1)

    def check_death(self, keyboard, message):
        if self.hp <= 0:
            self.death(message, keyboard)
            return True
        # else:
        #     bot.register_next_step_handler(message, self.fight, enemy)
        return False

    def load_map_move(self, name, x, y):
        self.map = name
        self.x = x
        self.y = y
        self.load_from_file_map()
        self.get_map()
        self.send_map(keyboard_move)

    def check_move(self, message, obj, forward, y, x):
        if obj in ENEMIES['skins']:
            bot.send_message(self.id, 'Вы напали на' + obj)
            if obj == ENEMIES["Паук"]['skin']:
                enemy = Spider(spells_list=ENEMIES['Паук']['spells'], lvl=2, xp=ENEMIES['Паук']['xp'],
                               target=self, skin=ENEMIES['Паук']['skin'], strength=2, agility=3, lucky=0,
                               intelligence=2, wisdom=1, stamina=2, name='Паук', enhancement_n=0, x=x, y=y)
            bot.send_message(self.id,
                             'У вас {}❤ {}💛'.format(self.hp, self.mp, enemy.hp),
                             reply_markup=keyboard_fight)
            bot.register_next_step_handler(message, self.fight, enemy)
        elif obj == '🌫':
            if forward == 1:  # ⬇️
                self.map_list[self.y][self.x] = '🌫'
                self.y += 1
                self.map_list[self.y][self.x] = self.hero_skin
                self.send_map(keyboard_move)
                bot.register_next_step_handler(message, self.hero_move)
            elif forward == 2:  # ➡️
                self.map_list[self.y][self.x] = '🌫'
                self.x += 1
                self.map_list[self.y][self.x] = self.hero_skin
                self.send_map(keyboard_move)
                bot.register_next_step_handler(message, self.hero_move)
            elif forward == 3:  # ⬆️
                self.map_list[self.y][self.x] = '🌫'
                self.y -= 1
                self.map_list[self.y][self.x] = self.hero_skin
                self.send_map(keyboard_move)
                bot.register_next_step_handler(message, self.hero_move)
            elif forward == 4:  # ⬅️
                self.map_list[self.y][self.x] = '🌫'
                self.x -= 1
                self.map_list[self.y][self.x] = self.hero_skin
                self.send_map(keyboard_move)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '👩🏼‍🏫':
            if self.map == 'library_town':
                bot.send_message(self.id, 'Вы начали разговор с библиотекарем', reply_markup=keyboard_librarian)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '👰🏼':
            if self.map == 'sewing_town':
                write_class(self.id, self)
                bot.send_message(self.id, 'Вы начали разговор со швеей', reply_markup=keyboard_sewer)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '🧔':
            if self.map == 'arena_town':
                write_class(self.id, self)
                bot.send_message(self.id, 'Вы начали разговор с распорядителем боев', reply_markup=keyboard_arena_town)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '📚':
            if self.map == 'town':
                self.load_map_move('library_town', x=5, y=9)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '🧵':
            if self.map == 'town':
                self.load_map_move('sewing_town', x=5, y=1)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '⚔':
            if self.map == 'town':
                self.load_map_move('arena_town', x=5, y=1)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '🚪':
            if self.map == 'town':
                self.load_map_move('level1', x=1, y=1)
            elif self.map == 'level1':
                self.load_map_move('town', x=5, y=1)
            elif self.map == 'library_town':
                self.load_map_move('town', x=6, y=2)
            elif self.map == 'sewing_town':
                self.load_map_move('town', x=4, y=2)
            elif self.map == 'arena_town':
                self.load_map_move('town', x=5, y=4)
            bot.register_next_step_handler(message, self.hero_move)
        else:
            self.send_map(keyboard_move)
            bot.register_next_step_handler(message, self.hero_move)

    def hero_move(self, message):
        butt = message.text
        if self.x <= 11 and self.y <= 11:
            if butt == '⬇️':
                obj = self.map_list[self.y + 1][self.x]
                self.check_move(message, obj, 1, self.y + 1, self.x)
            elif butt == '➡️':
                obj = self.map_list[self.y][self.x + 1]
                self.check_move(message, obj, 2, self.y, self.x + 1)
            elif butt == '⬆️':
                obj = self.map_list[self.y - 1][self.x]
                self.check_move(message, obj, 3, self.y - 1, self.x)
            elif butt == '⬅️' or butt == '⬅':
                obj = self.map_list[self.y][self.x - 1]
                self.check_move(message, obj, 4, self.y, self.x - 1)
            elif butt == '📚':
                n = '\n'
                bot.send_message(self.id,
                                 f"Ник: {classes[self.id].name}\nОпыт: {classes[self.id].xp}/{classes[self.id].hero_need_xp}\nСпособности: {', '.join(classes[self.id].spells_list)}\nСкин: {classes[self.id].hero_skin}\nКвесты: ({n.join(classes[self.id].quests[x]['des'] for x in QUESTS.keys() if classes[self.id].quests[x]['is_active'])})\nПрокачка характеристик:",
                                 reply_markup=classes[self.id].characteristic_keyboard())
                # bot.send_message(self.id, 'Нажмите играть для продолжения', reply_markup=keyboard_main)
                bot.register_next_step_handler(message, classes[self.id].hero_move)
            elif butt == '💼':
                read_class(self.id)
                bot.send_message(self.id, 'Ваш инвентарь:', reply_markup=classes[self.id].create_inventory_keyboard())
                bot.register_next_step_handler(message, self.hero_move)
            elif butt == 'Главное меню':
                bot.send_message(self.id, 'Вы перешли в главное меню', reply_markup=keyboard_main)
                bot.register_next_step_handler(message, send_text)
            else:
                bot.send_message(self.id, 'Вы, кажется, ошиблись действием', reply_markup=keyboard_move)
        else:
            bot.send_message(self.id, 'Не выходите за границы', reply_markup=keyboard_move)
            self.send_map(keyboard_move)
            bot.register_next_step_handler(message, self.hero_move)
        self.inventory = classes[self.id].inventory
        write_class(message.chat.id, self)

    def set_map(self, new_map_name):
        self.map = new_map_name

    def load_from_file_map(self):
        with open('levels/{}.txt'.format(self.map), 'rb') as f:
            self.map_list = load(f)
        self.map_list[self.y][self.x] = self.hero_skin

    def from_list_to_str_map(self):
        self.map_str = ''
        for i in range(len(self.map_list)):
            self.map_str += ''.join(self.map_list[i]) + '\n'

    def send_map(self, keyboard):
        self.from_list_to_str_map()
        bot.send_message(self.id, self.get_map(), reply_markup=keyboard)

    def get_map(self):
        if self.map_str == '':
            self.load_from_file_map()
            self.from_list_to_str_map()
        return self.map_str

    def get_level_map(self):
        return self.map

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_spells_keyboard(self):
        keyboard_spells = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_spells.add('назад')
        for spell in self.spells_list:
            keyboard_spells.add(spell)
        return keyboard_spells

    def fight_spells(self, message, enemy):
        text = message.text.lower()
        if text == 'назад':
            bot.send_message(message.chat.id, 'Вы в бою', reply_markup=keyboard_fight)
            bot.register_next_step_handler(message, self.fight, enemy)
        elif text == 'усиленный удар':
            bot.send_message(message.chat.id, f'Вы использовали {text}, вы наносите 110% урона')
            self.attack(message, enemy, self.damage * 1.1)

    def check_enemy_died_and_killed_logic(self, message, enemy):
        if enemy.you_died_tf():
            bonus_tf = False
            if enemy.lvl > self.hero_lvl:
                percent = abs(enemy.lvl - self.hero_lvl) * 0.1
                xp = round(percent * enemy.xp + enemy.xp, 1)
                bot.send_message(message.chat.id,
                                 f"Вы убили {enemy.skin} превосходящее вас по уровню за это "
                                 f"вы получаете на {percent * 100}% больше опыта",
                                 reply_markup=keyboard_fight)
                bonus_tf = True
            elif enemy.lvl == self.hero_lvl:
                xp = enemy.xp
            else:
                xp = round((1 - abs(self.hero_lvl - enemy.lvl) * 0.1) * enemy.xp, 1)
                self.add_xp(xp)
            if self.check_lvl_up():
                self.level_up()
                self.free_characters_points += 10

                if bonus_tf:
                    bot.send_message(message.chat.id,
                                     f'Вы получаете {xp} ед.опыта\nВы повысили уровень, '
                                     f'за это вы получаете 10 '
                                     f'очков характеристик, ваш уровень {self.hero_lvl}\n'
                                     f'До следующего '
                                     f'уровня осталось {round(self.hero_need_xp - self.xp, 1)} '
                                     f'ед.опыта',
                                     reply_markup=keyboard_move)
                else:
                    bot.send_message(message.chat.id,
                                     f'Вы убили {enemy.skin}, '
                                     f'вы получаете {xp} ед.опыта\nВы повысили уровень, за это '
                                     f'вы получаете 10 '
                                     f'очков характеристик, ваш уровень {self.hero_lvl}\n'
                                     f'До следующего уровня'
                                     f' осталось {round(self.hero_need_xp - self.xp, 1)} '
                                     f'ед.опыта',
                                     reply_markup=keyboard_move)
            else:
                bot.send_message(message.chat.id,
                                 f'Вы убили {enemy.skin}, вы получаете {xp} ед.опыта\n'
                                 f'До следующего уровня осталось {round(self.hero_need_xp - self.xp, 1)} '
                                 f'ед.опыта',
                                 reply_markup=keyboard_move)
            self.drop_from_enemy(message, enemy)
            self.map_list[enemy.y][enemy.x] = '🌫'
            self.send_map(keyboard_move)
            write_class(message.chat.id, self)
            return True
        return False

    def inventory_add_item(self, item):
        self.inventory.append(item)
        write_class(self.id, self)
        read_class(self.id)
        print(f'{self.id} {self.name} подобрал {item}')

    def drop_from_enemy(self, message, enemy):
        self.drop_items = []
        gold_edit = randint(-1 * ENEMIES[enemy.name]['drop_gold_edit'], ENEMIES[enemy.name]['drop_gold_edit'])
        gold_drop = ENEMIES[enemy.name]['drop_gold'] + gold_edit
        self.gold += gold_drop
        bot.send_message(self.id, f"Выпало {gold_drop} золота\nВаш баланс: {self.gold}")
        for item in ENEMIES[enemy.name]['drop_item'].keys():
            chance = randint(1, 100)
            if chance <= ENEMIES[enemy.name]['drop_item'][item] * 100:
                self.drop_items.append(item)
        if self.drop_items != 0:
            bot.send_message(message.chat.id, "Выберите, что хотите подобрать")
            bot.send_message(message.chat.id, f"Вам выпало:", reply_markup=self.keyboard_get_drop())
        else:
            bot.send_message(message.chat.id, "Вам ничего не выпало")

    def keyboard_get_drop(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(self.drop_items)):
            item_button = telebot.types.InlineKeyboardButton(text=self.drop_items[i],
                                                             callback_data=f"drop_from_enemy_{i}")
            keyboard.add(item_button)
        return keyboard

    def mp_regen(self):
        if self.mp < self.max_mp:
            if self.mp + self.mp_regen < self.max_mp:
                self.mp += self.mp_regen
            else:
                self.mp = self.max_mp

    def you_died_tf(self):
        if self.hp <= 0:
            return True
        return False

    def attack(self, message, enemy, attack_damage):
        damage = round(attack_damage - enemy.block, 1)
        enemy.damaging(attack_damage)
        if enemy.block >= attack_damage:
            bot.send_message(message.chat.id, 'Блок противника поглотил весь урон', reply_markup=keyboard_fight)
        else:
            bot.send_message(message.chat.id, f'Вы нанесли {damage}❤, осталось {enemy.hp}❤',
                             reply_markup=keyboard_fight)
            if self.check_enemy_died_and_killed_logic(message, enemy):
                bot.register_next_step_handler(message, self.hero_move)
            else:
                enemy.fight(message=message, chance_per_percent=0.5)
                tf = True
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            tf = False
                            bot.register_next_step_handler(message, self.hero_move)
                        elif tf:
                            bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                            enemy.fight(message=message, chance_per_percent=0.5)
                    enemy.you_skip_step_n = 0
                if tf:
                    if self.check_death(keyboard_move, message):
                        bot.register_next_step_handler(message, self.hero_move)
                    else:
                        bot.register_next_step_handler(message, self.fight, enemy)

    def fight_block(self, message, enemy):
        # damage = round(self.damage - enemy.block, 1)
        self.block += self.block_add_int
        # bot.send_message(message.chat.id, f'Вы защищаетесь',
        #                  reply_markup=keyboard_fight)
        if self.check_enemy_died_and_killed_logic(message, enemy):
            bot.register_next_step_handler(message, self.hero_move)
        else:
            if self.check_death(keyboard_move, message):
                bot.register_next_step_handler(message, self.hero_move)
            enemy.fight(message=message, chance_per_percent=0.5)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if self.check_death(keyboard_move, message):
                        bot.register_next_step_handler(message, self.hero_move)
                    bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                    enemy.fight(message=message, chance_per_percent=0.5)
                    enemy.block = 0
                    # if self.check_death(keyboard_move, message):
                    #     bot.register_next_step_handler(message, self.hero_move)
                enemy.you_skip_step_n = 0
            self.block = 0
            if self.check_death(keyboard_move, message):
                bot.register_next_step_handler(message, self.hero_move)
            else:
                bot.register_next_step_handler(message, self.fight, enemy)

    def fight_dodge(self, message, enemy):
        dodge_chance = randint(1, 100)
        if dodge_chance <= self.dodge:
            bot.send_message(message.chat.id, 'Вы смогли уклониться и сумели контратаковать',
                             reply_markup=keyboard_fight)
            damage = round(self.damage - enemy.block, 1)
            enemy.damaging(self.damage)
            if enemy.block >= self.damage:
                bot.send_message(message.chat.id, 'Блок противника поглотил весь урон', reply_markup=keyboard_fight)
            else:
                bot.send_message(message.chat.id, f'Вы нанесли {damage}❤, осталось {enemy.hp}❤',
                                 reply_markup=keyboard_fight)
                if self.check_enemy_died_and_killed_logic(message, enemy):
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    if enemy.you_skip_step_n != 0:
                        for i in range(enemy.you_skip_step_n):
                            if self.check_death(keyboard_move, message):
                                bot.register_next_step_handler(message, self.hero_move)
                            bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                            enemy.fight(message=message, chance_per_percent=0.5)
                    enemy.you_skip_step_n = 0
                    if self.check_death(keyboard_move, message):
                        bot.register_next_step_handler(message, self.hero_move)
                    else:
                        bot.register_next_step_handler(message, self.fight, enemy)
        else:
            bot.send_message(message.chat.id, 'Вы не смогли уклониться', reply_markup=keyboard_fight)
            if self.check_enemy_died_and_killed_logic(message, enemy):
                bot.register_next_step_handler(message, self.hero_move)
            else:
                enemy.fight(message=message, chance_per_percent=0.5)
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            bot.register_next_step_handler(message, self.hero_move)
                        bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                        enemy.fight(message=message, chance_per_percent=0.5)

                if self.check_death(keyboard_move, message):
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    bot.register_next_step_handler(message, self.fight, enemy)

    def fight(self, message, enemy):
        text = message.text.lower()
        if text == 'атака':
            self.attack(message, enemy, self.damage)
        elif text == 'блок':
            self.fight_block(message, enemy)
        elif text == 'уклонение':
            self.fight_dodge(message, enemy)
        elif text == 'способности':
            bot.send_message(message.chat.id, 'Вот ваши способности', reply_markup=self.get_spells_keyboard())
            bot.register_next_step_handler(message, self.fight_spells, enemy)
        elif text == '💼':
            if len(self.inventory) != 0:
                bot.send_message(self.id, 'Ваш инвентарь:', reply_markup=self.create_inventory_keyboard())
            else:
                bot.send_message(self.id, 'Ваш инвентарь пуст', reply_markup=keyboard_move)
            bot.register_next_step_handler(message, self.fight, enemy)
        else:
            bot.send_message(self.id, 'Из-за своей оплошности вы пропустили ход', reply_markup=keyboard_fight)
            bot.register_next_step_handler(message, self.fight, enemy)
        self.mp_regen()
        write_class(self.id, classes[self.id])

    def create_inventory_keyboard(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(classes[self.id].inventory)):
            item_button = telebot.types.InlineKeyboardButton(text=classes[self.id].inventory[i],
                                                             callback_data=f"inventory_{i}")
            keyboard.add(item_button)
        # write_class(self.id, self)
        # read_class(self.id)
        return keyboard
    
    def fight_spells_arena(self, message, enemy, im_first):
        text = message.text.lower()
        if text == 'назад':
            bot.send_message(message.chat.id, 'Вы в бою', reply_markup=keyboard_fight)
            bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)
        elif text == 'усиленный удар':
            bot.send_message(message.chat.id, f'Вы использовали {text}, вы наносите 110% урона')
            im_first = self.before_end_fight(True, im_first)
            self.attack_arena(message, enemy, self.damage * 1.1, im_first)
        
    def attack_arena(self, message, enemy, attack_damage, im_first):
        damage = round(attack_damage - enemy.block, 1)
        enemy.damaging(attack_damage)
        if enemy.block >= attack_damage:
            bot.send_message(message.chat.id, 'Блок противника поглотил весь урон', reply_markup=keyboard_fight)
        else:
            bot.send_message(message.chat.id, f'Вы нанесли {damage}❤, осталось {enemy.hp}❤',
                             reply_markup=keyboard_fight)
            if self.check_enemy_died_and_killed_logic(message, enemy):
                self.before_end_fight(True)
                bot.register_next_step_handler(message, self.hero_move)
            else:
                enemy.fight_arena(message, self, enemy.damage, im_first)
                tf = True
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            tf = False
                            self.before_end_fight()
                            bot.register_next_step_handler(message, self.hero_move)
                        elif tf:
                            bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                            im_first = self.before_end_fight(True, im_first)
                            enemy.fight_arena(message, self, enemy.damage, im_first)
                    enemy.you_skip_step_n = 0
                if tf:
                    if self.check_death(keyboard_move, message):
                        self.before_end_fight(True)
                        bot.register_next_step_handler(message, self.hero_move)
                    else:
                        im_first = self.before_end_fight(True, im_first)
                        bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)

    def fight_block_arena(self, message, enemy, im_first):
        # damage = round(self.damage - enemy.block, 1)
        self.block += self.block_add_int
        # bot.send_message(message.chat.id, f'Вы защищаетесь',
        #                  reply_markup=keyboard_fight)
        if self.check_enemy_died_and_killed_logic(message, enemy):
            self.before_end_fight(True)
            bot.register_next_step_handler(message, self.hero_move)
        else:
            if self.check_death(keyboard_move, message):
                bot.register_next_step_handler(message, self.hero_move)
            enemy.fight_arena(message, self, enemy.damage, im_first)
            if enemy.you_skip_step_n != 0:
                for i in range(enemy.you_skip_step_n):
                    if self.check_death(keyboard_move, message):
                        self.before_end_fight(True)
                        bot.register_next_step_handler(message, self.hero_move)
                    bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                    enemy.fight_arena(message, self, enemy.damage, im_first)
                    enemy.block = 0
                    # if self.check_death(keyboard_move, message):
                    #     bot.register_next_step_handler(message, self.hero_move)
                enemy.you_skip_step_n = 0
            self.block = 0
            if self.check_death(keyboard_move, message):
                self.before_end_fight(True)
                bot.register_next_step_handler(message, self.hero_move)
            else:
                im_first = self.before_end_fight(True, im_first)
                bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)

    def fight_dodge_arena(self, message, enemy, im_first):
        dodge_chance = randint(1, 100)
        if dodge_chance <= self.dodge:
            bot.send_message(message.chat.id, 'Вы смогли уклониться и сумели контратаковать',
                             reply_markup=keyboard_fight)
            damage = round(self.damage - enemy.block, 1)
            enemy.damaging(self.damage)
            if enemy.block >= self.damage:
                bot.send_message(message.chat.id, 'Блок противника поглотил весь урон', reply_markup=keyboard_fight)
            else:
                bot.send_message(message.chat.id, f'Вы нанесли {damage}❤, осталось {enemy.hp}❤',
                                 reply_markup=keyboard_fight)
                if self.check_enemy_died_and_killed_logic(message, enemy):
                    self.before_end_fight(True)
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    if enemy.you_skip_step_n != 0:
                        for i in range(enemy.you_skip_step_n):
                            if self.check_death(keyboard_move, message):
                                bot.register_next_step_handler(message, self.hero_move)
                            bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                            enemy.fight_arena(message, self, enemy.damage, im_first)
                    enemy.you_skip_step_n = 0
                    if self.check_death(keyboard_move, message):
                        self.before_end_fight(True)
                        bot.register_next_step_handler(message, self.hero_move)
                    else:
                        im_first = self.before_end_fight(True, im_first)
                        bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)
        else:
            bot.send_message(message.chat.id, 'Вы не смогли уклониться', reply_markup=keyboard_fight)
            if self.check_enemy_died_and_killed_logic(message, enemy):
                self.before_end_fight(True)
                bot.register_next_step_handler(message, self.hero_move)
            else:
                enemy.fight_arena(message, self, enemy.damage, im_first)
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            self.before_end_fight(True)
                            bot.register_next_step_handler(message, self.hero_move)
                        bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                        enemy.fight_arena(message, self, enemy.damage, im_first)

                if self.check_death(keyboard_move, message):
                    self.before_end_fight(True)
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    im_first = self.before_end_fight(True, im_first)
                    bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)

    def before_end_fight(self, arena=False, im_first=None):
        self.mp_regen()
        write_class(self.id, classes[self.id])
        if arena and im_first:
            return False  # im_first

    def fight_arena(self, message, enemy, im_first, who_i):
        text = message.text.lower()
        if im_first:
            if text == 'атака':
                self.attack_arena(message, enemy, self.damage, im_first)
            elif text == 'блок':
                self.fight_block_arena(message, enemy, im_first)
            elif text == 'уклонение':
                self.fight_dodge_arena(message, enemy, im_first)
            elif text == 'способности':
                bot.send_message(message.chat.id, 'Вот ваши способности', reply_markup=self.get_spells_keyboard())
                bot.register_next_step_handler(message, self.fight_spells_arena, enemy, im_first)
            elif text == '💼':
                if len(self.inventory) != 0:
                    bot.send_message(self.id, 'Ваш инвентарь:', reply_markup=self.create_inventory_keyboard())
                else:
                    bot.send_message(self.id, 'Ваш инвентарь пуст', reply_markup=keyboard_move)
                bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)
            else:
                bot.send_message(self.id, 'Из-за своей оплошности вы пропустили ход', reply_markup=keyboard_fight)
                im_first = self.before_end_fight(True, im_first)
                bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)
        else:
            bot.send_message(self.id, 'Ход противника', reply_markup=keyboard_fight)
            bot.register_next_step_handler(message, self.fight_arena, enemy, im_first)

    """
    Librarian logic
    begin
    """

    def keyboard_librarian_spells_shop(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text='Назад',
                                                                         callback_data="librarian_spells_shop_return")
        keyboard.add(librarian_spells_shop_spell)
        new_spells = list(HERO['spells'].keys())
        for spell in self.spells_list:
            if spell in new_spells:
                new_spells.remove(spell)
        for spell in new_spells:
            librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text=spell,
                                                                             callback_data=f"librarian_spells_shop_{spell}")
            keyboard.add(librarian_spells_shop_spell)
        return keyboard

    """
    Librarian logic
    end
    """
    """
    Sewer logic
    begin
    """

    def keyboard_sewer_skins_shop(self):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=5)
        librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text='Назад',
                                                                         callback_data="sewer_skins_shop_return")
        keyboard.add(librarian_spells_shop_spell)
        a = []
        n = 0
        for skin, cost in SEWER_SKINS_SHOP.items():
            if skin != self.hero_skin:
                n += 1
                librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text=skin + '|' + str(cost),
                                                                                 callback_data=f"sewer_skins_shop_{skin}")
                a.append(librarian_spells_shop_spell)
            if n == 5:
                keyboard.add(a[0], a[1], a[2], a[3], a[4])
                a = []
                n = 0
        return keyboard

    """
    Sewer logic
    end
    """


bot = telebot.TeleBot(token)
keyboard_main = telebot.types.ReplyKeyboardMarkup(True)
keyboard_main.row("Играть")
keyboard_main.row('Регистрация и удаление старого аккаунта')

keyboard_move = telebot.types.ReplyKeyboardMarkup(True)
keyboard_move.row('💼', '⬆️', '📚')
keyboard_move.row('⬅️', '⬇️', '➡️')
keyboard_move.row('Главное меню')

keyboard_fight = telebot.types.ReplyKeyboardMarkup(True)
keyboard_fight.row('Атака', "Блок", '💼')
keyboard_fight.row("Уклонение", "Способности")

keyboard_yes_or_no = telebot.types.ReplyKeyboardMarkup(True)
keyboard_yes_or_no.row('Да', "Нет")

"""
Library begin
"""
keyboard_librarian = telebot.types.InlineKeyboardMarkup()
keyboard_librarian.add(telebot.types.InlineKeyboardButton(text="Здравствуйте", callback_data="librarian_talk_hi"))

keyboard_librarian.add(
    telebot.types.InlineKeyboardButton(text="Магазин способностей", callback_data="librarian_spells_shop"))

keyboard_librarian.add(telebot.types.InlineKeyboardButton(text="До свидания", callback_data="librarian_talk_bye"))

keyboard_librarian_spells_shop_yes_or_no = telebot.types.InlineKeyboardMarkup()
keyboard_librarian_spells_shop_yes_or_no.add(telebot.types.InlineKeyboardButton(text="Да",
                                                                                callback_data="librarian_spells_shop_yes"),
                                             telebot.types.InlineKeyboardButton(text="Нет",
                                                                                callback_data="librarian_spells_shop_no"))
"""
Library end
"""

"""
Inventory
begin
"""
keyboard_return_in_inventory = telebot.types.InlineKeyboardMarkup()
keyboard_return_in_inventory.add(telebot.types.InlineKeyboardButton(text="Вернуться в инвентарь",
                                                                    callback_data="inventory_return"))
"""
Inventory
end
"""
"""
sewing
begin
"""
keyboard_sewer = telebot.types.InlineKeyboardMarkup()
keyboard_sewer.add(telebot.types.InlineKeyboardButton(text="Здравствуйте", callback_data="sewer_talk_hi"))

keyboard_sewer.add(telebot.types.InlineKeyboardButton(text="Магазин скинов",
                                                      callback_data="sewer_skins_shop"))
keyboard_sewer.add(telebot.types.InlineKeyboardButton(text="Сбор паутины",
                                                      callback_data="sewer_quest_spider_web"))
keyboard_sewer.add(telebot.types.InlineKeyboardButton(text="До свидания", callback_data="sewer_talk_bye"))

keyboard_sewer_skins_shop_yes_or_no = telebot.types.InlineKeyboardMarkup()
keyboard_sewer_skins_shop_yes_or_no.add(telebot.types.InlineKeyboardButton(text="Да",
                                                                           callback_data="sewer_skins_shop_yes"),
                                        telebot.types.InlineKeyboardButton(text="Нет",
                                                                           callback_data="sewer_skins_shop_no"))
"""
sewing
end.
Arena
begin
"""
keyboard_arena_town = telebot.types.InlineKeyboardMarkup()
arena_town = telebot.types.InlineKeyboardButton(text="Зарегистрироваться на бой",
                                                callback_data="arena_town_reg")
keyboard_arena_town.add(arena_town)
"""
Arena
end.
"""
classes = {}
arena_queue = []
print('start')
add_spell = ''
add_skin = ''
add_quest = ''
add_quest_keyboard = ''
keyboard_quest_yes_or_no = telebot.types.InlineKeyboardMarkup()
sewer_skins_shop_yes = telebot.types.InlineKeyboardButton(text="Да",
                                                          callback_data="quest_yes")
sewer_skins_shop_no = telebot.types.InlineKeyboardButton(text="Нет",
                                                         callback_data="quest_no")
keyboard_quest_yes_or_no.add(sewer_skins_shop_yes, sewer_skins_shop_no)


@bot.callback_query_handler(func=lambda call: 'arena_town' in call.data)
def dialog_with_arena_town_query_handler(call):
    if call.data == 'arena_town_reg':
        keyboard_arena_reg = telebot.types.InlineKeyboardMarkup()
        keyboard_arena_reg.add(telebot.types.InlineKeyboardButton(text="Зарегистрироваться",
                                                                  callback_data="arena_town_reg_yes"))
        keyboard_arena_reg.add(telebot.types.InlineKeyboardButton(text="Уйти с очереди",
                                                                  callback_data="arena_town_reg_no"))
        keyboard_arena_reg.add(telebot.types.InlineKeyboardButton(text="Я лучше уйду",
                                                                  callback_data="arena_town_reg_leave"))
        edit_message_in_inline(call,
                               "В мои обязанности входит рассказать правила перед этим, так что буду краток. Твоя задача зарегестрироваться и ждать момента, когда тебе подберется соперник. Вы будете сражаться, нанося друг другу удары по очереди. "
                               "Каждому на ход дается максимум 1 минута, не вложился в рамки? Тогда пропускаешь ход и он переходит противнику. Ах да! Насчет смерти, если умрешь на арене то умрешь по настоящему, так что береги жизнь. Мне нужны хорошие борцы.",
                               keyboard_arena_reg)
    elif call.data == 'arena_town_reg_yes':
        edit_message_in_inline(call, 'Жди..', keyboard_arena_town)
        arena_queue.append(call.from_user.id)
        reg_arena(call)
    elif call.data == 'arena_town_reg_no':
        try:
            arena_queue.remove(call.from_user.id)
            edit_message_in_inline(call, 'Хорошо, тогда приходи позже', keyboard_arena_town)
        except:
            edit_message_in_inline(call, 'Хорошо, тебя и так не было в очереди', keyboard_arena_town)


def reg_arena(call):
    while len(arena_queue) != 2:
        pass
    user1 = choice(arena_queue)
    user2 = choice(arena_queue)
    while user1 == user2:
        user1 = choice(arena_queue)
        user2 = choice(arena_queue)
    arena_queue.remove(user1)
    arena_queue.remove(user2)
    print(user1, user2)
    read_class(user1)
    read_class(user2)
    if call.from_user.id == user1:
        bot.send_message(user2, f'Начался бой с {classes[user1].name}', keyboard_fight)
    else:
        bot.send_message(user1, f'Начался бой с {classes[user2].name}', keyboard_fight)

    x = randint(0, 1)  # чей ход
    if x:
        if call.from_user.id == user1:
            bot.send_message(user1, "Вы ходите первым", keyboard_fight)
        else:
            bot.send_message(user2, f'{classes[user1].name} ходит первым', keyboard_fight)
        bot.register_next_step_handler(call.message, classes[user1].fight_arena, classes[user2], True, 1)
    else:
        if call.from_user.id == user2:
            bot.send_message(user2, "Вы ходите первым", keyboard_fight)
        else:
            bot.send_message(user1, f'{classes[user2].name} ходит первым', keyboard_fight)
        bot.register_next_step_handler(call.message, classes[user2].fight_arena, classes[user1], False, 0)


@bot.callback_query_handler(
    func=lambda call: 'sewer_skins_shop_yes' == call.data or 'sewer_skins_shop_no' == call.data)
def yes_or_no_skins(call):
    global add_skin
    if call.data == 'sewer_skins_shop_yes':
        classes[call.from_user.id].hero_skin = add_skin
        write_class(call.from_user.id, classes[call.from_user.id])
        edit_message_in_inline(call, f'Вы приобрели {add_skin}', classes[call.from_user.id].keyboard_sewer_skins_shop())
    else:
        edit_message_in_inline(call, 'Может быть вы хотите что-то еще?',
                               classes[call.from_user.id].keyboard_sewer_skins_shop())


@bot.callback_query_handler(func=lambda call: 'sewer_skins_shop' in call.data)
def dialog_with_sewer_spells_shop_query_handler(call):
    global add_skin
    z = len('sewer_skins_shop') + 1
    if call.data == 'sewer_skins_shop':
        edit_message_in_inline(call, 'Все, что я могу предложить:',
                               classes[call.from_user.id].keyboard_sewer_skins_shop())
    elif call.data[z:] in SEWER_SKINS_SHOP.keys():
        # classes[call.from_user.id].gold += 1000
        if classes[call.from_user.id].gold >= SEWER_SKINS_SHOP[call.data[z:]]:
            add_skin = call.data[z:]
            edit_message_in_inline(call, f'Вы хотите приобрести {call.data[z:]}?',
                                   keyboard_sewer_skins_shop_yes_or_no)
        else:
            edit_message_in_inline(call, 'У вас недостаточно средств',
                                   classes[call.from_user.id].keyboard_sewer_skins_shop())
    elif call.data == 'sewer_skins_shop_return':
        edit_message_in_inline(call, 'Что-то еще?', keyboard_sewer)


@bot.callback_query_handler(func=lambda call: 'sewer' in call.data)
def dialog_with_sewer_query_handler(call):
    global add_skin
    read_class(call.from_user.id)
    if call.data == 'sewer_spells_shop':
        edit_message_in_inline(call.from_user.id, 'Все, что я могу предложить:',
                               classes[call.from_user.id].keyboard_sewer_skins_shop())
    elif call.data == 'sewer_talk_hi':
        edit_message_in_inline(call, 'Приветики!', keyboard_sewer)
    elif call.data == 'sewer_talk_bye':
        edit_message_in_inline(call, 'Пока!')
        bot.send_message(call.from_user.id, 'Вы закончили разговор со швеей', reply_markup=keyboard_move)
        classes[call.from_user.id].send_map(keyboard_move)
    elif 'sewer_quest_spider_web' == call.data:
        quest('Сбор паутины', call, keyboard_sewer)


@bot.callback_query_handler(func=lambda call: 'quest_yes' == call.data or 'quest_no' == call.data)
def yes_or_no_quest(call):
    read_class(call.from_user.id)
    if call.data == 'quest_yes':
        classes[call.from_user.id].quests[add_quest]['is_active'] = True
        classes[call.from_user.id].quests[add_quest]['time_accept'] = time()
        write_class(call.from_user.id, classes[call.from_user.id])
        print(f'{classes[call.from_user.id].id} {classes[call.from_user.id].name} взял {add_quest}')
        edit_message_in_inline(call, 'Вы приняли квест!', add_quest_keyboard)
    else:
        edit_message_in_inline(call, 'Вы отказались от квеста!', add_quest_keyboard)


def quest(name, call, keyboard):
    global add_quest, add_quest_keyboard
    read_class(call.from_user.id)
    added = {k: QUESTS[k] for k, v in QUESTS.items() if k not in classes[
        call.from_user.id].quests}  # добавить квестов если их нет в списке квестов в классе logic
    for k, v in added.items():
        classes[call.from_user.id].quests[k] = v
    if classes[call.from_user.id].quests[name]['is_active'] is False:
        if (classes[call.from_user.id].quests[name]['time_accept'] + classes[call.from_user.id].quests[name][
            'time_repeat']) <= time():
            edit_message_in_inline(call, QUESTS[name]['des'], keyboard_quest_yes_or_no)
            add_quest = name
            add_quest_keyboard = keyboard
        else:
            edit_message_in_inline(call, "Вы уже принимали квест, идет перезарядка, подойдите позже", keyboard)
    else:
        tf = False
        for item_for_q in QUESTS[name]['things'].keys():
            if classes[call.from_user.id].inventory.count(item_for_q) >= QUESTS[name]['things'][item_for_q]:
                tf = True
            else:
                tf = False
                break
        if tf:
            print(f'{classes[call.from_user.id].id} {classes[call.from_user.id].name} выполнил {name}')
            for item in QUESTS[name]['things'].keys():
                for i in range(QUESTS[name]['things'][item]):
                    classes[call.from_user.id].inventory.remove(item)
            classes[call.from_user.id].quests[name]['is_active'] = False
            write_class(call.from_user.id, classes[call.from_user.id])
            edit_message_in_inline(call,
                                   f"Вы выполнили квест и получаете: {QUESTS[name]['xp']} опыта\n {', '.join(QUESTS[name]['reward'])}",
                                   keyboard)
        else:
            edit_message_in_inline(call, "Вы еще не выполнили квест", keyboard)


@bot.callback_query_handler(func=lambda call: 'inventory_' in call.data)
def inventory(call):
    text = call.data[10:]
    read_class(call.from_user.id)
    if text == 'return':
        edit_message_in_inline(call, 'Ваш инвентарь:',
                               classes[call.from_user.id].create_inventory_keyboard())
    else:
        try:
            edit_message_in_inline(call, ITEMS[classes[call.from_user.id].inventory[int(text)]]['des'],
                                   keyboard_return_in_inventory)
        except Exception as e:
            print('inventory', e)
            edit_message_in_inline(call,
                                   "Ошибка, сообщите об этом поддержке с подробным описанием ваших действий перед ошибкой",
                                   keyboard_return_in_inventory)


@bot.callback_query_handler(func=lambda call: 'drop_from_enemy_' in call.data)
def drop_from_enemy(call):
    read_class(call.from_user.id)
    if len(classes[call.from_user.id].inventory) != classes[call.from_user.id].inventory_max_slots:
        text = call.data[16:]
        item = classes[call.from_user.id].drop_items.pop(int(text))
        classes[call.from_user.id].inventory_add_item(item)
        write_class(call.from_user.id, classes[call.from_user.id])
        read_class(call.from_user.id)
        if len(classes[call.from_user.id].drop_items) != 0:
            edit_message_in_inline(call, f'Вы подобрали {item}, что-то еще?',
                                   classes[call.from_user.id].keyboard_get_drop())
        else:
            edit_message_in_inline(call, 'Предметов нет')
    else:
        edit_message_in_inline(call, f'Ваш инвентарь полон')


@bot.callback_query_handler(
    func=lambda call: 'librarian_spells_shop_yes' == call.data or 'librarian_spells_shop_no' == call.data)
def yes_or_no_spells(call):
    global add_spell
    if call.data == 'librarian_spells_shop_yes':
        classes[call.from_user.id].add_spell(add_spell)
        write_class(call.from_user.id, classes[call.from_user.id])
        edit_message_in_inline(call, f'Вы приобрели {add_spell}',
                               classes[call.from_user.id].keyboard_librarian_spells_shop())
    else:
        edit_message_in_inline(call, 'Может быть вы хотите что-то еще?',
                               classes[call.from_user.id].keyboard_spells_shop())


def edit_message_in_inline(call, text, keyboard=None):
    try:
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text,
                                    parse_mode='Markdown')
        if keyboard is not None:
            msg = bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                                reply_markup=keyboard)
    except Exception as e:
        print(e, text, call.message.text)


@bot.callback_query_handler(func=lambda call: 'librarian_spells_shop' in call.data)
def dialog_with_librarian_spells_shop_query_handler(call):
    global add_spell
    read_class(call.from_user.id)
    if call.data == 'librarian_spells_shop':
        edit_message_in_inline(call, 'Все, что я могу предложить:',
                               classes[call.from_user.id].keyboard_librarian_spells_shop())
    elif call.data[22:] in list(HERO['spells'].keys()):
        if classes[call.from_user.id].gold >= HERO['spells'][call.data[22:]]['librarian_gold']:
            edit_message_in_inline(call,
                                   HERO['spells'][call.data[22:]][
                                       'des'] + '\n' + f'Вы хотите приобрести {call.data[22:]}?',
                                   keyboard_librarian_spells_shop_yes_or_no)
            add_spell = call.data[22:]
        else:
            edit_message_in_inline(call, 'У вас недостаточно средств',
                                   classes[call.from_user.id].keyboard_librarian_spells_shop())
    elif call.data == 'librarian_spells_shop_return':
        edit_message_in_inline(call, 'Что-то еще?', keyboard_librarian)


@bot.callback_query_handler(func=lambda call: 'librarian' in call.data)
def dialog_with_librarian_query_handler(call):
    read_class(call.from_user.id)
    if call.data == 'librarian_spells_shop':
        bot.send_message(call.from_user.id, 'Все, что я могу предложить:',
                         classes[call.from_user.id].keyboard_librarian_spells_shop())
    elif call.data == 'librarian_talk_hi':
        edit_message_in_inline(call, 'Здравствуйте!', keyboard_librarian)
    elif call.data == 'librarian_talk_bye':
        edit_message_in_inline(call, 'До свидания!')
        bot.send_message(call.from_user.id, 'Вы закончили разговор с бибилиотекарем', reply_markup=keyboard_move)
        classes[call.from_user.id].send_map(keyboard_move)


def char_butt_calls(user_id):
    read_class(user_id)
    strength = classes[user_id].strength
    agility = classes[user_id].agility
    intelligence = classes[user_id].intelligence
    lucky = classes[user_id].lucky
    wisdom = classes[user_id].wisdom
    stamina = classes[user_id].stamina
    points = classes[user_id].free_characters_points
    return classes[user_id], strength, agility, intelligence, lucky, wisdom, stamina, points


@bot.callback_query_handler(func=lambda call: call.data in CHARACTERISTICS)
def characteristic_query_handler(call):
    classes[call.from_user.id], strength, agility, intelligence, lucky, wisdom, stamina, points = char_butt_calls(
        call.from_user.id)
    if points > 0:
        if call.data == 'strength':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко силы')
            strength += 1
            points -= 1
        elif call.data == 'agility':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко ловкости')
            agility += 1
            points -= 1
        elif call.data == 'intelligence':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко интеллекта')
            intelligence += 1
            points -= 1
        elif call.data == 'lucky':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко удачи')
            lucky += 1
            points -= 1
        elif call.data == 'wisdom':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко мудрости')
            wisdom += 1
            points -= 1
        elif call.data == 'stamina':
            bot.answer_callback_query(callback_query_id=call.id, text='+1 очко выносливости')
            stamina += 1
            points -= 1
        classes[call.from_user.id].strength = strength
        classes[call.from_user.id].agility = agility
        classes[call.from_user.id].free_characters_points = points
        classes[call.from_user.id].intelligence = intelligence
        classes[call.from_user.id].lucky = lucky
        classes[call.from_user.id].wisdom = wisdom
        classes[call.from_user.id].stamina = stamina
        classes[call.from_user.id].update_char()
        write_class(call.from_user.id, classes[call.from_user.id])
        read_class(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Прокачка характеристик:",
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                      reply_markup=classes[call.from_user.id].characteristic_keyboard())
    else:
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='У вас нет очков характеристик, повысьте ваш уровень')


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        read_class(message.chat.id)
    except:
        print(
            f'registration chat id: {message.chat.id} user name and surname {message.from_user.first_name, message.from_user.last_name}')
    if message.chat.id not in classes:
        begin_reg(message)


def begin_reg(message):
    b = Logic(message)
    b.load_from_file_map()
    b.from_list_to_str_map()
    write_class(message.chat.id, b)
    bot.send_message(message.chat.id, 'Укажите как к вам обращаться, длина ника не должна превышать 24 символа')
    bot.register_next_step_handler(message, reg_name)


def reg_name(message):
    name = message.text
    if len(name) <= 24:
        bot.send_message(message.chat.id, "Вы уверены, что хотите чтобы вас звали {}?".format(name),
                         reply_markup=keyboard_yes_or_no)
        bot.register_next_step_handler(message, yon_name, name)
    else:
        bot.send_message(message.chat.id, "Длина ника не должна превышать 24 символа".format(name))
        bot.register_next_step_handler(message, reg_name)


def yon_name(message, name):
    if yes_or_no(message):
        classes[message.chat.id].set_name(name)
        bot.send_message(message.chat.id, 'Вы успешно зарегистрировались', reply_markup=keyboard_main)
        write_class(message.chat.id, classes[message.chat.id])
        bot.register_next_step_handler(message, send_text)
    else:
        bot.send_message(message.chat.id, 'Укажите как к вам обращаться')
        bot.register_next_step_handler(message, reg_name)


def yes_or_no(message):
    if message.text.lower() == 'да':
        return True
    return False


@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        read_class(message.chat.id)
        if message.text.lower() == '/':
            classes[message.chat.id].gold += 1000
            for i in range(5):
                classes[message.chat.id].inventory.append('Паутина')
            write_class(message.chat.id, classes[message.chat.id])
            bot.send_message(message.chat.id, 'Привет, мой создатель')
            # bot.send_message(message.chat.id, '🌲', reply_markup=keyboard1)
        elif message.text.lower() == 'играть':
            bot.send_message(message.chat.id, classes[message.chat.id].get_map(), reply_markup=keyboard_move)
            bot.register_next_step_handler(message, classes[message.chat.id].hero_move)
        elif message.text.lower() == 'регистрация и удаление старого аккаунта':
            begin_reg(message)
        else:
            bot.send_message(message.chat.id, 'Вы, кажется, ошиблись', reply_markup=keyboard_main)
        # write_class(message.chat.id, classes[message.chat.id])
    except Exception as e:
        bot.send_message(message.chat.id, 'Возможно ты не зарегистрировался',
                         reply_markup=keyboard_main)
        begin_reg(message)
        print(e)


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        print('bot.polling error')
