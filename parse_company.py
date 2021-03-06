import requests
from bs4 import BeautifulSoup as bs
import sqlite3


URL='https://smolensk.jsprav.ru/'
HEADERS ={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
          'accept':'*/*'}
INDEX='https://smolensk.jsprav.ru'
def get_html(url,params=None):
    req = requests.get(url, headers=HEADERS,params=params)
    return req




list_db=[]
def get_content(html):
    list_href = []
    soup=bs(html,'html.parser')
    items=soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-6 col-lg-4')
    for item in items:
        a = item.find('a',class_='').attrs['href']
        list_href.append(a)
    return list_href

def get_content_2(html):
    list_href2=[]
    soup=bs(html,'html.parser')
    items=soup.find_all('div',class_='cat-item')
    for item in items:
        a = item.find('a',class_='').attrs['href']
        list_href2.append(a)
    return list_href2

def get_content_3(html,url_cur,check):
    global list_db
    soup=bs(html,'html.parser')
    items=soup.find_all('div',class_='org')

    for item in items:
        address = 'Не указано'
        time_work='Не указано'
        name = item.find('a',class_='lnk')
        url = INDEX + name.attrs['href']
        name = name.text

        try:
            address= item.find('span', class_='address').text
        except:
            pass
        try:
            time_work = item.find('span', class_='time').text
        except:
            pass
        #print(f'{name } ---- {url} ---- {address} --- {time_work}')
        list_db.append([name, time_work, address, url])
    if check==1:
        page_bar = soup.find('ul', class_='pagination')
        page_max = 1
        if page_bar != None:
            page_list = [int(a.text) for a in page_bar.find_all('a')]
            page_max = max(page_list)
        #print('\n---',page_max,'---\n')
        if page_max!=1:
            for page in range(2,page_max+1):
                html_cur=get_html(url=url_cur,params={'p':page})
                get_content_3(html_cur.text,url_cur,0)
    #print(url_cur)




def parse_company():
    global list_db
    html = get_html(URL)
    if html.status_code==200:
        hrefs = get_content(html.text)
        for href in hrefs:
            html2 = get_html(INDEX+href)
            hrefs2 = get_content_2(html2.text)
            for href2 in hrefs2:
                html3=get_html((INDEX + href2))
                get_content_3(html3.text,INDEX + href2,1)
    else:
        print('Error with website')
    conn = sqlite3.connect('company_smolensk.db')
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM company;', )
    except:
        cur.execute("""CREATE TABLE IF NOT EXISTS company(
                id INTEGER PRIMARY KEY,
                name TEXT,
                time TEXT,
                address TEXT,
                site TEXT);
                """)
    cur.executemany("""INSERT INTO company (name, time, address, site) VALUES (?, ?, ?, ?);""", list_db)
    conn.commit()


if __name__ == "__main__":
    parse_company()