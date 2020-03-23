"""
Created on March 19, 2020

@author: Daniel Aberer daniel.aberer@geo.tuwien.ac.at

"""

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter as savgol
from functools import reduce


def flagit(df):
    flag_c01(df)
    flag_c02(df)
    flag_c03(df)
    flag_d01(df)
    flag_d02(df)
    flag_d03(df)  # D5 included
    flag_d04(df)
    flag_d05(df)
    flag_d06(df)
    flag_d07(df)  # D8 included
    flag_d09(df)
    flag_d10(df)
    #flag_g(df)
    return df


def apply_savgol(df):
    """
    Calculates derivations 1 and 2 using Savitzky-Golay filer
    """
    df['deriv1'] = savgol(df.soil_moisture, 3, 2, 1, mode='nearest')
    df['deriv2'] = savgol(df.soil_moisture, 3, 2, 2, mode='nearest')


def check_savgol(df):
    if 'deriv1' not in df.columns or 'deriv2' not in df.columns:
        apply_savgol(df)


def flag_c01(df):
    """
    Lower Boundary - flags when measurement is below threshold
    """
    low_boundary = 0
    index = df[df.soil_moisture < low_boundary].index
    if len(index):
        df['qflag'][index].apply(lambda x: x.add(1))


def flag_c02(df):
    """
    Upper Boundary - flags when measurement is above threshold
    """
    upper_boundary = 60
    index = df[df.soil_moisture > upper_boundary].index
    if len(index):
        df['qflag'][index].apply(lambda x: x.add(2))


def flag_c03(df, hwsd=None):
    """
    HWSD Saturation Point - flags when measurment is above saturation point (at the station location)
    """
    if not hwsd:
        return

    index = df.loc[df.soil_moisture > hwsd].index
    if len(index):
        df['qflag'][index].apply(lambda x: x.add(3))


def flag_d01(df):
    """
    In situ Soil Temperature - flags when in situ soil temperature is below 0 degrees celsius

    """
    if 'soil_temperature' in df.columns:
        index = df[df.soil_temperature < 0].index
        if len(index):
            df['qflag'][index].apply(lambda x: x.add(4))


def flag_d02(df):
    """
    In situ Air Temperature - flags when in situ air temperature is below 0 degrees celsius

    """
    if 'air_temperature' in df.columns:
        index = df[df['air_temperature'] < 0].index
        if len(index):
            df['qflag'][index].apply(lambda x: x.add(5))


def flag_d03(df):
    """
    Gldas soil temperature

    """
    if 'gldas_soil_temperature' in df.columns:
        index = df[df['gldas_soil_temperature'] < 0].index
        if len(index):
            df['qflag'][index].apply(lambda x: x.add(6))


def flag_d04(df):
    """
    This flag was designed for surface soil moisture, sensors at depths greater than 10cm behave differently.

    If soil moisture shows rise without insitu precipitation event in the preceding 24h.
    through resampling nan values are added to fill gaps in the sm and p timeseries.
    this is important for the calculation of the std-dev and the rise of sm, and the sum of 24h precipitation.

    Criteria
    --------
    1. an hourly rise in sm
    2. a rise within the last 24h that is larger than twice the std-dev of sm
    3. no precipitation event greater or equal to the minimum precipitation (dependent on depth of sensor
    """

    if 'precipitation' in df.columns:
        min_precipitation = 0.2
        df['total_precipitation'] = df['precipitation'].rolling(min_periods=1, window=24).sum()

        df['std_x2'] = df['soil_moisture'].rolling(min_periods=1, window=25).std() * 2
        df['rise24h'] = df['soil_moisture'].diff(24)
        df['rise1h'] = df['soil_moisture'].diff(1)

        index = df[(df['rise1h'] > 0) & (df['rise24h'] > df['std_x2']) & 
                   (df['total_precipitation'] < min_precipitation)].index

        df['qflag'][index].apply(lambda x: x.add(7))


def flag_d05(df):
    """
    Should only be applied to surface soil moisture sensors (<= 10cm sensor depth)

    Criteria
    --------
    1. an hourly rise in sm
    2. a rise within the last 24h that is larger than twice the std-dev of sm
    3. no precipitation event greater or equal to the minimum precipitation (dependent on depth of sensor
    """
    # flag D05

    if 'gldas_precipitation' in df.columns:
        min_precipitation = 0.2

        df['gldas_total_precipitation'] = df['gldas_precipitation'].rolling(min_periods=1, window=24).sum()
        df['gl_std_x2'] = df['soil_moisture'].rolling(min_periods=1, window=25).std() * 2
        df['gl_rise24h'] = df['soil_moisture'].diff(24)
        df['gl_rise1h'] = df['soil_moisture'].diff(1)

        index = df[(df['gl_rise1h'] > 0) & (df['gl_rise24h'] > df['gl_std_x2']) &
                   (df['gldas_total_precipitation'] < min_precipitation)].index

        if len(index):
            df['qflag'][index].apply(lambda x: x.add(8))


def flag_d06(df):
    """
    Checks if time-series shows a spike.

    Criteria
    --------
    1. rise or fall of 15%
    2. ratio of second derivates of t-1 and t+1 respectively is between 0.8 and 1.2
    3. variance to mean ratio of observations (t-12 to t+12 without t) smaller than 1
    4. observation is positive or negative peak (t-1 to t+1)
    pandas internal functions such as rolling and shift are used to calculate the criteria, next the indices of the
    observations that fulfill these criteria are found (index), and the dataframe is flagged at these instances.
    5. additional criteria drop to zero with a delta of 5
    """
    check_savgol(df)

    def rolling_var(x):
        """
        returns variance of x(t-12, x+12) without the current value
        """
        x = np.delete(x, 12, axis=0)
        x = x[~np.isnan(x)]
        return ((x - x.mean()) ** 2).sum() / (len(x) - 1)

    def peak(x):
        """
        check if middle element is a positive or negative peak
        """
        if ((x[0] < x[1]) & (x[1] > x[2])) | (
                (x[0] > x[1]) & (x[1] < x[2])):  # changed to not include equal 10.7.2019
            return 1
        elif len(x) > 3:  # Added October 2019 - detect spikes that last 2 hours
            if ((x[0] < x[1]) & (x[1] == x[2]) & (x[2] > x[3])) | (
                    (x[0] > x[1]) & (x[1] == x[2]) & (x[2] < x[3])):
                return 2
        return 0

    window = np.ones(25)
    window[12] = 0  # set the center-value to zero

    df['criteria1'] = round(df['soil_moisture'].shift(-1).div(df['soil_moisture'], axis=0).shift(1), 3)
    df['criteria2'] = round(abs(
        df['deriv2'].div(df['deriv2'].shift(-2), axis=0).shift(1)), 3)
    # calculate variation coefficient without value at t:
    df['criteria3'] = abs(
        df['soil_moisture'].rolling(min_periods=25, window=25, center=True).apply(rolling_var, raw=True)).div(
        df['soil_moisture'].rolling(window=window, win_type='boxcar', center=True).mean(), axis=0)
    df['criteria4'] = df['soil_moisture'].rolling(min_periods=3, window=4, center=True).apply(peak, raw=True).shift(-1)
    df['spike_2h'] = df['criteria4'].shift(1) > 1.1

    df['spike'] = (((df['criteria1'] > 1.15) | (df['criteria1'] < 0.85)) | (df['spike_2h'] > 0)) & \
                  ((df['criteria2'] > 0.8) & (df['criteria2'] < 1.2)) & (df['criteria3'] < 1) & (df['criteria4'] > 0)

    index = df[(df.spike > 0) | ((df.spike.shift(1) > 0) & (df['spike_2h'] > 0))].index  # last expression for 2h spikes

    df['qflag'][index].apply(lambda x: x.add(9))


def flag_d07(df):
    """
    Checks if time-series shows a break.

    Criteria
    --------
    1. relative (and absolute) change in soil moisture
    2. comparison of first derivative to average of first derivatives centered at t.
    3. A negative (positive) break results in a large negative (positive) second derivative at t followed by a large
     postive (negative) value at t+1.
    4. Additional criteria not in VJZ paper: Jump from above 0.05m³/m³ to Zero
    """
    check_savgol(df)
    df['delta'] = df['soil_moisture'] - df['soil_moisture'].shift(1)  # remove abs on 16.10.2019 - like idl
    df['criteria1'] = abs(df['delta'].div(df['soil_moisture']))
    df['criteria2'] = abs(df['deriv1'].rolling(min_periods=5, window=25, center=True).mean() * 10)
    df['criteria3'] = round(abs(df['deriv2'].shift(1).div(df['deriv2'])), 1)
    df['criteria3a'] = abs(df['deriv2'].div(df['deriv2'].shift(-2)))

    # Include jumps to zero!
    df['criteria4'] = (abs(df['delta']) > 5) & (df['soil_moisture'] == 0)  # new constraint not included in vzj paper

    index = df[(df['criteria1'] > 0.1) & (abs(df['delta']) > 1) & (df['soil_moisture'] != 0) & 
               (abs(df['deriv1']) > df['criteria2']) & (df['criteria3'] == 1) & (df['deriv2'] != 0) &
               (df['criteria3a'] > 10)].index

    index_neg = index.intersection(df[df['deriv1'] < 0].index)
    index_pos = index.intersection(df[df['deriv1'] > 0].index)

    index_zero = df[df['criteria4'] > 0].index  # index where there are drops to zero
    index_neg = index_neg.append(index_zero)

    if len(index_neg):
        df['qflag'][index_neg].apply(lambda x: x.add(10))
    if len(index_pos):
        df['qflag'][index_pos].apply(lambda x: x.add(11))


def flag_d09(df):
    """
    Low Plateau

    Criteria
    --------
    1. a previous soil moisture break (D07)
    2. a period with a low coefficient of variance

    If both coincide this is an 'Event', which remains active until the var_coeff is above a threshold.
    df.event is a dataframe-column that is either 1, 0, or -1. When a soil moisture break coincides with a period
    of low var_coeff df.event = '1'. Following an 'Event' once the var_coeff is above a certain threshold
    event = '-1'. '0' means none of the above.
    results features sequences of 1 for Events and df.end extends these sequences to at least 12h periods.
    """
    df.dropna(subset=['soil_moisture'], inplace=True)

    df['var_coeff'] = round(df['soil_moisture'].rolling(min_periods=13, window=13).var().shift(-12), 4) / \
                      round(df['soil_moisture'].rolling(min_periods=13, window=13).mean().shift(-12), 4)

    nan_index = df[df['var_coeff'].isna() & (df['soil_moisture'] == 0)].index
    df.at[nan_index, 'var_coeff'] = 0.0

    # if a neg. break occurs (D07) flagged until coefficient of variation is over 0.001, +11h (D09 minimum)
    def change_filter(u, l, v):
        return reduce(lambda x, y: x + [max(min(x[-1] + y, u), l)], v, [0])[1:]

    df['event'] = ((df['qflag'].astype(str)).str.contains('10') & (df['var_coeff'] < 0.001))
    df['event'].replace(np.nan, 0, inplace=True)
    df['event'] = df['event'].astype(int)
    df.loc[(df[['var_coeff']].max(1).diff() > 0.001) & (df['event'] == 0), 'event'] = -1
    df['result'] = change_filter(1, 0, df['event'].values)
    df['end'] = df['result'].rolling(min_periods=13, window=13).max()  # flag is at least 12h + 1h

    index = df[df['end'] > 0.0].index
    if len(index):
        df['qflag'][index].apply(lambda x: x.add(12))

    df = df.resample('H').asfreq()


def flag_d10(df):
    """
    Saturated Plateau

    Criteria
    --------
    1. variance of soil moisture - values within 12h is below 0.05, as long as this is fulfilled
    a period of low variance (plv) is extending (with a min_len of 12h).
    2. at the beginning of the plv +/- 12h a rise occurs in the first derivative of at least 0.25
    3. at the end of the plv +/- 12h a drop occurs in the first derivative lower or equal to 0
    4. the mean of the soil moisture values between rise (2) and drop(3) (or if beyond plv scope, beginning and
    end of plv) are above 0.95% of the previous highest soil moisture value ever detected (highest_sm).

    """
    check_savgol(df)
    global d10group
    d10group = 0
    highest_sm = df['soil_moisture'][df['soil_moisture'] < 60].max()

    def assign_groups(x):
        global d10group
        if (x[0] == 0) & (x[1] == 1):
            d10group += 1
        if x[0] > 0:
            return d10group
        return 0

    index = []
    df.dropna(subset=['soil_moisture'], inplace=True)
    df.loc[:, 'step2'] = df['soil_moisture'].rolling(min_periods=12, window=12).var().shift(-11) <= 0.05
    df.loc[:, 'maximum'] = df['deriv1'].rolling(window=25, min_periods=1).max().shift(-12)
    df.loc[:, 'minimum'] = df['deriv1'].rolling(window=25, min_periods=1).min().shift(-24)

    df['step3'] = df['step2'].rolling(window=3).apply(assign_groups, raw=True).shift(-2)
    # head/tail because first/last value is the period of interest for rise/drop
    rise = round(df.groupby('step3')['maximum'].first(), 3)
    drop = round(df.groupby('step3')['minimum'].last(), 3)
    rise = rise[rise >= 0.25]
    drop = drop[drop < 0]

    resultdf = pd.concat([rise, drop], axis=1)[1:]
    resultdf.dropna(inplace=True)
    deriv = df['deriv1']
    for idx, row in resultdf.iterrows():
        df['step4'] = df.step3[(df.step3 == idx)]  # step 4 column is changes constantly
        box = df['step4'].rolling(window=12, min_periods=1).max() == idx  # window +1 to 12 because of IDL

        if not df.index[box & (deriv == row[0])].empty:
            emp = df.index[box & (deriv == row[0])][0]
            # max lies within VAR period
            if not df.index[box & (deriv == row[1])].empty:
                fin = df.index[box & (deriv == row[1])][0]
            else:
                fin = box[::-1].idxmax()
                # min lies outside VAR
        else:
            emp = box.idxmax()
            if not df.index[box & (deriv == row[1])].empty:
                fin = df.index[box & (deriv == row[1])][0]
            else:
                fin = box[::-1].idxmax()

        plateau = df['soil_moisture'].loc[emp:fin]
        if plateau.mean() > (highest_sm * 0.95):
            index.extend(plateau.index)

    df['qflag'][index].apply(lambda x: x.add(13))

    df =  df.resample('H').asfreq()
    

if __name__ == '__main__':
    dataframe = pd.read_pickle('df_v3.pkl')
    dataframe_flagged = flagit(dataframe)
