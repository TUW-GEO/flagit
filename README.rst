======
flagit
======


ISMN quality control procedures for in situ soil moisture observations


Description
===========

The ISMN Quality control procedures are used to detect implausible and dubious in situ soil moisture measurements
(flagging). When downloading data at ISMN (https://ismn.geo.tuwien.ac.at) all variable-data are provided with additional
tags in column "qflag" which can be one of three main categories: C (exceeding plausible geophysical range),
D (questionable/dubious) or G (good).


.. raw:: html
    
    <table class="table table-bordered table-hover table-condensed">
        <thead>
            <tr>
                <th title="Field #1">code</th>
                <th title="Field #2">description</th>
                <th title="Field #3">ancillary data required</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>C01</td>
                <td>soil moisture &lt; 0 m³/m³</td>
                <td>-</td>
            </tr>
            <tr>
                <td>C02</td>
                <td>soil moisture &gt; 0.60 m³/m³</td>
                <td>-</td>
            </tr>
            <tr>
                <td>C03</td>
                <td>soil moisture &gt; saturation point (based on HWSD)</td>
                <td>HWSD sand, clay and organic content</td>
            </tr>
            <tr>
                <td>D01</td>
                <td>negative soil temperature (in situ)</td>
                <td>in situ soil temperature</td>
            </tr>
            <tr>
                <td>D02</td>
                <td>negative air temperature (in situ)</td>
                <td>in situ air temperature</td>
            </tr>
            <tr>
                <td>D03</td>
                <td>negative soil temperature (GLDAS)</td>
                <td>GLDAS soil temperature</td>
            </tr>
            <tr>
                <td>D04</td>
                <td>rise in soil moisture without precipitation (in situ)</td>
                <td>in situ precipitation</td>
            </tr>
            <tr>
                <td>D05</td>
                <td>rise in soil moisture without precipitation (GLDAS)</td>
                <td>GLDAS precipitation</td>
            </tr>
            <tr>
                <td>D06</td>
                <td> spikes</td>
                <td>-</td>
            </tr>
            <tr>
                <td>D07</td>
                <td> negative breaks (drops)</td>
                <td>-</td>
            </tr>
            <tr>
                <td>D08</td>
                <td>positive breaks (jumps)</td>
                <td>-</td>
            </tr>
            <tr>
                <td>D09</td>
                <td>constant low values following negative break</td>
                <td>-</td>
            </tr>
            <tr>
                <td>D10</td>
                <td>saturated plateaus</td>
                <td>-</td>
            </tr>
            <tr>
                <td>G</td>
                <td>good</td>
                <td>-</td>
            </tr>
        </tbody>
    </table>

At ISMN, ancillary data sets are used for flags C03, D01 - D05. Since we cannot provide this ancillary data at this
point, we kindly ask users to either provide their own ancillary in situ and GLDAS data in the input pandas.DataFrame,
in addition to a soil moisture saturation (i.e.: highest soil moisture for soil properties at the respective in situ
station) or accept the limitation of the quality control to flags without ancillary requirements.

We will try to update the functionality of this package to include ancillary data.
	
	
For a detailed description of the quality control procedures ee: Dorigo, W.A. , Xaver, A. Vreugdenhil, M. Gruber, A., Hegyiová, A. Sanchis-Dufau, A.D., Zamojski, D. , Cordes, C., Wagner, W., and Drusch, M. (2013). GlobalAutomated Quality Control of In situ Soil Moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12, 3, doi:10.2136/vzj2012.0097

Citation
========

If you use the software in a publication then please cite: 

* Dorigo, W.A. , Xaver, A. Vreugdenhil, M. Gruber, A., Hegyiová, A. Sanchis-Dufau, A.D., Zamojski, D. , Cordes, C., Wagner, W., and Drusch, M. (2013). GlobalAutomated Quality Control of In situ Soil Moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12, 3, doi:10.2136/vzj2012.0097
* https://github.com/TUW-GEO/flagit


Installation
============

This package should be installable through pip:

.. code::

    pip install flagit


Example installation script
---------------------------

The following script will install miniconda and setup the environment on a UNIX
like system. Miniconda will be installed into ``$HOME/miniconda``.

.. code::

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

.. code::

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

.. raw:: html

    <table border="1" class="dataframe">
        <thead>
        <tr style="text-align: right;">
            <th></th>
            <th>soil_moisture</th>
            <th>soil_temperature</th>
            <th>air_temperature</th>
            <th>precipitation</th>
            <th>gldas_soil_temperature</th>
            <th>gldas_precipitation</th>
        </tr>
        <tr>
            <th>utc</th>
            <th></th>
            <th></th>
            <th></th>
            <th></th>
            <th></th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <th>2017-01-27 00:00:00</th>
            <td>5.0</td>
            <td>-4.7</td>
            <td>-13.6</td>
            <td>0.0</td>
            <td>-8.474371</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 01:00:00</th>
            <td>4.9</td>
            <td>-4.9</td>
            <td>-13.4</td>
            <td>0.0</td>
            <td>-8.641007</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 02:00:00</th>
            <td>4.9</td>
            <td>-5.1</td>
            <td>-14.0</td>
            <td>0.0</td>
            <td>-8.807644</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 03:00:00</th>
            <td>4.9</td>
            <td>-5.1</td>
            <td>-13.2</td>
            <td>0.0</td>
            <td>-8.974280</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 04:00:00</th>
            <td>4.9</td>
            <td>-4.9</td>
            <td>-11.2</td>
            <td>0.0</td>
            <td>-9.133185</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 05:00:00</th>
            <td>4.9</td>
            <td>-4.6</td>
            <td>-10.1</td>
            <td>0.0</td>
            <td>-9.292090</td>
            <td>0.0</td>
        </tr>
        <tr>
            <th>2017-01-27 06:00:00</th>
            <td>5.0</td>
            <td>-4.5</td>
            <td>-8.9</td>
            <td>0.0</td>
            <td>-9.450995</td>
            <td>0.0</td>
        </tr>
        </tbody>
    </table>



.. code:: python

    from src.flagit import flagit
    import pandas as pd


.. code:: python

    # read from pickle file:
    file_path = "/path_to_dataframe/dataframe/data.pkl"
	df = pd.read_pickle(file_path)


.. code:: python

    # read from csv file
    file_path = "/path_to_dataframe/dataframe/data.csv"
	df = pd.read_csv(file_path, sep=',', index_col='utc', parse_dates=True)


.. code:: python

    # initialize interface
    flag = Interface(df)
	result_df = flag.run(sat_point = 42.7)
	
	# optional: choose only specific algorithms through list or string:
	result_df = flag.run(name = ['D06', 'D07', 'D09'])
	result_df = flag.run(name = 'C01')


.. code:: python

    # get flag-descriptions
    flag = Interface(df)
    flag.get_flag_description()

    




	
	
