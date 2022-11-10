======
flagit
======

.. image:: https://github.com/TUW-GEO/flagit/workflows/Automated%20Tests/badge.svg?branch=main
   :target: https://github.com/TUW-GEO/flagit/actions

.. image:: https://coveralls.io/repos/github/TUW-GEO/flagit/badge.svg?branch=main
    :target: https://coveralls.io/github/TUW-GEO/flagit?branch=main

.. image:: https://badge.fury.io/py/flagit.svg
    :target: http://badge.fury.io/py/flagit

.. image:: https://readthedocs.org/projects/flagit/badge/?version=latest
   :target: http://flagit.readthedocs.org/

ISMN quality control procedures for in situ soil moisture time series

Citation
========

If you use the software in a publication then please cite:

* Dorigo, W.A. , Xaver, A. Vreugdenhil, M. Gruber, A., Hegyiova, A. Sanchis-Dufau, A.D., Zamojski, D. , Cordes, C., Wagner, W., and Drusch, M. (2013). Global Automated Quality Control of In situ Soil Moisture data from the International Soil Moisture Network. Vadose Zone Journal, 12, 3, doi:10.2136/vzj2012.0097

Please also cite the correct version of this package. Click on the badge below, select the correct version and copy the text under "Cite as".

.. image:: https://zenodo.org/badge/304609951.svg
   :target: https://zenodo.org/badge/latestdoi/304609951

Installation
============

For installation we recommend `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_. So please install it according to the official instructions. As soon 
as the ``conda`` command is available in your shell you can continue:

.. code:: python

    conda install -c conda-forge pandas scipy numpy

This following command will install the flagit pip package:

.. code:: python

    pip install flagit

To create a full development environment with conda, the environment.yml file in this repository can be used:

.. code:: python

    git clone git@github.com:TUW-GEO/flagit.git flagit
    cd flagit
    conda create -n flagit python=3.10 # or any supported python version
    conda activate flagit
    conda env update -f environment.yml -n flagit
    python setup.py develop
    
   
After that you should be able to run:

.. code:: python

    python setup.py test

to run the test suite.

Description
===========

The `International Soil Moisture Network (ISMN) <https://ismn.geo.tuwien.ac.at>`_ quality control procedures are used to detect implausible and dubious 
measurements in hourly situ soil moisture time series. When downloading data at ISMN all variable-data are provided 
with additional tags in column "qflag", which can be one of three main categories: C (exceeding plausible geophysical range), 
D (questionable/dubious) or G (good).

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

At ISMN, ancillary data sets are used for flags C03, D01 - D05 (see table above). Since we do not provide ancillary data, 
we kindly ask users to either provide their own ancillary in situ and GLDAS data (including a soil moisture saturation 
value for flag C03) in the input (pandas.DataFrame), or accept the limitation of the quality control to flags without 
ancillary requirements.

We hope to update the functionality of this package to facilitate the inclusion of ancillary data.

For a detailed description of the quality control procedures see paper on `Global Automated quality control <https://www.geo.tuwien.ac.at/downloads/wd/journal/Dorigo2013_VZJ_QC_ISMN.pdf>`_.

Contribute
==========

We would be happy if you would like to contribute. Please raise an issue explaining what
is missing or if you find a bug. We will also gladly accept pull requests
against our main branch for new features or bug fixes.

Guidelines
----------

If you want to contribute please follow these steps:

- Fork the flagit repository to your account
- Clone the repository
- make a new feature branch from the flagit main branch
- Add your feature
- Please include tests for your contributions in one of the test directories.
  We use unittest so a simple function called test_my_feature is enough
- submit a pull request to our main branch

Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
