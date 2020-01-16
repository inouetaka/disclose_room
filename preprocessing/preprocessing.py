import numpy as np
import pandas as pd

def station_walk(data):
    places = ['立地1', '立地2', '立地3']
    stations = ['路線/駅1', '路線/駅2', '路線/駅3']
    walks = ['徒歩1', '徒歩2', '徒歩3']

    for p, s, w in zip(places, stations, walks):
        station = data[p].str.split('歩', expand=True)
        station.columns = [s, w]
        station[s] = station[s].fillna(-1)
        station[w] = station[w].str.replace('分', '').fillna(-1)
        data = pd.concat([data, station], axis=1)
        for i, l in enumerate(data[s]):
            if 'バス' in str(l):
                data.loc[i, s] = -1
        location_dummy = pd.get_dummies(data[s], prefix=s, drop_first=True)
        data = pd.concat([data, location_dummy], axis=1)

    data.drop(places + stations, axis=1, inplace=True)
    return data

def madori(data):
    madori = ['DK', 'L', 'S', 'K', 'ワンルーム']
    data['間取りDK'] = 0
    data['間取りL'] = 0
    data['間取りS'] = 0
    data['間取りK'] = 0
    data['間取りワンルーム'] = 0

    for i, d in enumerate(data['間取り']):
        for m in madori:
            if m in d:
                data.loc[i, f'間取り{m}'] = 1
                if m is 'ワンルーム':
                    data.loc[i, '間取り'] = data.loc[i, '間取り'].replace(m, '1')
                else:
                    data.loc[i, '間取り'] = data.loc[i, '間取り'].replace(m, '')
    return data

def undergraund(data):
    data['全層'] = data['全層'].str.replace('階建', '')
    # 地下は2桁ないことを前提に決め打ち
    for i, z in enumerate(data['全層']):
        if '地下' in z:
            data.loc[i, '全層'] = data.loc[i, '全層'][3:].replace('地上', '')
    return data


def simple_pre(data):
    data['築年数'] = data['築年数'].replace('新築', '0')
    data['築年数'] = data['築年数'].str.replace('築', '').str.replace('年', '')
    data['階層'] = data['階層'].str.replace('\t', '').replace('2-', '2').replace('1-', '1').replace('-\n', '0').replace('B1', '-1')
    data['階層'] = data['階層'].str.replace('階', '')
    data['家賃'] = data['家賃'].str.replace('万円', '')
    data['管理費'] = data['管理費'].str.replace('円', '').replace('-', 0).astype(np.float32)
    data['管理費'] = data['管理費'].div(1e4)
    data['敷金'] = data['敷金'].str.replace('万円', '').replace('-', 0)
    data['礼金'] = data['礼金'].str.replace('万円', '').replace('-', 0)
    data['専有面積'] = data['専有面積'].str.replace('m', '')
    return data

def preprocessing(data):
    df = station_walk(data)
    df = madori(df)
    df = undergraund(df)
    df = simple_pre(df)
    return df
