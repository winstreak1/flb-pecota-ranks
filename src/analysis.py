import os
import numpy as np
import pandas as pd


DATA_DIR = "/Users/linusmarco/documents/data/PECOTA"
PECOTA_FILE = "pecota_2017_03_01_86394.xls"
TEAMS = 9
ROSTER_SIZE_H = 12
ROSTER_SIZE_P = 9
CATEGORIES_H = ['OBP', 'SLG', 'HR', 'R', 'SB']


def main():
    hitters = pd.read_excel(os.path.join(DATA_DIR, PECOTA_FILE), sheetname="Hitters")
    hitters = hitters[['FIRSTNAME', 'LASTNAME'] + CATEGORIES_H]
    print('UNIVERSE: {}'.format(len(hitters)))

    hitters_top = pd.DataFrame()
    for cat in CATEGORIES_H:
        hitters_top = hitters_top.append(hitters.nlargest(ROSTER_SIZE_H*TEAMS, cat))

    hitters_top.drop_duplicates(inplace=True)
    print('TOP 200 ANY CATEGORY: {}'.format(len(hitters_top)))




if (__name__ == "__main__"):
    main()
