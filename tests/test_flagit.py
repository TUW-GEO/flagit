import flagit.flagit as flag
import numpy as np
import pandas as pd
import os


def load_data():
    ancillary_path = os.path.abspath(os.path.join(os.getcwd(),'tests','test_data'))
    os.chdir(ancillary_path)
    return pd.read_pickle('./df_v3.pkl')

df = load_data()

def test_run_flags():
    reset_qflags()
    flag.flagit(df, 42.7)
    assert df.soil_moisture[10] == 5.1
    assert df.index[2] == pd.Timestamp('2017-01-27 02:00:00'), 'Error reading data'
    assert df.qflag[30] == {1, 4, 5, 6, 9}
    assert df.qflag[40] == {4, 5, 6, 10, 12}
    assert df.qflag[62] == {4, 6}
    assert df.qflag[69] == {4, 5, 6}
    assert df.qflag[70] == {2, 3, 4, 5, 6, 7, 8}
    assert df.qflag[99] == {3, 4, 5, 6, 13}
    assert df.qflag[136] == {6, 7, 8}
    assert df.qflag[636] == {14}
    np.testing.assert_almost_equal(df.deriv1[58], -5.551115123125783e-17)
    np.testing.assert_almost_equal(df.deriv2[29], -6.200000000000003)
    assert len(df) == 695
    assert len(df.keys()) == 29


def reset_qflags():
    df['qflag'] = df.qflag.apply(lambda x: set())


def test_check_c01():
    reset_qflags()
    assert df.soil_moisture[10] == 5.1
    assert df.index[2] == pd.Timestamp('2017-01-27 02:00:00'), 'Error reading data'
    flag.flag_c01(df)
    assert df.qflag[30] == {1}
    assert df.qflag[31] == set()


def test_check_c02():
    flag.flag_c02(df)
    assert df.qflag[70] == {2}
    assert df.qflag[69] == set()


def test_check_c03():
    flag.flag_c03(df, 42.7)
    assert df.qflag[80] == {3}
    assert df.qflag[79] == set()


def test_check_d01():
    flag.flag_d01(df)
    assert df.qflag[35] == {4}
    assert df.qflag[136] == set()


def test_check_d02():
    reset_qflags()
    flag.flag_d02(df)
    assert df.qflag[2] == {5}
    assert df.qflag[62] == set()


def test_check_d03():
    reset_qflags()
    flag.flag_d03(df)
    assert df.qflag[70] == {6}
    assert df.qflag[636] == set()
    assert df.qflag[0] == {6}


def test_check_d04():
    reset_qflags()
    flag.flag_d04(df)
    assert df.qflag[70] == {7}
    assert df.qflag[71] == set()


def test_check_d05():
    reset_qflags()
    flag.flag_d05(df)
    assert df.qflag[70] == {8}
    assert df.qflag[636] == set()


def test_check_d06():
    flag.apply_savgol(df)
    flag.flag_d06(df)
    np.testing.assert_almost_equal(df.deriv1[58], -5.551115123125783e-17)
    np.testing.assert_almost_equal(df.deriv2[29], -6.200000000000003)
    assert df.qflag[30] == {9}
    assert df.qflag[29] == set()


def test_check_d07():
    flag.flag_d07(df)
    assert df.qflag[40] == {10}
    assert df.qflag[41] == set()
    assert df.qflag[60] == {11}
    assert df.qflag[61] == set()


def test_check_d09():
    flag.flag_d09(df)
    assert df.qflag[41] == {12}
    assert df.qflag[39] == set()


def test_check_d10():
    flag.flag_d10(df)
    assert df.qflag[99] == {13}
    assert df.qflag[75] == set()


def test_check_good():
    flag.flag_g(df)
    assert df.qflag[3] == {14}


if __name__ == '__main__':
    test_run_flags()
    test_check_c01()
    test_check_c02()
    test_check_c03()
    test_check_d01()
    test_check_d02()
    test_check_d03()
    test_check_d04()
    test_check_d05()
    test_check_d06()
    test_check_d07()
    test_check_d09()
    test_check_d10()
    test_check_good()
