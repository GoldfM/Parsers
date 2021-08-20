import requests
from bs4 import BeautifulSoup as bs
import sqlite3



HEADERS ={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
          'accept':'*/*'}
INDEX='https://www.marathonbet.ru/su/popular/e-Sports'
def get_html(url):
    req = requests.get(url, headers=HEADERS,params=None)
    return req
INDEX = 'https://www.marathonbet.ru/su/popular/e-Sports/'
conn = sqlite3.connect('bets.db')
cur = conn.cursor()


def null_bd(bd):
    for bet_id in cur.execute(f'''SELECT id FROM {bd}''').fetchall():
        cur.execute(f"""update {bd} set test=0 where id = ?""",(bet_id[0],))
    conn.commit()



def parse(html,bd):
    null_bd(bd)
    soup=bs(html,'html.parser')
    matches=soup.find_all('div',class_='bg coupon-row')
    for match in matches:
        commands=match.find_all('a',class_='member-link')
        a,b = commands[0].text.strip(), commands[1].text.strip()
        koefs = match.find_all('span', class_='selection-link active-selection')
        k_a = koefs[0].text.strip()
        k_b = koefs[1].text.strip()
        try:
            cur.execute(f"""select id from {bd.strip()} where command1 = ? and command2 = ?""",(a,b))
            id = cur.fetchone()
            id=id[0]
            cur.execute(f"""update {bd.strip()} set koef1=?, koef2=?,test=1 where id = ?""",(k_a,k_b,id))
            conn.commit()
            print(f'[INFO] Строка с id: {id} обновлена')
        except TypeError:
            cur.execute(f"""INSERT INTO {bd} (command1, command2, koef1, koef2, test) VALUES (?, ?, ?, ?, 1);""", (a, b, k_a, k_b))
            conn.commit()
            print('Добавлена новая строка')
    for bet in cur.execute(f'''SELECT test,id FROM {bd}''').fetchall():
        check,id=bet
        if check==0:
            cur.execute(f"""DELETE from {bd} where id = ?""", (id,))
            print(f'[OLD BET] Строка с id: {id} удалена из БД {bd}')



def parse_marafon(game):

    if game=='Dota':
        URL = INDEX+'Dota+2'
        bd = 'dota_bet'
    elif game=='LoL':
        URL = INDEX+'LoL'
        bd = 'lol_bet'
    elif game=='CS GO':
        URL=INDEX+'CS%3AGO'
        bd = 'cs_bet'
    elif game=='COD':
        URL = INDEX +'Call+of+Duty'
        bd = 'cod_bet'
    elif game=='Overwatch':
        URL = INDEX + 'Overwatch'
        bd = 'overwatch_bet'
    elif game=='Starcraft':
        URL = INDEX + 'Starcraft+2'
        bd = 'starcraft_bet'
    elif game=='Valorant':
        URL = INDEX + 'Valorant'
        bd='valorant_bet'
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {bd}(
        id INTEGER PRIMARY KEY,
        command1 TEXT,
        command2 TEXT,
        koef1 TEXT,
        koef2 TEXT,
        test BOOLEAN);
    """)
    conn.commit()
    html = get_html(URL)
    print('')
    print(f'-----{bd}-----')
    if html.status_code==200:
        parse(html.text,bd)
    else:
        print('Error with website')
for game in ('Dota','LoL','CS GO','Overwatch','Starcraft','Valorant'):
    parse_marafon(game)
