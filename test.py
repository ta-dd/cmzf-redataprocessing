import pandas as pd
import numpy as np

import requests
import sqlite3
import sys
import certifi
import os

from datetime import date
from time import sleep 
from random import randint, choice

from tqdm.auto import tqdm

from typing import Dict, Union, Optional, Tuple
import re 

from redataprocessing.sreality_api_dictionaries import *
from redataprocessing.sreality_description_download_decoding import *
from redataprocessing.sreality import *

collector=download_lists(category_main=1, category_type=2, locality_region_id=2)

#category_main=1
#category_main_input=category_main
#df=decode_collector(collector, category_main=category_main_input)

#for estate in r['_embedded']['estates']:
#    print(estate["name"])
#    get_area_from_name(estate["name"])

#estate=r['_embedded']['estates'][1]
#estate["name"]
#collector.items()[]



