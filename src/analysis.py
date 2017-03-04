import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


DATA_DIR = "/Users/linusmarco/documents/data/PECOTA"
PECOTA_FILE = "pecota_2017_03_01_86394.xls"
TEAMS = 9
ROSTER_SIZE_H = 12
ROSTER_SIZE_P = 9
CATEGORIES_H = [
    {'name': 'OBP', 'weight': 'PA' },
    {'name': 'SLG', 'weight': 'AB' },
    {'name': 'HR', 'weight': None },
    {'name': 'R', 'weight': None },
    {'name': 'SB', 'weight': None }
]
CATEGORIES_P = [
    {'name': 'ERA', 'weight': 'IP' },
    {'name': 'WHIP', 'weight': 'IP' },
    {'name': 'QS', 'weight': None },
    {'name': 'SO', 'weight': None },
    {'name': 'SV', 'weight': None }
]


def calc_zscores(col):
    mean = col.mean()
    std = col.std(ddof=0)
    z = (col - mean)/std
    return z


def weight_column(col, wt_col):
    mean = col.mean()
    weighted = (col - mean)*wt_col
    return weighted


def rank(players, categories, rosternum, bypos=False):
    df = players.copy()

    id_cols = ['FIRSTNAME', 'LASTNAME']
    if bypos:
        id_cols.append('POS')

    # set up and weight columns for analysis
    raw_cols = []
    val_cols = []
    wt_cols = []
    for cat in categories:
        raw_cols.append(cat['name'])
        if (cat['weight'] != None):
            df[cat['name'] + '_WT'] = weight_column(df[cat['name']], df[cat['weight']])
            val_cols.append(cat['name'] + '_WT')
            if (cat['weight'] not in wt_cols):
                wt_cols.append(cat['weight'])
        else:
            val_cols.append(cat['name'])

    # limit player universe
    top = pd.DataFrame()
    for cat in categories:
        if (cat['weight'] == None):
            largest = df.nlargest(rosternum, cat['name'])
        else:
            largest = df.nlargest(rosternum, cat['name'] + '_WT')
        top = top.append(largest)

    top.drop_duplicates(inplace=True)

    # calculate z scores for each category
    z_cols = [c + '_zscore' for c in raw_cols]
    if bypos:
        top[z_cols] = top.groupby('POS')[val_cols].apply(calc_zscores)
    else:
        top[z_cols] = top[val_cols].apply(calc_zscores)

    # rank by sum of z scores
    top['all_zscore'] = top[z_cols].sum(axis=1)
    top.sort_values(by='all_zscore', ascending=False, inplace=True)
    top.reset_index(drop=True, inplace=True)
    top['rank'] = top.index + 1

    # organize columns
    cols = ['rank', 'all_zscore']
    cols = cols + id_cols + wt_cols
    for c in categories:
        cols.append(c['name'])
        cols.append(c['name'] + '_zscore')

    top = top[cols]

    print(top.head(50))
    return top


def combine_ranks(hitters, pitchers):
    cols = list(hitters.columns.values) + [c for c in pitchers.columns.values if c not in hitters.columns.values]
    top = hitters.append(pitchers)
    top.sort_values(by='all_zscore', ascending=False, inplace=True)
    top.reset_index(drop=True, inplace=True)
    top['rank'] = top.index + 1
    top = top[cols]
    print(top.head(50))
    return top


def main():
    hitters = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Hitters")
    hitters['POS'].replace(to_replace=['LF', 'CF', 'RF'], value='OF', inplace=True)
    hitters_top = rank(hitters, CATEGORIES_H, ROSTER_SIZE_H*TEAMS, bypos=True)
    hitters_top.to_csv(os.path.join(DATA_DIR, "hitters.csv"), index=False)

    pitchers = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Pitchers")
    pitchers[['ERA', 'WHIP']] = pitchers[['ERA', 'WHIP']].multiply(-1)
    pitchers_top = rank(pitchers, CATEGORIES_P, ROSTER_SIZE_P*TEAMS, bypos=False)
    pitchers_top[['ERA', 'WHIP']] = pitchers_top[['ERA', 'WHIP']].multiply(-1)
    pitchers_top.to_csv(os.path.join(DATA_DIR, "pitchers.csv"), index=False)

    pitchers_top['POS'] = 'P'
    players_top = combine_ranks(hitters_top, pitchers_top)
    players_top.to_csv(os.path.join(DATA_DIR, "players.csv"), index=False)


if (__name__ == "__main__"):
    main()
