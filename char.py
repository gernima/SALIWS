BASIC_CHARS = {'dodge': 5}


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
