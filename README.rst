======
flagit
======

.. image:: https://travis-ci.org/TUW-GEO/flagit.svg?branch=master
    :target: https://travis-ci.org/TUW-GEO/flagit

.. image:: https://coveralls.io/repos/github/TUW-GEO/flagit/badge.svg?branch=master
    :target: https://coveralls.io/github/TUW-GEO/flagit?branch=master

.. image:: https://badge.fury.io/py/flagit.svg
    :target: http://badge.fury.io/py/flagit

.. image:: https://readthedocs.org/projects/flagit/badge/?version=latest
   :target: http://flagit.readthedocs.org/

ISMN quality control procedures for in situ soil moisture observations


Description
===========

The International Soil Moisture Network (ISMN) quality control procedures are used to detect implausible and dubious in
situ soil moisture measurements (flagging). When downloading data at ISMN (https://ismn.geo.tuwien.ac.at) all
variable-data are provided with additional tags in column "qflag" which can be one of three main categories: C
(exceeding plausible geophysical range), D (questionable/dubious) or G (good).

+------+-------------------------------------------------------+-------------------------------------+
| code | description                                           | ancillary data required             |
+======+=======================================================+=====================================+
| C01  | soil moisture < 0 m³/m³                               |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| C02  | soil moisture > 0.60 m³/m³                            |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| C03  | soil moisture > saturation point (based on HWSD)      | HWSD sand, clay and organic content |
+------+-------------------------------------------------------+-------------------------------------+
| D01  | negative soil temperature (in situ)                   | in situ soil temperature            |
+------+-------------------------------------------------------+-------------------------------------+
| D02  | negative air temperature (in situ)                    | in situ air temperature             |
+------+-------------------------------------------------------+-------------------------------------+
| D03  | negative soil temperature (GLDAS)                     | GLDAS soil temperature              |
+------+-------------------------------------------------------+-------------------------------------+
| D04  | rise in soil moisture without precipitation (in situ) | in situ precipitation               |
+------+-------------------------------------------------------+-------------------------------------+
| D05  | rise in soil moisture without precipitation (GLDAS)   | GLDAS precipitation                 |
+------+-------------------------------------------------------+-------------------------------------+
| D06  | spikes                                                |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| D07  | negative breaks (drops)                               |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| D08  | positive breaks (jumps)                               |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| D09  | constant low values following negative break          |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| D10  | saturated plateaus                                    |                                     |
+------+-------------------------------------------------------+-------------------------------------+
| G    | good                                                  |                                     |
+------+-------------------------------------------------------+-------------------------------------+


At ISMN, ancillary data sets are used for flags C03, D01 - D05. Since we cannot provide this ancillary data at this
point, we kindly ask users to either provide their own ancillary in situ and GLDAS data in the input (pandas.DataFrame),
plus a soil moisture saturation value as keyword when running the code (see instructions on using flagit module below)
or accept the limitation of the quality control to flags without ancillary requirements.

We will try to update the functionality of this package to include ancillary data.

For a detailed description of the quality control procedures ee: Dorigo, W.A. , Xaver, A. Vreugdenhil, M. Gruber, A., Hegyiova, A. Sanchis-Dufau, A.D., Zamojski, D. , Cordes, C., Wagner, W., and Drusch, M. (2013). GlobalAutomated Quality Control of In situ Soil Moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12, 3, doi:10.2136/vzj2012.0097

Citation
========

If you use the software in a publication then please cite:

* Dorigo, W.A. , Xaver, A. Vreugdenhil, M. Gruber, A., Hegyiova, A. Sanchis-Dufau, A.D., Zamojski, D. , Cordes, C., Wagner, W., and Drusch, M. (2013). Global Automated Quality Control of In situ Soil Moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12, 3, doi:10.2136/vzj2012.0097
* https://github.com/TUW-GEO/flagit


Installation
============

This package should be installable through pip:

.. code:: python

    pip install flagit


Example installation script
---------------------------

The following script will install miniconda and setup the environment on a UNIX
like system. Miniconda will be installed into ``$HOME/miniconda``.

.. code:: python

   wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
   bash miniconda.sh -b -p $HOME/miniconda
   export PATH="$HOME/miniconda/bin:$PATH"
   git clone git@github.com:TUW-GEO/flagit.git flagit
   cd flagit
   conda env create -f environment.yml
   source activate flagit


This script adds ``$HOME/miniconda/bin`` temporarily to the ``PATH`` to do this
permanently add ``export PATH="$HOME/miniconda/bin:$PATH"`` to your ``.bashrc``
or ``.zshrc``

The last line in the example activates the ``flagit`` environment.

After that you should be able to run:

.. code:: python

    python setup.py test

to run the test suite.


Contribute
==========

We are happy if you want to contribute. Please raise an issue explaining what
is missing or if you find a bug. We will also gladly accept pull requests
against our master branch for new features or bug fixes.

Development setup
-----------------

For Development we also recommend a ``conda`` environment. You can create one
including test dependencies and debugger by running
``conda env create -f environment.yml``. This will create a new
``ismn`` environment which you can activate by using
``source activate ismn``.

Guidelines
----------

If you want to contribute please follow these steps:

- Fork the ismn repository to your account
- Clone the repository
- make a new feature branch from the ismn master branch
- Add your feature
- Please include tests for your contributions in one of the test directories.
  We use unittest so a simple function called test_my_feature is enough
- submit a pull request to our master branch


Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.



Using flagit module
===================

This example program shows how to initialize the Interface an run the flagging procedures.


As Input a pandas.DataFrame of the following format is required:

+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
|                     | soil_moisture | soil_temperature | air_temperature | precipitation | gldas_soil_temperature | gldas_precipitation |
+=====================+===============+==================+=================+===============+========================+=====================+
| utc                 |               |                  |                 |               |                        |                     |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 00:00:00 | 5.0           | -4.7             | -13.6           | 0.0           | -8.4                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 01:00:00 | 4.9           | -4.9             | -13.4           | 0.0           | -8.6                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 02:00:00 | 4.9           | -5.1             | -14.0           | 0.0           | -8.8                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 03:00:00 | 4.9           | -5.1             | -13.2           | 0.0           | -8.9                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 04:00:00 | 4.9           | -4.9             | -11.2           | 0.0           | -9.1                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 05:00:00 | 4.9           | -4.6             | -10.1           | 0.0           | -9.2                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+
| 2017-01-27 06:00:00 | 5.0           | -4.5             | -8.9            | 0.0           | -9.4                   | 0.0                 |
+---------------------+---------------+------------------+-----------------+---------------+------------------------+---------------------+


.. code:: python

    from src.flagit import flagit
    import pandas as pd


.. code:: python

    # read from CSV file
    file_path = "/path_to_dataframe/dataframe/data.csv"
    df = pd.read_csv(file_path, sep=',', index_col='utc', parse_dates=True)


.. code:: python

    # initialize interface
    flag = Interface(df)
    result_df = flag.run(sat_point = 42.7)

    # optional: choose only specific procedures by providing a list or string as name:
    result_df = flag.run(name = ['D06', 'D07', 'D09'])
    result_df = flag.run(name = 'C01')


.. code:: python

    # get flag-descriptions
    flag = Interface(df)
    flag.get_flag_description()
