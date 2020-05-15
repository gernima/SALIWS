import telebot
from char import *
from random import randint
from sqlite3 import connect


def from_db_dict_to_normal_dict(what, name):
    inv = {}
    b = cur.execute(f"""Select {what} from enemies where name = {name}""").fetchone()[0].split(';')
    if len(b) > 0 and b[0] != '':
        for i in [x.split(':') for x in b]:
            inv[i[0]] = int(i[1])
    return inv


def get_enemies_data_from_db():
    global ENEMIES
    enemies_in_db = cur.execute(f"""Select name from enemies""").fetchone()
    for enemy_name in enemies_in_db:
        ENEMIES[enemy_name] = ENEMIES['example']
        tables = ['name', 'skin', 'des', 'xp', 'drop_gold', 'drop_gold_edit']
        dict_tables = ['char']
        items = cur.execute(f"""Select skin from enemies where name = {enemy_name}""").fetchone()[0].split(';')
        for i in [x.split(':') for x in items]:
            ENEMIES[enemy_name]['drop_items'][i[0]] = ENEMIES_ITEM_TEMPLATE
            ENEMIES[enemy_name]['drop_items'][i[0]]['n'] = int(i[1])
            ENEMIES[enemy_name]['drop_items'][i[0]]['chance'] = int(i[2])
        ENEMIES['skins'].append(cur.execute(f"""Select skin from enemies where name = {enemy_name}""").fetchone()[0])
        for table in tables:
            ENEMIES[enemy_name][table] = cur.execute(f"""Select {table} from enemies where name = {enemy_name}""").fetchone()[0]
        for dict_table in dict_tables:
            ENEMIES[enemy_name][dict_table] = from_db_dict_to_normal_dict(dict_table, enemy_name)


con = connect("saves.db", check_same_thread=False)
cur = con.cursor()
ENEMIES_ITEM_TEMPLATE = {'example': {'n': 0, 'chance': 0}}
ENEMIES = {'skins': [], 'example': {'char': {}, 'des': '', 'spells': {}, 'xp': 0, 'skin': '', 'drop_items': {}, 'drop_gold': 0, 'drop_gold_edit': 0}}


class Enemy:
    def __init__(self, spells_list, lvl, xp, target, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                 name, enhancement_n, x, y, bot):
        self.you_skip_step_n = 0
        self.name = name
        self.bot = bot
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
            self.bot.send_message(self.target.id, 'Ваш блок поглотил весь урон', reply_markup=keyboard_fight)
        else:
            damage = round(self.damage - self.target.block, 1)
            self.target.damaging(self.damage)
            self.bot.send_message(self.target.id, f'{self.skin} нанес вам {damage}❤ ед.урона, '
                                             f'у вас осталось {self.target.hp}❤', reply_markup=keyboard_fight)

    def block_action(self):
        self.block += self.block_add_int
        self.bot.send_message(self.target.id, f'{self.skin} защищается', reply_markup=keyboard_fight)

    def dodge_action(self):
        dodge_chance = randint(1, 100)
        self.bot.send_message(self.target.id, f'{self.skin} пытается уклониться..', reply_markup=keyboard_fight)
        if dodge_chance <= self.dodge:
            self.bot.send_message(self.target.id, f'{self.skin} смог уклониться и контатакует', reply_markup=keyboard_fight)
            # attack
            self.attack_action()
        else:
            self.bot.send_message(self.target.id, f'{self.skin} не смог уклониться', reply_markup=keyboard_fight)

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
                 name, enhancement_n, x, y, bot):
        super().__init__(spells_list, lvl, xp, target, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                         name, enhancement_n, x, y, bot)

    def spell_use(self, name, chat_id):
        super().spell_use(name, chat_id)
        chance_of_activation = randint(1, 100)
        chance = 100 // len(ENEMIES[name]['spells'])
        n = 0
        for spell, spell_mp in ENEMIES[name]['spells'].items():
            n += 1
            if self.mp >= spell_mp:
                if n * chance >= chance_of_activation:
                    self.bot.send_message(chat_id, "{} использовал {}".format(name, spell), reply_markup=keyboard_fight)
                    if spell == 'Опутывание паутиной':
                        self.bot.send_message(chat_id,
                                         "Вас опутали паутиной, вы пытаетесь выбраться и кажется вам скоро удастся",
                                         reply_markup=keyboard_fight)
                        self.you_skip_step_n = 2
                    elif spell == 'Защита паутиной':
                        self.bot.send_message(chat_id,
                                         "Паук опутал себя паутиной в надежде защитить себя",
                                         reply_markup=keyboard_fight)
                        self.block += self.block_add_int
                    self.mp -= spell_mp
                    return True
        return False
