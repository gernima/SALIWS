import telebot
import pickle
from random import randint
import dotenv
from os import environ

dotenv.load_dotenv()
token = environ['dev_token']
# token = environ['main_token']
# from os.path import getsize
CHARACTERISTICS = {'strength', 'agility', 'intelligence', 'lucky', 'wisdom', 'stamina'}
HERO_SPELLS = ['Усиленный удар']
HERO_SPELLS_DESCRIPTION = {
    'Усиленный удар': "Вы используете свои силы, пытаясь как можно сильнее ударить противника\nНаносите 110% вашего урона\nЦена: 15 золота"}
HERO_SPELLS_GOLD_COST = {'Усиленный удар': 15}
HERO_SPELLS_MP_COST = {'Усиленный удар': 5}
HERO_SPELLS_CD = {'Усиленный удар': 3}
HERO_SPELLS_LIBRARY_COST = {'Усиленный удар': 100}

ENEMIES_SPELLS = {'Паук': {'Защита паутиной': 10, 'Опутывание паутиной': 8}}
# ENEMIES_SPELLS_COST = {}
ENEMIES_XP = {'Паук': 5}
ENEMIES_SKINS = {'Паук': '🕷'}
QUESTS_XP = {}
BASIC_DODGE = 5


def write_class(chat_id, b):
    classes[chat_id] = b
    with open('saves/{}.txt'.format(chat_id), 'wb') as out:
        pickle.dump(b, out)


def read_class(chat_id):
    with open('saves/{}.txt'.format(chat_id), 'rb') as f:
        classes[chat_id] = pickle.load(f)
    return classes[chat_id]


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
        self.dodge = get_dodge_from_agility(agility) + BASIC_DODGE
        self.crit = get_crit_from_lucky(lucky)
        self.chance_of_loot = get_chance_of_loot_from_lucky(lucky)

    def random_move(self):
        pass

    def move_to_hero(self):
        pass

    def mp_regen(self):
        if self.mp < self.max_mp:
            self.mp += self.mp_regen

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

    def block_action(self):
        self.block += self.block_add_int
        bot.send_message(self.target.id, f'{self.skin} защищается', reply_markup=keyboard_fight)

    def dodge_action(self):
        dodge_chance = randint(1, 100)
        bot.send_message(self.target.id, f'{self.skin} пытается уклониться..', reply_markup=keyboard_fight)
        if dodge_chance <= self.dodge:
            bot.send_message(self.target.id, f'{self.skin} смог уклониться и контатакует',
                             reply_markup=keyboard_fight)
            # attack
            self.attack_action()
        else:
            bot.send_message(self.target.id, f'{self.skin} не смог уклониться',
                             reply_markup=keyboard_fight)

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

    def fight_actions(self, text, another_chance, chance_per_int, n):
        text = text.lower()
        if text == 'атака':
            self.chance_actions(n <= chance_per_int, n <= another_chance + chance_per_int)
        elif text == 'блок':
            self.chance_actions(n <= chance_per_int, 0 != 0)
        elif text == 'уклонение':
            self.chance_actions(n <= chance_per_int, n <= another_chance + chance_per_int)

    def fight_logic(self, message, chance_per_percent, from_n=1, to_n=100):
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
        chance = 100 // len(ENEMIES_SPELLS[name])
        n = 0
        for spell, spell_mp in ENEMIES_SPELLS[name].items():
            n += 1
            if self.mp >= spell_mp:
                if n * chance >= chance_of_activation:
                    bot.send_message(chat_id, "{} использовал {}".format(name, spell), reply_markup=keyboard_fight)
                    if spell == 'Опутывание паутиной':
                        bot.send_message(chat_id,
                                         "Вас опутали паутиной, вы пытаетесь выбраться и кажется вам скоро удастся",
                                         reply_markup=keyboard_fight)
                        self.you_skip_step_n = 1
                    elif spell == 'Защита паутиной':
                        bot.send_message(chat_id,
                                         "Паук опутал себя паутиной в надежде защитить себя",
                                         reply_markup=keyboard_fight)
                        self.block += self.block_add_int
                    self.mp -= spell_mp
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
        self.dodge = get_dodge_from_agility(self.agility) + BASIC_DODGE
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
        reset_button = telebot.types.InlineKeyboardButton(text="Сброс", callback_data="reset")
        keyboard.add(free_points_button)
        keyboard.add(strength_button)
        keyboard.add(agility_button)
        keyboard.add(lucky_button)
        keyboard.add(intel_button)
        keyboard.add(wisdom_button)
        keyboard.add(stamina_button)
        keyboard.add(reset_button)
        return keyboard

    def calc_xp_for_next_lvl(self):
        return round((self.hero_lvl * 10) ** 1.5, 1)

    def level_up(self):
        self.hero_lvl += 1
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

    def check_death(self, keyboard, message):
        # print(f'self.hp {self.hp}')
        if self.hp <= 0:
            self.death(message, keyboard)
            self.send_map(keyboard_move)
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
        if obj in ENEMIES_SKINS.values():
            bot.send_message(self.id, 'Вы напали на' + self.map_list[self.y + 1][self.x])
            try:
                if obj == ENEMIES_SKINS["Паук"]:
                    enemy = Spider(spells_list=ENEMIES_SPELLS['Паук'], lvl=2, xp=ENEMIES_XP['Паук'],
                                   target=self, skin=ENEMIES_SKINS['Паук'], strength=2, agility=3, lucky=0,
                                   intelligence=2, wisdom=1, stamina=2, name='Паук', enhancement_n=0, x=x, y=y)
                # if self.hero_class != 'Маг':
                bot.send_message(self.id,
                                 'У вас {}❤ {}💛'.format(self.hp, self.mp, enemy.hp),
                                 reply_markup=keyboard_fight)
                # else:
                #     bot.send_message(self.id,
                #                      'У вас {}❤ {}💙'.format(self.hp, self.mp, 'in working'),
                #                      reply_markup=keyboard_fight)
                try:
                    if obj == ENEMIES_SKINS["Паук"]:
                        bot.register_next_step_handler(message, self.fight, enemy)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
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
            if self.map == 'town':
                self.load_map_move('library', x=5, y=9)
                bot.register_next_step_handler(message, self.hero_move)
            elif self.map == 'library':
                bot.send_message(self.id, 'Вы начали разговор с библиотекарем', reply_markup=keyboard_librarian)
                bot.register_next_step_handler(message, self.hero_move)
        elif obj == '🚪':
            if self.map == 'town':
                self.load_map_move('level1', x=1, y=1)
            elif self.map == 'level1':
                self.load_map_move('town', x=5, y=1)
            elif self.map == 'library':
                self.load_map_move('town', x=6, y=2)
            bot.register_next_step_handler(message, self.hero_move)
        else:
            self.send_map(keyboard_move)
            bot.register_next_step_handler(message, self.hero_move)

    def hero_move(self, message):

        butt = message.text
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
            bot.send_message(self.id,
                             "Прокачка характеристик:",
                             reply_markup=self.characteristic_keyboard())
            bot.register_next_step_handler(message, self.hero_move)
        else:
            bot.send_message(self.id, 'Вы, кажется, ошиблись действием', reply_markup=keyboard_move)
        write_class(message.chat.id, self)

    def set_map(self, new_map_name):
        self.map = new_map_name

    def load_from_file_map(self):
        with open('levels/{}.txt'.format(self.map), 'rb') as f:
            self.map_list = pickle.load(f)
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
            bot.send_message(message.chat.id, 'Хорошо', reply_markup=keyboard_fight)
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
            self.map_list[enemy.y][enemy.x] = '🌫'
            self.send_map(keyboard_move)
            write_class(message.chat.id, self)
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
                enemy.fight_logic(message=message, chance_per_percent=0.5)
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            bot.register_next_step_handler(message, self.hero_move)
                        bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                        enemy.fight_logic(message=message, chance_per_percent=0.5)
                    enemy.you_skip_step_n = 0
                if self.check_death(keyboard_move, message):
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    bot.register_next_step_handler(message, self.fight, enemy)

    def fight(self, message, enemy):
        text = message.text.lower()
        if text == 'атака':
            self.attack(message, enemy, self.damage)
        elif text == 'блок':
            # damage = round(self.damage - enemy.block, 1)
            self.block += self.block_add_int
            # bot.send_message(message.chat.id, f'Вы защищаетесь',
            #                  reply_markup=keyboard_fight)
            if self.check_enemy_died_and_killed_logic(message, enemy):
                bot.register_next_step_handler(message, self.hero_move)
            else:
                if self.check_death(keyboard_move, message):
                    bot.register_next_step_handler(message, self.hero_move)
                enemy.fight_logic(message=message, chance_per_percent=0.5)
                if enemy.you_skip_step_n != 0:
                    for i in range(enemy.you_skip_step_n):
                        if self.check_death(keyboard_move, message):
                            bot.register_next_step_handler(message, self.hero_move)
                        bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                        enemy.fight_logic(message=message, chance_per_percent=0.5)
                        enemy.block = 0
                        # if self.check_death(keyboard_move, message):
                        #     bot.register_next_step_handler(message, self.hero_move)
                    enemy.you_skip_step_n = 0
                self.block = 0
                if self.check_death(keyboard_move, message):
                    bot.register_next_step_handler(message, self.hero_move)
                else:
                    bot.register_next_step_handler(message, self.fight, enemy)
        elif text == 'уклонение':
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
                                enemy.fight_logic(message=message, chance_per_percent=0.5)
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
                    enemy.fight_logic(message=message, chance_per_percent=0.5)
                    if enemy.you_skip_step_n != 0:
                        for i in range(enemy.you_skip_step_n):
                            if self.check_death(keyboard_move, message):
                                bot.register_next_step_handler(message, self.hero_move)
                            bot.send_message(message.chat.id, 'Вы пропускаете ход', reply_markup=keyboard_fight)
                            enemy.fight_logic(message=message, chance_per_percent=0.5)

                    if self.check_death(keyboard_move, message):
                        bot.register_next_step_handler(message, self.hero_move)
                    else:
                        bot.register_next_step_handler(message, self.fight, enemy)
        elif text == 'способности':
            bot.send_message(message.chat.id, 'Вот ваши способности', reply_markup=self.get_spells_keyboard())
            bot.register_next_step_handler(message, self.fight_spells, enemy)
        elif text == '💼':
            bot.send_message(self.id, 'В разработке', keyboard_fight)
            bot.register_next_step_handler(message, self.fight, enemy)
        else:
            bot.send_message(self.id, 'Из-за своей оплошности вы пропустили ход', keyboard_fight)
            bot.register_next_step_handler(message, self.fight, enemy)
        write_class(self.id, classes[self.id])

    """
    Librarian logic
    """

    def keyboard_spells_shop(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text='Назад',
                                                                         callback_data="librarian_spells_shop_return")
        keyboard.add(librarian_spells_shop_spell)
        new_spells = HERO_SPELLS
        for spell in self.spells_list:
            if spell in new_spells:
                new_spells.remove(spell)
        for spell in new_spells:
            librarian_spells_shop_spell = telebot.types.InlineKeyboardButton(text=spell,
                                                                             callback_data=f"librarian_spells_shop_{spell}")
            keyboard.add(librarian_spells_shop_spell)
        return keyboard


bot = telebot.TeleBot(token)
keyboard_main = telebot.types.ReplyKeyboardMarkup(True)
keyboard_main.row("Играть")
keyboard_main.row('Регистрация и удаление старого аккаунта')

# ✨
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
Librarian begin
"""
keyboard_librarian = telebot.types.InlineKeyboardMarkup()
librarian_talk = telebot.types.InlineKeyboardButton(text="Здравствуйте", callback_data="librarian_talk_hi")
keyboard_librarian.add(librarian_talk)

librarian_spells_shop = telebot.types.InlineKeyboardButton(text="Магазин способностей",
                                                           callback_data="librarian_spells_shop")
keyboard_librarian.add(librarian_spells_shop)
librarian_talk = telebot.types.InlineKeyboardButton(text="До свидания", callback_data="librarian_talk_bye")
keyboard_librarian.add(librarian_talk)

keyboard_librarian_spells_shop_yes_or_no = telebot.types.InlineKeyboardMarkup()
librarian_spells_shop_yes = telebot.types.InlineKeyboardButton(text="Да",
                                                               callback_data="librarian_spells_shop_yes")
librarian_spells_shop_no = telebot.types.InlineKeyboardButton(text="Нет",
                                                              callback_data="librarian_spells_shop_no")
keyboard_librarian_spells_shop_yes_or_no.add(librarian_spells_shop_yes, librarian_spells_shop_no)
"""
Librarian end
"""

classes = {}
print('start')
add_spell = ''


@bot.callback_query_handler(func=lambda call: 'librarian_spells_shop_yes' == call.data or 'librarian_spells_shop_no' == call.data)
def yes_or_no_spells(call):
    global add_spell
    if call.data == 'librarian_spells_shop_yes':
        classes[call.from_user.id].add_spell(add_spell)
        print(classes[call.from_user.id].spells_list)
        write_class(call.from_user.id, classes[call.from_user.id])
        edit_message_in_inline(call, f'Вы приобрели {add_spell}', classes[call.from_user.id].keyboard_spells_shop())
    else:
        edit_message_in_inline(call, 'Может быть вы хотите что-то еще?',
                               classes[call.from_user.id].keyboard_spells_shop())


def edit_message_in_inline(call, text, keyboard=None):
    msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=text,
                                parse_mode='Markdown')
    if keyboard is not None:
        msg = bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                            reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'librarian_spells_shop' in call.data)
def dialog_with_librarian_spells_shop_query_handler(call):
    global add_spell
    if call.data == 'librarian_spells_shop':
        edit_message_in_inline(call, 'Все, что я могу предложить:', classes[call.from_user.id].keyboard_spells_shop())
    elif call.data[22:] in HERO_SPELLS:
        classes[call.from_user.id].gold += 1000
        if classes[call.from_user.id].gold >= HERO_SPELLS_GOLD_COST[call.data[22:]]:
            edit_message_in_inline(call,
                                   HERO_SPELLS_DESCRIPTION[
                                       call.data[22:]] + '\n' + f'Вы хотите приобрести {call.data[22:]}?',
                                   keyboard_librarian_spells_shop_yes_or_no)
            add_spell = call.data[22:]
        else:
            edit_message_in_inline(call, 'У вас недостаточно средств',
                                   classes[call.from_user.id].keyboard_spells_shop())
    elif call.data == 'librarian_spells_shop_return':
        edit_message_in_inline(call, 'Что-то еще?', keyboard_librarian)


@bot.callback_query_handler(func=lambda call: 'librarian' in call.data)
def dialog_with_librarian_query_handler(call):
    a = read_class(call.from_user.id)
    if call.data == 'librarian_spells_shop':
        bot.send_message(call.from_user.id, 'Все, что я могу предложить:',
                         classes[call.from_user.id].keyboard_spells_shop())
    elif call.data == 'librarian_talk_hi':
        edit_message_in_inline(call, 'Здравствуйте!', keyboard_librarian)
    elif call.data == 'librarian_talk_bye':
        edit_message_in_inline(call, 'До свидания!')
        bot.send_message(call.from_user.id, 'Вы закончили разговор с бибилиотекарем', reply_markup=keyboard_move)
        classes[call.from_user.id].send_map(keyboard_move)


def char_butt_calls(hero):
    # global strength, agility, intelligence, lucky, wisdom, stamina, points, target_char_hero, char_keyboard
    target_char_hero = hero

    strength = target_char_hero.strength
    agility = target_char_hero.agility
    intelligence = target_char_hero.intelligence
    lucky = target_char_hero.lucky
    wisdom = target_char_hero.wisdom
    stamina = target_char_hero.stamina
    points = target_char_hero.free_characters_points
    # if message.text.lower() == 'Готово' or message.text.lower() == 'Сохранить':
    #     bot.register_next_step_handler(message, target_char_hero.hero_move)
    return target_char_hero, strength, agility, intelligence, lucky, wisdom, stamina, points


@bot.callback_query_handler(func=lambda call: call.data in CHARACTERISTICS)
def characteristic_query_handler(call):
    target_char_hero, strength, agility, intelligence, lucky, wisdom, stamina, points = char_butt_calls(
        read_class(call.from_user.id))
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

        target_char_hero.strength = strength
        target_char_hero.agility = agility
        target_char_hero.free_characters_points = points
        target_char_hero.intelligence = intelligence
        target_char_hero.lucky = lucky
        target_char_hero.wisdom = wisdom
        target_char_hero.stamina = stamina
        target_char_hero.free_characters_points = points
        target_char_hero.update_char()
        write_class(call.from_user.id, target_char_hero)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Прокачка характеристик:",
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                      reply_markup=read_class(call.from_user.id).characteristic_keyboard())
    else:
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='У вас нет очков характеристик, чтобы их получить повысьте ваш уровень')


@bot.message_handler(commands=['start'])
def start_message(message):
    # bot.send_message(message.chat.id, '🌲', reply_markup=keyboard1)
    try:
        read_class(message.chat.id)
    except Exception as e:
        print(e)
    if message.chat.id not in classes:
        begin_reg(message)


def begin_reg(message):
    b = Logic(message)
    b.load_from_file_map()
    b.from_list_to_str_map()
    write_class(message.chat.id, b)
    bot.send_message(message.chat.id, 'Укажите как к вам обращаться')
    bot.register_next_step_handler(message, reg_name)


def reg_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Вы уверены, что хотите чтобы вас звали {}?".format(name),
                     reply_markup=keyboard_yes_or_no)
    bot.register_next_step_handler(message, yon_name, name)


def yon_name(message, name):
    if yes_or_no(message):

        classes[message.chat.id].set_name(name)
        bot.send_message(message.chat.id, 'Вы успешно зарегестрировались', reply_markup=keyboard_main)
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
    # print(message)
    try:
        a = read_class(message.chat.id)

        if message.text.lower() == '/':
            bot.send_message(message.chat.id, 'Привет, мой создатель')
            # bot.send_message(message.chat.id, '🌲', reply_markup=keyboard1)
        elif message.text.lower() == 'играть':
            bot.send_message(message.chat.id, a.get_map(), reply_markup=keyboard_move)
            bot.register_next_step_handler(message, a.hero_move)
        elif message.text.lower() == 'регистрация и удаление старого аккаунта':
            begin_reg(message)
        else:
            bot.send_message(message.chat.id, 'Err', reply_markup=keyboard_main)

        write_class(message.chat.id, a)
    except Exception as e:
        bot.send_message(message.chat.id, 'Возможно ты не зарегистрировался',
                         reply_markup=keyboard_main)
        begin_reg(message)
        print(e)


bot.polling()
