from flagit import flagit
import numpy as np
import pandas as pd
import os
import unittest


class TestInterface(unittest.TestCase):
    def setUp(self):
        """
        Read pandas.DataFrame from CSV file and setting up of interface object
        """
        self.ancillary_path = os.path.join(os.path.dirname(__file__))
        self.data = pd.read_csv(os.path.join(self.ancillary_path,
                                                './test_data/test_dataframe.csv'), index_col='utc', parse_dates=True)
        self.iface = flagit.Interface(data=self.data, sat_point=42.7)

    def test_init(self) -> None:
        """
        Test if FormatError is raised
        """
        self.data.drop(['soil_moisture'], axis=1, inplace=True)
        with self.assertRaises(flagit.FormatError):
            flagit.Interface(data=self.data)

    def test_run_flags(self) -> None:
        """
        Test application of ISMN quality control - all flags applied
        """
        df = self.iface.run()
        assert self.data.soil_moisture[10] == 5.1
        assert self.data.index[2] == pd.Timestamp('2020-01-27 02:00:00'), 'Error reading data'
        assert self.data.qflag[30] == {'C01', 'D01', 'D02', 'D03', 'D06'}
        assert self.data.qflag[40] == {'D01', 'D02', 'D03', 'D07', 'D09'}
        assert self.data.qflag[62] == {'D01', 'D03'}
        assert self.data.qflag[69] == {'D01', 'D02', 'D03'}
        assert self.data.qflag[70] == {'C02', 'C03', 'D01', 'D02', 'D03', 'D04', 'D05'}
        assert self.data.qflag[99] == {'C03', 'D01', 'D02', 'D03', 'D10'}
        assert self.data.qflag[136] == {'D03', 'D04', 'D05'}
        assert self.data.qflag[636] == {'G'}
        np.testing.assert_almost_equal(self.data.deriv1[58], -5.551115123125783e-17)
        np.testing.assert_almost_equal(self.data.deriv2[29], -6.200000000000003)
        assert len(self.data.keys()) == 34
        assert type(df) == pd.DataFrame
        assert len(df) == 696
        assert len(df.keys()) == 7
        assert df[df['soil_moisture'].isna()].index[0] == pd.Timestamp('2020-02-19 15:00:00', freq='H')

    def test_check_C01(self) -> None:
        """
        Test flag C01
        """
        self.iface.run(name='C01')
        assert self.data.qflag[30] == {'C01'}
        assert self.data.qflag[31] == set()

    def test_check_C02(self) -> None:
        """
        Test flag C02
        """
        self.iface.run(name='C02')
        assert self.data.qflag[70] == {'C02'}
        assert self.data.qflag[69] == set()

    def test_check_C03(self) -> None:
        """
        Test flag C03
        """
        self.iface.run(name='C03')
        assert self.data.qflag[80] == {'C03'}
        assert self.data.qflag[79] == set()

    def test_check_D01(self) -> None:
        """
        Test flag D01
        """
        self.iface.run(name='D01')
        assert self.data.qflag[35] == {'D01'}
        assert self.data.qflag[136] == set()

    def test_check_D02(self) -> None:
        """
        Test flag D02
        """
        self.iface.run(name='D02')
        assert self.data.qflag[2] == {'D02'}
        assert self.data.qflag[62] == set()

    def test_check_D03(self) -> None:
        """
        Test flag D03
        """
        self.iface.run(name='D03')
        assert self.data.qflag[70] == {'D03'}
        assert self.data.qflag[636] == set()
        assert self.data.qflag[0] == {'D03'}

    def test_check_D04(self) -> None:
        """
        Test flag D04
        """
        self.iface.run(name='D04')
        assert self.data.qflag[70] == {'D04'}
        assert self.data.qflag[71] == set()

    def test_check_D05(self) -> None:
        """
        Test flag D05
        """
        self.iface.run(name='D05')
        assert self.data.qflag[70] == {'D05'}
        assert self.data.qflag[636] == set()

    def test_check_D06(self) -> None:
        """
        Test flag D06
        """
        self.iface.run(name='D06')
        np.testing.assert_almost_equal(self.data.deriv1[58], -5.551115123125783e-17)
        np.testing.assert_almost_equal(self.data.deriv2[29], -6.200000000000003)
        assert self.data.qflag[30] == {'D06'}
        assert self.data.qflag[29] == set()

    def test_check_D07_D08_D09(self) -> None:
        """
        Test flags D07, D08 and D09
        """
        self.iface.run(name=['D07', 'D09'])
        assert self.data.qflag[40] == {'D09', 'D07'}
        assert self.data.qflag[80] == {'D08'}
        assert self.data.qflag[61] == set()
        assert self.data.qflag[41] == {'D09'}
        assert self.data.qflag[39] == set()

    def test_check_D10(self) -> None:
        """
        Test flag D10
        """
        self.iface.run(name='D10')
        assert self.data.qflag[99] == {'D10'}
        assert self.data.qflag[75] == set()

    def test_check_good(self) -> None:
        """
        Test flag "good"
        """
        self.iface.run(name='G')
        assert self.data.qflag[3] == {'G'}
        assert len(np.unique(self.data.qflag)) == 1



if __name__ == '__main__':
    unittest.main()
