from bs4 import BeautifulSoup
import requests

from argparse import ArgumentParser
import pandas as pd
import time

import config
from preprocessing.preprocessing import preprocessing

def num_page(place):
    url = config.URL[place]
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, "lxml")
    body = soup.find("body")
    pages = body.find_all("div", {'class': 'pagination pagination_set-nav'})
    pages_text = str(pages)
    pages_split = pages_text.split('</a></li>\n</ol>')
    pages_split0 = pages_split[0]
    pages_split1 = pages_split0[-3:]
    pages_split2 = pages_split1.replace('">', '')
    pages_split3 = int(pages_split2)

    urls = []
    urls.append(url)
    for i in range(pages_split3 - 1):
        pg = str(i + 2)
        url_page = url + '&pn=' + pg
        urls.append(url_page)
    return urls

def crawler(opt):
    name = []
    address = []
    locations0 = []
    locations1 = []
    locations2 = []
    ages = []
    levels = []
    floors = []
    rents = []
    admins = []
    deposits = []
    gratuites = []
    madoris = []
    mensekis = []
    links = []
    urls = num_page(opt.place)

    for i, url in enumerate(urls):
        print(f'start page:{i+1}')
        result = requests.get(url)
        c = result.content
        soup = BeautifulSoup(c, "lxml")
        summary = soup.find("div", {'id': 'js-bukkenList'})

        num = []
        num_content = summary.find_all('table', {'class': 'cassetteitem_other'})
        for content in num_content:
            data = content.find_all('tbody')
            num_data = len(data)
            num.append(num_data)

        # 物件名
        name_list = summary.find_all('div', {'class': 'cassetteitem_content-title'})
        for n, content in zip(num, name_list):
            data = str(content).split(">")[1]
            data = data.split('<')[0]
            for i in range(n):
                name.append(data)

        # 住所
        address_list = summary.find_all('li', {'class': 'cassetteitem_detail-col1'})
        for n, content in zip(num, address_list):
            data = str(content).split('>')[1]
            data = data.split('<')[0]
            for i in range(n):
                address.append(data)

        # 上位3つの最寄駅
        location_list = summary.find_all('li', {'class': 'cassetteitem_detail-col2'})
        for n, locatiton in zip(num, location_list):
            cols = locatiton.find_all('div')
            for i in range(len(cols)):
                text = cols[i].getText()
                for c in range(n):
                    if i == 0:
                        locations0.append(text)
                    elif i == 1:
                        locations1.append(text)
                    elif i == 2:
                        locations2.append(text)

        # 築年数, 階層
        age_list = summary.find_all('li', {'class': 'cassetteitem_detail-col3'})
        for n, content in zip(num, age_list):
            age, level = content.find_all('div')
            age = str(age).replace('<div>', '').replace('</div>', '')
            level = str(level).replace('<div>', '').replace('</div>', '')
            for i in range(n):
                ages.append(age)
                levels.append(level)

        # 階数, 家賃, 管理費, 敷金, 礼金, 間取り, 専有面積
        base_info = summary.find_all('table', {'class': 'cassetteitem_other'})
        for info in base_info:
            floor = info.find_all('tr', {'class': 'js-cassette_link'})
            rent = info.find_all('span', {'class': 'cassetteitem_other-emphasis ui-text--bold'})
            admin = info.find_all('span', {'class': 'cassetteitem_price cassetteitem_price--administration'})
            deposit = info.find_all('span', {'cassetteitem_price cassetteitem_price--deposit'})
            gratuity = info.find_all('span', {'cassetteitem_price cassetteitem_price--gratuity'})
            madori = info.find_all('span', {'class': 'cassetteitem_madori'})
            menseki = info.find_all('span', {'class': 'cassetteitem_menseki'})
            for f, r, a, d, g, m, me in zip(floor, rent, admin, deposit, gratuity, madori, menseki):
                floors.append(f.getText()[23:26])
                rents.append(str(r).split('>')[1].split('<')[0])
                admins.append(str(a).split('>')[1].split('<')[0])
                deposits.append(str(d).split('>')[1].split('<')[0])
                gratuites.append(str(g).split('>')[1].split('<')[0])
                madoris.append(str(m).split('>')[1].split('<')[0])
                mensekis.append(str(me).split('>')[1].split('<')[0])

        details = summary.find_all('a', {'class': 'js-cassette_link_href cassetteitem_other-linktext'})
        for d in details:
            detail = d.get('href')
            full_link = 'https://suumo.jp' + detail
            links.append(full_link)

        time.sleep(10)

    print('scraping fin!')

    name = pd.Series(name)
    address = pd.Series(address)
    location0 = pd.Series(locations0)
    location1 = pd.Series(locations1)
    location2 = pd.Series(locations2)
    ages = pd.Series(ages)
    levels = pd.Series(levels)
    floors = pd.Series(floors)
    rents = pd.Series(rents)
    admins = pd.Series(admins)
    deposits = pd.Series(deposits)
    gratuites = pd.Series(gratuites)
    madoris = pd.Series(madoris)
    mensekis = pd.Series(mensekis)
    links = pd.Series(links)

    suumo_df = pd.concat([name, address, location0, location1, location2, ages, levels, floors, \
                          rents, admins, deposits, gratuites, madoris, mensekis, links], axis=1)
    suumo_df.columns = ['マンション名', '住所', '立地1', '立地2', '立地3', '築年数', '全層', '階層', \
                        '家賃', '管理費', '敷金', '礼金', '間取り', '専有面積', '詳細ページ']

    suumo_df.to_csv(f'{opt.output}/suumo_{opt.file_name}.csv', encoding='utf-16')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--place', type=str, required=True, help='検索したい地域(ex:荻窪)')
    argparser.add_argument('--file_name', type=str, required=True, help='出力時のファイル名')
    argparser.add_argument('--output', type=str, default='./csv', help='csvファイル吐き出し先')
    opt = argparser.parse_args()
    crawler(opt)
    data = pd.read_csv(f'{opt.output}/suumo_{opt.file_name}.csv', encoding='utf-16', index_col=0)
    data = preprocessing(data)
    data.to_csv(f'./processing_{opt.file_name}.csv')