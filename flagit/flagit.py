'''
Created on March 19, 2020

@author: Daniel Aberer daniel.aberer@geo.tuwien.ac.at

'''

import pandas as pd




def flagit(df):
    run_C01(df)
    # run_C02(df)
    # run_C03(df)
    # run_D01(df)
    # run_D02(df)
    # run_D03(df)  # D5 included
    # run_D04(df)
    # run_D06(df)
    # run_D07(df)  # D8 included
    # run_D09(df)
    # run_D10(df)
    # run_G(df)
    return df

def run_C01(df):
    """
    Lower Boundary - flags when measurement is below threshold
    """

    low_boundary = 0

    index = df[df.value < low_boundary].index
    if len(index):
        df.qflag[index].apply(lambda x: x.add(1))



df = pd.read_pickle('dummy_timeseries.pkl')
df = flagit(df)