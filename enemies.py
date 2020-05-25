import telebot
from char import *
from random import randint
from sqlite3 import connect
from keyboards import *
from fight import *
from base_var_and_func import *


class Enemy:
    def __init__(self, spells_list, xp, skin, strength, agility, lucky, intelligence, wisdom, stamina,
                 name, enhancement_n, x, y, bot, lvl):
        self.you_skip_step_n = 0
        self.name = name
        self.bot = bot
        self.x = x
        self.lvl = lvl
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
        self.xp = xp
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

    def f_mp_regen(self):
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

    def attack(self, call):
        damaging(self.damage, call)

    def you_died_tf(self):
        if self.hp <= 0:
            return True
        return False

    def spell_use(self, call):
        pass

    def attack_action(self, call):
        if saves[call.from_user.id]['fight']['block'] >= self.damage:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + 'Ваш блок поглотил весь урон'
        else:
            damage = round(self.damage - saves[call.from_user.id]['fight']['block'], 1)
            damaging(self.damage, call)
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'{self.name} {self.skin} нанес вам {damage}❤ ед.урона, у вас осталось {saves[call.from_user.id]["fight"]["hp"]}❤'

    def block_action(self, call):
        self.block += self.block_add_int
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'{self.name} {self.skin} защищается'

    def dodge_action(self, call):
        dodge_chance = randint(1, 100)
        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'{self.name} {self.skin} пытается уклониться..'
        if dodge_chance <= self.dodge:
            saves[call.from_user.id]['buffer']['fight_text']['text']['text'] += '\n' + f'{self.name} {self.skin} смог уклониться и контатакует'
            # attack
            self.attack_action(call)
        else:
            saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f'{self.name} {self.skin} не смог уклониться'

    def chance_actions(self, first_chance, second_chance, call):
        if first_chance:
            # attack
            self.attack_action(call)
        elif second_chance:
            # block
            self.block_action(call)
        else:
            # dodge
            self.dodge_action(call)
        self.f_mp_regen()
        # send_fight_text(call, self.bot)

    def fight_actions(self, call, another_chance, chance_per_int, n):
        self.chance_actions(n <= chance_per_int, n <= another_chance + chance_per_int, call)

    def fight(self, call, chance_per_percent, from_n=1, to_n=100):
        n = randint(from_n, to_n)
        chance_per_int = int(to_n * chance_per_percent)
        another_chance = (to_n - chance_per_int) / 2
        chance_of_spell = randint(0, 1)
        # chance_of_spell = 0
        if chance_of_spell == 0:
            if not self.spell_use(call.from_user.id):
                self.fight_actions(call, another_chance, chance_per_int, n)
        else:
            self.fight_actions(call, another_chance, chance_per_int, n)


class Spider(Enemy):
    def __init__(self, name, enhancement_n, x, y, bot):
        super().__init__(ENEMIES[name]['spells'], ENEMIES[name]['xp'], ENEMIES[name]['skin'],
                         ENEMIES[name]['char']['strength'], ENEMIES[name]['char']['agility'],
                         ENEMIES[name]['char']['lucky'], ENEMIES[name]['char']['intelligence'],
                         ENEMIES[name]['char']['wisdom'], ENEMIES[name]['char']['stamina'], name,
                         enhancement_n, x, y, bot, ENEMIES[name]['lvl'])

    def spell_use(self, call):
        super().spell_use(call)
        chance_of_activation = randint(1, 100)
        n_spells = len(ENEMIES[self.name]['spells'])
        if n_spells > 0:
            chance = 100 // n_spells
        else:
            chance = 0
        n = 0
        for spell, spell_mp in ENEMIES[self.name]['spells'].items():
            n += 1
            if self.mp >= spell_mp:
                if n * chance >= chance_of_activation:
                    saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f"{self.name} {self.name} использовал {spell}"
                    if spell == 'Опутывание паутиной':
                        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + "Вас опутали паутиной, вы пытаетесь выбраться и кажется вам скоро удастся"
                        self.you_skip_step_n = 2
                    elif spell == 'Защита паутиной':
                        saves[call.from_user.id]['buffer']['fight_text']['text'] += '\n' + f"{self.name} {self.skin} опутал себя паутиной в надежде защитить себя"
                        self.block += self.block_add_int
                    self.mp -= spell_mp
                    return True
        return False
