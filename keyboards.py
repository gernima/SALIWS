from telebot import types


choice_mode_keyboard = types.InlineKeyboardMarkup()  # перед началом игры, после /start
choice_mode_keyboard.add(types.InlineKeyboardButton('Одиночная игра', callback_data='mode_single'))
# choice_mode_keyboard.add(types.InlineKeyboardButton('Сетевая игра (В идеи)', callback_data='mode_multiplayer'))


def get_move_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('📚', callback_data=f'move_chars'),
                 types.InlineKeyboardButton('⬆', callback_data=f'move_up'),
                 types.InlineKeyboardButton('💼', callback_data=f'move_inventory'))
    keyboard.add(types.InlineKeyboardButton('⬅', callback_data=f'move_left'),
                 types.InlineKeyboardButton('⬇', callback_data=f'move_down'),
                 types.InlineKeyboardButton('➡', callback_data=f'move_right'))
    keyboard.add(types.InlineKeyboardButton('Главное меню', callback_data=f'move_main_menu'))
    return keyboard


def get_fight_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Атака', callback_data=f'fight_attack'),
                 types.InlineKeyboardButton('Уклонение', callback_data=f'fight_dodge'),
                 types.InlineKeyboardButton('Блок', callback_data=f'fight_block'))
    keyboard.add(types.InlineKeyboardButton("Способности", callback_data=f'fight_spells'),
                 types.InlineKeyboardButton('Инвентарь', callback_data=f'fight_inv'),
                 types.InlineKeyboardButton('Сбежать', callback_data=f'fight_away'))
    return keyboard


def get_librarian_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"librarian_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин способностей", callback_data=f"librarian_spells_shop"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data=f"librarian_talk_bye"))
    return keyboard


def get_librarian_spells_shop_keyboard(spell):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"librarian_{spell}_spells_shop_yes"),
                 types.InlineKeyboardButton(text="Нет", callback_data=f"librarian_{spell}_spells_shop_no"))
    return keyboard


def get_return_to_inventory():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"inventory_return"))
    return keyboard


def get_sewer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Здравствуйте", callback_data=f"sewer_talk_hi"))
    keyboard.add(types.InlineKeyboardButton(text="Магазин скинов", callback_data=f"sewer_skins_shop"))
    keyboard.add(types.InlineKeyboardButton(text="Сбор паутины", callback_data=f"sewer_quest_spider_web"))
    keyboard.add(types.InlineKeyboardButton(text="До свидания", callback_data=f"sewer_talk_bye"))
    return keyboard


def get_sewer_skins_shop_yes_or_no_keyboard(skin):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"sewer_{skin}_skins_shop_yes"),
                 types.InlineKeyboardButton(text="Нет", callback_data=f"sewer_{skin}_skins_shop_no"))
    return keyboard


def get_quest_keyboard(quest):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"quest_{quest}_yes"),
                 types.InlineKeyboardButton(text="Нет", callback_data=f"quest_{quest}_no"))
    return keyboard

