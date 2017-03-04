import os
import numpy as np
import pandas as pd


DATA_DIR = "/Users/linusmarco/documents/data/PECOTA"
PECOTA_FILE = "pecota_2017_03_01_86394.xls"
TEAMS = 9
ROSTER_SIZE_H = 12
ROSTER_SIZE_P = 9
CATEGORIES_H = ['OBP', 'SLG', 'HR', 'R', 'SB']


def calc_zscores(col):
    mean = col.mean()
    std = col.std(ddof=0)
    z = (col - mean)/std
    return z


def main():
    hitters = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Hitters")
    hitters = hitters[['FIRSTNAME', 'LASTNAME', 'POS'] + CATEGORIES_H]
    print('UNIVERSE: {}'.format(len(hitters)))

    hitters_top = pd.DataFrame()
    for cat in CATEGORIES_H:
        hitters_top = hitters_top.append(hitters.nlargest(int(ROSTER_SIZE_H*TEAMS), cat))

    hitters_top.drop_duplicates(inplace=True)
    print('TOP ANY CATEGORY: {}'.format(len(hitters_top)))

    z_cols = [x + '_zscore' for x in CATEGORIES_H]
    hitters_top[z_cols] = hitters_top[CATEGORIES_H].apply(calc_zscores)
    hitters_top['all_zscore'] = hitters_top[z_cols].sum(axis=1)
    hitters_top.sort_values(by='all_zscore', ascending=False, inplace=True)
    hitters_top.reset_index(drop=True, inplace=True)
    hitters_top['rank'] = hitters_top.index + 1

    hitters_top.to_csv(os.path.join(DATA_DIR, "hitters_top.csv"))

    print(hitters_top.head(50))


if (__name__ == "__main__"):
    main()
