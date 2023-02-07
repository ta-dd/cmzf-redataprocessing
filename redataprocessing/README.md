
# redataprocessing: tool for requesting, decoding and storing real estate data from Sreality API

## What is it?

**redataprocessing** is a Python package that provides functions for requesting data on
real estate offers from [**Sreality**](https://www.sreality.cz) API based on few categories. 
Moreover, it contains functions for decoding of requests into `pandas DataFrame` and their storage
to `SQLite`.

## Main Features
Here are few functionalities of **redataprocessing**:

  - Requesting of current real estate offers based on chosen parameters
  - Decoding of requested jsons into `pandas DataFrame`
  - Functions for download of both list with offers and list with detailed description of downloaded offers
  - Asynchronous requesting of description data
  - Storage of dataframes with offers and their description into `SQLite` database

## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/vojtechkaniaedu/re_data_processing/redadataprocessing

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/redataprocessing).

```sh
# PyPI
pip install redataprocessing
```

## Installation from sources
In the `redataprocessing` directory (same one where you found this file after
cloning the git repo), execute:

```sh
python setup.py install
```

## Background
Work on ``redataprocessing`` started as a university course project at 
[Institute of Economic Studies](https://ies.fsv.cuni.cz) in winter semester 2022/2023.

## Getting Help

For usage questions, the best place to go to is [StackOverflow](https://stackoverflow.com).
Further, general questions could be send to vojtech.kania@gmail.com.

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.
