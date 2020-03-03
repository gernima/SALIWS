import requests
from bs4 import BeautifulSoup as bs


def read_login_password(message):
    login = ''
    with open('edu.txt', 'r') as file:
        data = file.read()
        a = data.split('\n')
        for i in a:
            x = i.split(':')
            if x[0] == str(message.chat.id):
                login = x[1].split(' ')[0]
                password = x[1].split(' ')[1]
        # if len(login):
        #     bot.send_message(message.chat.id, 'Сперва авторизируйтесь', reply_markup=keyboard)
    return login, password


def write_login_password(message, bot, keyboard):
    if ' ' in message.text:
        with open('edu.txt', 'r+') as f:
            data = f.read().strip().split('\n')
            for i in range(len(data)):
                if data[i].split(':')[0] == str(message.chat.id):
                    data[i] = ''
        data = [x.replace('\n', '') for x in data]
        with open('edu.txt', 'w') as f:
            f.write(
                '\n'.join(data).strip() + '\n' + str(message.chat.id) + ':' + str(
                    message.text.split(' ')[0]) + ' ' + str(
                    message.text.split()[1]))

        bot.send_message(message.chat.id, 'Вы успешно авторизовались', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Логин и пароль нужно писать через пробел', reply_markup=keyboard)


def click_hm(message, bot, keyboard):
    # try:
    login, password = read_login_password(message)
    table = parsing(login, password)
    s = []
    for key, val in table.items():
        s.append(key + ': ' + ' '.join(val))
    bot.send_message(message.chat.id, s, reply_markup=keyboard)
    # print(s)


# except:
#    bot.send_message(message.chat.id, 'Проверьте логин и пароль', reply_markup=keyboard)


def login_with_requests(session, login, password):
    payload = {'main_login': login, 'main_password': password}
    url = 'https://edu.tatar.ru/logon'
    headers = {'Referer': url}
    responce = session.post(url,
                            data=payload,
                            headers=headers)


def parsing(login, password):
    s = requests.Session()
    s.proxies = {'http': '62.32.90.99:8080', 'http': '195.191.250.38:3128'}
    login_with_requests(s, login, password)
    res = s.get('https://edu.tatar.ru/user/diary/term')
    html = res.text
    soup = bs(html, 'html.parser')
    table = soup.find('tbody')
    subjects = table.find_all('tr')
    tds = []
    for x in subjects:
        tds.append(list(z.text for z in x.find_all('td') if z.text)[:-2])
    res = {}
    for td in tds:
        if td:
            res[td[0]] = td[1:]
    return res


