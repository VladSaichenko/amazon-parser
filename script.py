import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

with open('usersagents.txt', 'r') as f:
    useragents = f.readlines()

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,la;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': str(random.choice(useragents)).rstrip(),
}


def change_proxy():
    global valid_proxies, PROXY, PROXY_ID

    if PROXY_ID+1 >= len(valid_proxies):
        PROXY_ID = 0
        PROXY = valid_proxies[PROXY_ID]
    else:
        PROXY = valid_proxies[PROXY_ID+1]


file = input('Напишите полное название файла: ')
if file.endswith('.csv'):
    df = pd.read_csv(file)
else:
    df = pd.read_excel(file, engine="openpyxl")

with open('proxies.txt') as f:
    proxies = f.readlines()

print('Конфигурирую прокси')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
valid_proxies = []
for proxy in tqdm(proxies):
    try:
        resp = requests.get('https://developer.mozilla.org/', proxies={'http': proxy}, headers=headers)
    except Exception:
        time.sleep(5)
        continue
    if resp.status_code == 200:
        valid_proxies.append(proxy)

PROXY = valid_proxies[0]
PROXY_ID = 0
print('Начинаю анализировать ссылки.')
print('')
valid_df = pd.DataFrame(columns=df.columns)
for i in tqdm(range(len(df))):
    link = df.iloc[i][df.columns[1]]
    try:
        resp = requests.get(link, proxies={'http': proxy}, headers=HEADERS)
    except Exception:
        time.sleep(10)
        change_proxy()
        resp = requests.get(link, proxies={'http': proxy}, headers=HEADERS)
    if resp.status_code != 200 or 'captcha' in resp.text:
        change_proxy()
        resp = requests.get(link, proxies={'http': proxy}, headers=HEADERS)

    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        div = soup.find('div', class_='a-fixed-right-grid-col ie7-width-935 a-col-left')
        labels = div.find_all('label', class_='a-form-label')

        metal = length = False
        if labels:
            for label in labels:
                if 'Metal Type' in label.text.strip() or \
                  'Métal' in label.text.strip() or \
                  'Tipo di metallo' in label.text.strip():
                    metal = True
                if 'Länge' in label.text.strip() or \
                    'Longueur' in label.text.strip() or \
                    'Lunghezza' in label.text.strip():
                    length = True

        if not metal and not length:
            valid_df = valid_df.append(df.iloc[i:i+1])
    except Exception:
        continue


    time.sleep(random.randint(0, 3))

print('Скрипт успешно завершил работу.')
valid_df.to_excel('results.xlsx', index=False)
