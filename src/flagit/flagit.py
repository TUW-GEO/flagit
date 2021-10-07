# The MIT License (MIT)
#
# Copyright (c) 2020 TU Wien
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter as savgol
from functools import reduce
import warnings
from flagit.settings import Variables


class FormatError(Exception):
    pass


t = Variables()


class Interface(object):
    """
    class provides interface to apply ISMN quality control procedures to in situ soil moisture data.

    upon initialization it checks if the provided DataFrame has the required format. Quality control procedures can then
    be applied using the Interface.run function. The flags are provided as additional tags in column "qflag" which is
    one of three main categories: C (exceeding plausible geophysical range), D (questionable/dubious) or G (good).
    For a detailed description of the algorithms please see: Dorigo, W. A., Xaver, A., Vreugdenhil, M., Gruber, A.,
    Hegyiova, A., Sanchis-Dufau, A. D., ... & Drusch, M. (2013). Global automated quality control of in situ soil
    moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12(3), doi:10.2136/vzj2012.0097.
    
    If variable is not soil moisture but one of the following list: 
    [soil temperature, air temperature, precipitation, soil suction, snow water equivalent, snow depth, 
    soil surface temperature] then for the ISMN quality control only threshold flags (c01 and c02) are applied.
    
    It is required that the first column of the dataframe is equal to the name of the variable.   

    Parameters
    ----------
    data : pandas.DataFrame
        Input for Interface Object containing in situ soil moisture measurements
    sat_point : float
            Saturation Point for soil at the respective location.
            At ISMN the saturation point is calculated from Harmonized World Soil Database (HWSD) sand, clay and organic
            content for each station using Equations [2,3,5] from Saxton & Rawls (2006).
            (Saxton, K. E., & Rawls, W. J. (2006). Soil water characteristic estimates by texture and organic matter for
            hydrologic solutions. Soil science society of America Journal, 70(5), 1569-1578. doi:10.2136/sssaj2005.0117)

    Raises
    ------
    FormatError
        if provided Input is no DataFrame or does not meet the required format

    Attributes
    ----------
    data : pandas.DataFrame
        DataFrame containing in situ soil moisture measurement

    Methods
    -------
    run(name,sat_point)
        Apply ISMN quality control to in situ soil moisture measurements

    """

    def __init__(self, data, sat_point=None, depth_from = None):
        self.data = data
        self.sat_point = sat_point
        self.depth_from = depth_from
        self.variable = None

        if not type(self.data) == pd.DataFrame:
            raise FormatError('Please provide pandas.DataFrame as data.')

        if 'soil_moisture' not in self.data.columns:
            self.variable = self.data.keys()[0]
            self.data['qflag'] = data[self.variable].apply(lambda x: set())
        
        else:
            self.data['qflag'] = data.soil_moisture.apply(lambda x: set())
            self.variable = 'soil_moisture'


    def run(self, name=None, sat_point=None, depth_from=None, flag_numbers=False) -> pd.DataFrame:
        """
        Applies all quality control algorithms when keyword name is not set. However for flag C03 a threshold value
        (saturation point: highest soil moisture value depending on soil properties) is needed as input.

        Parameters
        ----------
        name : string or list, optional
            provide name of flag or list of flags to only apply these flags
        sat_point : float
                Saturation Point for soil at the respective location.
                At ISMN the saturation point is calculated from Harmonized World Soil Database (HWSD) sand, clay
                and organic content for each station using Equations [2,3,5] from Saxton & Rawls (2006).
                (Saxton, K. E., & Rawls, W. J. (2006). Soil water characteristic estimates by texture and organic matter
                for hydrologic solutions. Soil science society of America Journal, 70(5), 1569-1578.)
        depth_from : Decimal
                Used to calculate minimum precipitation necessary to consitute a rain event for flags D04 and D05.
                Also used to skip sensor depths >=10cm for D04 and D05 (applied to surface soil moisture sensors only).
        flag_numbers : bool
                if true flag numbers are used as tags in the qflag column instead of flag ids (e.g.: '1' instead of
                'C01', '14' instead of 'G')

        Returns
        -------
        pandas.DataFrame
            DataFrame including ISMN quality flags in column "qflag".
        """
        keys = self.data.keys()
        if not self.sat_point:
            self.sat_point = sat_point
        if not self.depth_from:
            self.depth_from = depth_from
        if self.variable == 'soil_moisture':
            self.apply_savgol()
        if not flag_numbers:
            flags_dict = {'C01': self.flag_C01, 'C02': self.flag_C02, 'C03': self.flag_C03, 'D01': self.flag_D01,
                      'D02': self.flag_D02, 'D03': self.flag_D03, 'D04': self.flag_D04, 'D05': self.flag_D05,
                      'D06': self.flag_D06, 'D07': self.flag_D07, 'D09': self.flag_D09, 'D10': self.flag_D10,
                      'G': self.flag_G}
        else:
            flags_dict = {1: self.flag_C01, 2: self.flag_C02, 3: self.flag_C03, 4: self.flag_D01,
                          5: self.flag_D02, 6: self.flag_D03, 7: self.flag_D04, 8: self.flag_D05,
                          9: self.flag_D06, 10: self.flag_D07, 12: self.flag_D09, 13: self.flag_D10,
                          14: self.flag_G}


        if name is not None:
            if type(name) == list:
                for key in name:
                    flags_dict[key](key)
            elif type(name) == str:
                flags_dict[name](name)
        else:
            for key in flags_dict.keys():
                flags_dict[key](key)

        return self.data[keys]


    def get_flag_description(self) -> None:
        """
        Prints out table with flag codes and a short description.
        """
        names = ['C01','C02','C03','D01','D02','D03','D04','D05','D06','D07','D08','D09','D10', 'G']
        description = ['soil moisture < 0 m³ / m³', 'soil moisture > 0.60m³ / m³',
                        'soil moisture > saturation point(based on HWSD)', 'negative soil temperature( in situ)',
                        'negative air temperature( in situ)', 'negative soil temperature (GLDAS)',
                        'rise in soil moisture without precipitation( in situ)',
                        'rise in soil moisture without precipitation(GLDAS)',
                        'spikes', 'negative breaks(drops)', 'positive breaks(jumps)',
                        'constant values following negative break', 'saturated plateaus', 'good']

        titles = ['code', 'description']
        table_create = [titles] + list(zip(names, description))

        for i, d in enumerate(table_create):
            line = ' | '.join(str(x).ljust(4) for x in d)
            print(line)
            if i == 0:
                print('-' * len(line))


    def apply_savgol(self) -> None:
        """
        Calculates and adds derivations 1 and 2 using Savitzky-Golay filter
        """
        self.data['deriv1'] = savgol(self.data.soil_moisture, 3, 2, 1, mode='nearest')
        self.data['deriv2'] = savgol(self.data.soil_moisture, 3, 2, 2, mode='nearest')

    def flag_C01(self, tag):
        """
        Soil moisture below threshold:
        Flags when measurement is below threshold

        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        low_boundary = t.low_boundary(self.variable)

        index = self.data[self.data[self.variable] < low_boundary].index
            
        if len(index):
            self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_C02(self, tag):
        """
        Soil moisture above threshold:
        Flags when measurement is above threshold

        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        upper_boundary = t.hi_boundary(self.variable)
        index = self.data[self.data[self.variable] > upper_boundary].index
        if len(index):
            self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_C03(self, tag):
        """
        Soil moisture above saturation point:
        Flags when soil moisture is above saturation point.
        At ISMN the saturation point is calculated from Harmonized World Soil Database (HWSD) sand, clay and organic
        content for each station using Equations [2,3,5] from Saxton & Rawls (2006). doi:10.2136/vzj2012.0097.
        
        Parameters
        ----------
        tag : string
        code added to qflag-column when flag-criteria are met
        """
        if not self.sat_point:
            return

        index = self.data.loc[self.data.soil_moisture > self.sat_point].index
        if len(index):
            self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D01(self, tag):
        """
        In situ soil temperature below threshold:
        Flags when ancillary in situ soil temperature is below threshold
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        if 'soil_temperature' in self.data.columns:
            index = self.data[self.data.soil_temperature < t.ancillary_ts_lower].index
            if len(index):
                self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D02(self, tag):
        """
        In situ air temperature below threshold:
        Flags when ancillary in situ air temperature is below threshold
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        if 'air_temperature' in self.data.columns:
            index = self.data[self.data['air_temperature'] < t.ancillary_ta_lower].index
            if len(index):
                self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D03(self, tag):
        """
        GLDAS soil temperature below threshold:
        Flags when ancillary GLDAS NOAA soil temperature is below threshold
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        if 'gldas_soil_temperature' in self.data.columns:
            index = self.data[self.data['gldas_soil_temperature'] < t.ancillary_ts_lower].index
            if len(index):
                self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D04(self, tag):
        """
        Soil moisture rise without precipitation event (in situ):
        Flags when soil moisture increased both during the last hour and during the preceding 24h (increase is larger
        than 2x std-dev during this period), yet ancillary in situ data shows there was no precipitation event greater
        or equal to the minimum precipitation (depending on sensor depth).
    
        At ISMN this flag is only applied to surface soil moisture sensors (<= 10cm sensor depth)
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        if 'precipitation' in self.data.columns:
            min_precipitation = t.ancillary_p_min

            if self.depth_from != None:
                if self.depth_from >= 0.1:
                    return
                if self.depth_from != 0:
                    min_precipitation = float(self.depth_from) * 0.05 * 0.5 * 1000

            self.data['total_precipitation'] = round(self.data['precipitation']
                                                     .rolling(min_periods=1, window=24).sum(), 1)
            self.data['std_x2'] = self.data['soil_moisture'].rolling(min_periods=1, window=25).std() * 2
            self.data['rise24h'] = self.data['soil_moisture'].diff(24)
            self.data['rise1h'] = self.data['soil_moisture'].diff(1)

            index = self.data[(self.data['rise1h'] > 0) & (self.data['rise24h'] > self.data['std_x2']) &
                              (self.data['total_precipitation'] < min_precipitation)].index

            self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D05(self, tag):
        """
        Soil moisture rise without precipitation event (Gldas precipitation):
        Flags when soil moisture increased both during the last hour and during the preceding 24h (increase is larger
        than 2x std-dev during this period), yet ancillary GLDAS data shows there was no precipitation event greater
        or equal to the minimum precipitation (depending on sensor depth).
    
        At ISMN this flag is only applied to surface soil moisture sensors (<= 10cm sensor depth)
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """

        if 'gldas_precipitation' in self.data.columns:
            min_precipitation = t.ancillary_p_min

            if self.depth_from != None:
                if self.depth_from >= 0.1:
                    return
                if self.depth_from != 0:
                    min_precipitation = float(self.depth_from) * 0.05 * 0.5 * 1000

            self.data['gldas_total_precipitation'] = self.data['gldas_precipitation'].rolling(min_periods=1,
                                                                                              window=24).sum()
            self.data['gl_std_x2'] = self.data['soil_moisture'].rolling(min_periods=1, window=25).std() * 2
            self.data['gl_rise24h'] = self.data['soil_moisture'].diff(24)
            self.data['gl_rise1h'] = self.data['soil_moisture'].diff(1)

            index = self.data[(self.data['gl_rise1h'] > 0) & (self.data['gl_rise24h'] > self.data['gl_std_x2']) &
                              (self.data['gldas_total_precipitation'] < min_precipitation)].index

            if len(index):
                self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D06(self, tag):
        """
        Soil moisture spike:
        Flags when soil moisture shows a positive or negative spike.
        See Eq [4,5,6] in Dorigo et al. (2013), Global Automated Quality Control of In Situ
        Soil Moisture Data from the International Soil Moisture Network,VZJ.
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """

        def rolling_var(sm_array) -> float:
            """
            Calulates variance of soil moisture over a time-range from t-12, t+12 hours without the current value
    
            Parameters
            ----------
            sm_array : numpy.ndarray
                soil moisture values from t-12 to t+12 hours
    
            Returns
            -------
            float
                Soil moisture variance within 25 hours without the current value
            """
            sm_array = np.delete(sm_array, 12, axis=0)
            sm_array = sm_array[~np.isnan(sm_array)]
            return ((sm_array - sm_array.mean()) ** 2).sum() / (len(sm_array) - 1)

        def peak(sm_array) -> int:
            """
            Checks if middle element of three consecutive soil moisture measurements is a positive or negative peak or
            alternatively, if middle two values of four consecutive measurements are equal and form a positive or
            negative peak.
    
            Parameters
            ----------
            sm_array : numpy.ndarray
                soil moisture values from t-1 to t+1 hours
    
            Returns
            -------
            int
               0 (no peak)
               1 (peak)
               2 (peak that lasts 2 hours)
            """
            if ((sm_array[0] < sm_array[1]) &
                (sm_array[1] > sm_array[2])) | \
                    ((sm_array[0] > sm_array[1]) & (sm_array[1] < sm_array[2])):
                return 1
            elif len(sm_array) > 3:
                if ((sm_array[0] < sm_array[1]) &
                    (sm_array[1] == sm_array[2]) &
                    (sm_array[2] > sm_array[3])) | (
                        (sm_array[0] > sm_array[1]) &
                        (sm_array[1] == sm_array[2]) &
                        (sm_array[2] < sm_array[3])):
                    return 2
            return 0

        window = np.ones(25)
        window[12] = 0  # set the center-value to zero

        self.data['eq4'] = round(self.data['soil_moisture'].shift(-1)
                                 .div(self.data['soil_moisture'], axis=0).shift(1), 3)
        self.data['eq5'] = round(abs(
            self.data['deriv2'].div(self.data['deriv2'].shift(-2), axis=0).shift(1)), 3)

        # calculate relative variance at time t
        self.data['eq6'] = abs(
            self.data['soil_moisture'].rolling(min_periods=25, window=25, center=True).apply(rolling_var, raw=True)) \
            .div(self.data['soil_moisture'].rolling(window=window, win_type='boxcar', center=True).mean(), axis=0)

        self.data['eq_new1'] = self.data['soil_moisture'].rolling \
            (min_periods=3, window=4, center=True).apply(peak, raw=True).shift(-1)

        self.data['spike_2h'] = self.data['eq_new1'].shift(1) > 1

        self.data['spike'] = (((self.data['eq4'] > 1.15) | (self.data['eq4'] < 0.85)) |
                              (self.data['spike_2h'] > 0)) & \
                             ((self.data['eq5'] > 0.8) & (self.data['eq5'] < 1.2)) & \
                             (self.data['eq6'] < 1) & \
                             (self.data['eq_new1'] > 0)

        index = self.data[(self.data.spike > 0) | ((self.data.spike.shift(1) > 0) & (self.data['spike_2h'] > 0))].index

        self.data['qflag'][index].apply(lambda x: x.add(tag))

    def flag_D07(self, tag):
        """
        !Includes jumps (D08)!
        Soil moisture drop (D07) or jump (D08):
        Flags when time-series shows a break based on relative (and absolute) change in
        soil moisture, a comparison of the first derivatives to the average of first derivatives centered at t and a
        large negative (positive) second derivative at t followed by a large postive (negative) value at t+1.
        The resective observations are then flagged as drop "D07" (or jump "D08") when the 1. derivative at t is
        negative (positive).

        See Eq [7,8,9] in Dorigo et al. (2013), Global Automated Quality Control of In Situ
        Soil Moisture Data from the International Soil Moisture Network,VZJ.

        Includes an alternative drop type, which was not included in VJZ paper: drop from above 0.05m³/m³ to zero
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """

        self.data['absolute_change'] = self.data['soil_moisture'] - self.data['soil_moisture'].shift(1)
        self.data['eq7'] = abs(self.data['absolute_change'].div(self.data['soil_moisture']))
        self.data['eq8'] = abs(self.data['deriv1'].rolling(min_periods=4, window=25, center=True).mean() * 10)
        self.data['eq9'] = round(abs(self.data['deriv2'].shift(1).div(self.data['deriv2'])), 1)

        self.data['eq9a'] = abs(self.data['deriv2'].div(self.data['deriv2'].shift(-2)))

        # Include drops to zero!
        self.data['eq_new2'] = (abs(self.data['absolute_change']) > 5) & (
                self.data['soil_moisture'] == 0)

        index = self.data[(self.data['eq7'] > 0.1) &
                          (abs(self.data['absolute_change']) > 1) &
                          (self.data['soil_moisture'] != 0) &
                          (abs(self.data['deriv1']) > self.data['eq8']) &
                          (np.isclose(self.data['eq9'], 1, atol=1e-2)) &
                          (self.data['deriv2'] != 0) &
                          (self.data['eq9a'] > 10)].index

        index_neg = index.intersection(self.data[self.data['deriv1'] < 0].index)
        index_pos = index.intersection(self.data[self.data['deriv1'] > 0].index)

        index_zero = self.data[self.data['eq_new2'] > 0].index  # index where there are drops to zero
        index_neg = index_neg.append(index_zero)

        if len(index_neg):
            self.data['qflag'][index_neg].apply(lambda x: x.add(tag))

        # Change tag to indicate soil moisture jumps
        if isinstance(tag, int):
            tag += 1
        elif tag == 'D07':
            tag = 'D08'

        # Includes soil moisture jumps (flag D08)
        if len(index_pos):
            self.data['qflag'][index_pos].apply(lambda x: x.add(tag))


    def flag_D08(self):
        """
        !Included in flag_D07!
        """
        pass


    def flag_D09(self, tag):
        """
        Low constant values:
        Flags where a previous soil moisture break (D07) and a period of low relative variance
        (variance/mean < 0.001 m³m⁻³) coincide, soil moisture observations are flagged as "D09" as long as the
        relative variance remains below the treshold. The defined minimum duration of a low plateau is 13h.

        See Eq [14] in Dorigo et al. (2013), Global Automated Quality Control of In Situ
        Soil Moisture Data from the International Soil Moisture Network,VZJ.
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """

        self.data.dropna(subset=['soil_moisture'], inplace=True)

        # calculate relative variance
        self.data['rel_var'] = round(self.data['soil_moisture'].rolling(min_periods=13, window=13).var()
                                     .shift(-12), 4) / round(self.data['soil_moisture']
                                                             .rolling(min_periods=13, window=13)
                                                             .mean().shift(-12), 4)

        # When sm == 0 for >12h => the mean equals 0 => relative variance is therefore calculated as nan
        # To catch periods of sm=0 after a sm-drop to zero (D07 criteria 4): reset these nan-values to 0
        self.data['rel_var'][self.data['rel_var'].isna() & (self.data['soil_moisture'] == 0)] = 0.0

        # find where there is a drop in soil moisture (flag D07) and a period of low relative variance
        flag_D07 = 'D07'
        if type(tag) == int:
            flag_D07 = 10
        self.data['event'] = ((self.data['qflag'].astype(str)).str.contains(str(flag_D07)) & (self.data['rel_var'] < 0.001))
        self.data['event'].replace(np.nan, 0, inplace=True)
        self.data['event'] = self.data['event'].astype(int)

        # assign -1 where the "event" could end and create a pleateau_mask
        self.data.loc[(self.data[['rel_var']].max(1).diff() >= 0.001) & (self.data['event'] == 0), 'event'] = -1

        def plateau_mask(array_sequence) -> list:
            """
            Generates a mask where Plateau criteria are fulfilled.
    
            Parameters
            ----------
            array_sequence:  numpy ndarray
                sequence of 1 (Plateau criteria fulfilled), -1(Plateau criteria no longer fulfilled), 0
    
            Returns
            -------
            list
                sequence of 1 (Plateau criteria fulfilled) and 0 (Plateau criteria not fulfilled)
            """
            return reduce(lambda x, y: x + [max(min(x[-1] + y, 1), 0)], array_sequence, [0])[1:]

        self.data['plateau'] = plateau_mask(self.data['event'].values)

        # Extend each Plateau to at least 13h time (minimum period)
        self.data['end'] = self.data['plateau'].rolling(min_periods=13, window=13).max()

        index = self.data[self.data['end'] > 0.0].index

        if len(index):
            self.data['qflag'][index].apply(lambda x: x.add(tag))

        if type(self.data.index) == pd.core.indexes.datetimes.DatetimeIndex:
            self.data = self.data.resample('H').asfreq()



    def flag_D10(self, tag):
        """
        Invariant high soil moisture values:
        Flags where the variance of soil moisture values within 12h is below 0.05 ->  period of low variance (plv)
        with a min_len of 12h. The plv requires a rise in the first derivative of at least 0.25 in beginning of the plv
        +/- 12h and a drop in the first derivative lower or equal to 0 at the end of the plv +/- 12h a mean of the
        soil moisture values between the rise and drop (or if they occur beyond plv scope, beginning and/or respective
        end of plv) of above 0.95% of the previous highest soil moisture value ever detected (highest_sm).

        See Eq [10,11,12,13] in Dorigo et al. (2013), Global Automated Quality Control of In Situ
        Soil Moisture Data from the International Soil Moisture Network,VZJ.
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """

        def renumber_plateaus(array) -> list:
            """
            Possible plateaus are numbered consecutively.
            (e.g.: array([1,0,1,1,0,0,1,1)] -> [1,0,2,2,0,0,3,3])
    
            Parameters
            ----------
            array : ndarray
                1-dimensional array containing mask where variance of soil moisture observations are below 0.05 for 12h
    
            Returns
            -------
            seq : list
                Sequence containing rising group numbers (potential plateaus).
            """
            group = 1
            seq = []
            for a, b in zip(array, array[1:]):
                seq.append((lambda x: group if x > 0 else 0)(a))
                if a == 1 and b == 0:
                    group += 1
            return seq + [group * array[-1]]

        # Mean of plateau must be higher than 95% of this threshold;
        # For ISMN quality flags the previous 2 years of data are taken into account.
        highest_sm_value = self.data['soil_moisture'][self.data['soil_moisture'] < 60].max()        
        
        

        # Throw out datagaps - plateau can bridge gap
        self.data.dropna(subset=['soil_moisture'], inplace=True)

        # Look for periods of low variance (VAR) and assign rising numbers
        self.data.loc[:, 'VAR'] = self.data['soil_moisture'].rolling(min_periods=12, window=12).var().shift(-11) <= 0.05
        self.data['VAR_grouped'] = renumber_plateaus(self.data.VAR.values)

        # Look for maximum rise and minimum drop within 25 hours for each period of low varicance
        self.data.loc[:, 'maximum'] = self.data['deriv1'].rolling(window=25, min_periods=1).max().shift(-12)
        self.data.loc[:, 'minimum'] = self.data['deriv1'].rolling(window=25, min_periods=1).min().shift(-24)

        rise = round(self.data.groupby('VAR_grouped')['maximum'].first(), 3)
        drop = round(self.data.groupby('VAR_grouped')['minimum'].last(), 3)
        rise = rise[rise >= 0.25]
        drop = drop[drop < 0]

        possible_plateaus = pd.concat([rise, drop], axis=1)[1:]
        possible_plateaus.dropna(inplace=True)

        index = []
        for idx, row in possible_plateaus.iterrows():
            # Look for possible plateaus including both a soil moisture rise and drop
            self.data['VAR_rise_drop'] = self.data.VAR_grouped[(self.data.VAR_grouped == idx)]
            VAR_period = self.data['VAR_rise_drop'].rolling(window=12, min_periods=1).max() == idx

            # max lies inside of VAR period
            if not self.data.index[VAR_period & (self.data['deriv1'] == row.maximum)].empty:
                max_search_period_start = self.data.index[VAR_period & (self.data['deriv1'] == row.maximum)][0]
                # min lies within VAR period
                if not self.data.index[VAR_period & (self.data['deriv1'] == row.minimum)].empty:
                    min_search_period_end = self.data.index[VAR_period & (self.data['deriv1'] == row.minimum)][0]
                # min lies outside VAR
                else:
                    min_search_period_end = VAR_period[::-1].idxmax()

            # max lies outside of VAR period
            else:
                max_search_period_start = VAR_period.idxmax()
                # mimimum within VAR period
                if not self.data.index[VAR_period & (self.data['deriv1'] == row.minimum)].empty:
                    min_search_period_end = self.data.index[VAR_period & (self.data['deriv1'] == row.minimum)][0]
                # minimum within VAR period
                else:
                    min_search_period_end = VAR_period[::-1].idxmax()

            Plateau = self.data['soil_moisture'].loc[max_search_period_start:min_search_period_end]
            if 'highest_sm' in self.data.columns:
                if Plateau.mean() > \
                        (self.data['highest_sm'].loc[max_search_period_start:min_search_period_end].mean() * 0.95):
                    index.extend(Plateau.index)
            else: # if no highest_sm column then use highest_sm_value as threshold
                if Plateau.mean() > (highest_sm_value * 0.95):
                    index.extend(Plateau.index)

        self.data['qflag'][index].apply(lambda x: x.add(tag))


    def flag_G(self, tag):
        """
        Applies tag for all unflagged observations
        
        Parameters
        ----------
        tag : string or int, optional
        code added to qflag-column when flag-criteria are met
        """
        index_good = self.data[self.data['qflag'] == set()].index
        self.data['qflag'][index_good].apply(lambda x: x.add(tag))
