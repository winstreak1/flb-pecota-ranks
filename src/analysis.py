import os
import numpy as np
import pandas as pd


DATA_DIR = "/Users/linusmarco/documents/data/PECOTA"
PECOTA_FILE = "pecota_2017_03_01_86394.xls"
TEAMS = 9
ROSTER_SIZE_H = 12
ROSTER_SIZE_P = 9
CATEGORIES_H = ['OBP', 'SLG', 'HR', 'R', 'SB']
CATEGORIES_P = ['ERA', 'WHIP', 'QS', 'SO', 'SV']


def calc_zscores(col):
    mean = col.mean()
    std = col.std(ddof=0)
    z = (col - mean)/std
    return z


def rank(players, categories, rosternum, wt_cats=None, wt_col=None, bypos=False):
    if bypos:
        id_cols = ['FIRSTNAME', 'LASTNAME', 'POS']
    else:
        id_cols = ['FIRSTNAME', 'LASTNAME']

    if (wt_col != None):
        id_cols.append(wt_col)

    df = players.copy()[id_cols + categories]

    top = pd.DataFrame()
    for cat in categories:
        top = top.append(df.nlargest(rosternum, cat))
    top.drop_duplicates(inplace=True)

    z_cols = [x + '_zscore' for x in categories]
    if bypos:
        top[z_cols] = top.groupby('POS')[categories].apply(calc_zscores)
    else:
        top[z_cols] = top[categories].apply(calc_zscores)

    if (wt_cats != None and wt_col != None):
        wt_z_cols = [x + '_zscore' for x in wt_cats]
        top[wt_z_cols] = top[wt_z_cols].apply(lambda x: x * top[wt_col])

    top['all_zscore'] = top[z_cols].sum(axis=1)
    top.sort_values(by='all_zscore', ascending=False, inplace=True)
    top.reset_index(drop=True, inplace=True)
    top['rank'] = top.index + 1

    print(top.head(50))
    return top


def main():
    # hitters = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Hitters")
    # hitters['POS'].replace(to_replace=['LF', 'CF', 'RF'], value='OF', inplace=True)
    # hitters_top = rank(hitters, CATEGORIES_H, ROSTER_SIZE_H*TEAMS, bypos=True)
    # hitters_top.to_csv(os.path.join(DATA_DIR, "hitters.csv"))

    pitchers = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Pitchers")
    pitchers[['ERA', 'WHIP']] = pitchers[['ERA', 'WHIP']].multiply(-1)
    pitchers_top = rank(pitchers, CATEGORIES_P, ROSTER_SIZE_P*TEAMS, wt_cats=['ERA', 'WHIP'], wt_col='IP', bypos=False)
    pitchers_top[['ERA', 'WHIP']] = pitchers_top[['ERA', 'WHIP']].multiply(-1)
    pitchers_top.to_csv(os.path.join(DATA_DIR, "pitchers.csv"))


if (__name__ == "__main__"):
    main()
