import telebot


def is_alive(call, saves):
    if saves[call.from_user.id]['hp'] <= 0:
        return True
    return False


