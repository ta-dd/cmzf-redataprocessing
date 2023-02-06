# importing all packages
import pandas as pd
import numpy as np

import requests
import sqlite3
import sys
import certifi
import os

from datetime import date
from time import sleep 
from random import randint

from typing import Dict
import re 

from redataprocessing.sreality_api_dictionaries import *
from redataprocessing.sreality_description_download_decoding import *

# requesting information from sreality api

def download_lists(category_main: int, category_type: int, locality_region_id: int|list, category_sub: int|list=None):
    """

    Parameters
    ----------
    category_main :
        
    category_type :
        
    category_sub :
        
    locality_region_id :
        

    Returns
    -------

    """


    if isinstance(category_sub, int):
        category_sub_string=str(category_sub)
    elif isinstance(category_sub, list):
        category_sub_string = '%7C'.join(str(v) for v in category_sub)
    else:
        raise TypeError("category_sub: must be an integer or a list")
    
    if isinstance(locality_region_id, int):
        locality_region_id_string=str(locality_region_id)
    elif isinstance(locality_region_id, list):
        locality_region_id_string = '%7C'.join(str(v) for v in locality_region_id)
    else:
        raise TypeError("locality_region_id: must be an integer or a list")

    collector={}
    i=0
    run=True

    # solving issues with ssl requests (OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /etc/ssl/certs/ca-certificates.crt)
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), certifi.where())

    while run==True:
        
        base_url = "https://www.sreality.cz/api/cs/v2/estates"
        
        params={"category_main_cb":category_main,
            "category_type_cb":category_type,
            "per_page":60,
            "page":i}

        if len(locality_region_id)>0:
            params=params|{"locality_region_id":locality_region_id_string}
            
        if len(category_sub)>0:
            params=params|{"category_sub_cb":category_sub_string}

        r = requests.get(base_url, params=params, verify= True)

        print("starting sleep")
        sleep(randint(1,3))

        if r.status_code==404:
            print(f"Code {r.status_code} was returned.")
            break
        elif r.status_code==200:
            r_dict=r.json()

            if len(r_dict["_embedded"]["estates"]) == 0:
                print(f"downloading of offers finished")
                break

            collector[i]=r_dict
            
            print(f"downloaded list of offers: page {i+1}")

            i=i+1
            j=0

        else:
            if  j==3:
                print(f"Code {r.status_code} was returned.")
                break
            else:
                j=j+1
    return collector

# preparation of functions for decoding

def get_gps_lat_lon(estate_raw: Dict):
    """

    Parameters
    ----------
    estate_raw: Dict :
        
    Returns
    -------

    """
    gps_ = estate_raw['gps']
    return gps_['lat'], gps_['lon']

def get_flat_type_from_name(name: str):
    """

    Parameters
    ----------
    name: str :
        

    Returns
    -------

    """
    return name.split()[2]

def get_area_from_name(name: str):
    """

    Parameters
    ----------
    name: str :
        

    Returns
    -------

    """
    if category_main == 1:
        name_ = name.split()
        return int(''.join(re.findall('(\d*)', ''.join(name_[3:]))))
    else:
        name_ = re.sub("m2", "", name)
        name_ = name_.split()
        return int(''.join(re.findall('(\d*)', ''.join(name_))))

def get_company_details(estate_raw: Dict):
    """

    Parameters
    ----------
    estate_raw: Dict :
        

    Returns
    -------

    """
    try:
            company_id = estate_raw["_embedded"]["company"]["id"]
            company_name = estate_raw["_embedded"]["company"]["name"]
    except (KeyError):
            company_id = np.nan
            company_name = np.nan

    return company_id, company_name

# wrapping up all decoding

def decode_collector(collector: list, category_main: int):
    """

    Parameters
    ----------
    collector :
        

    Returns
    -------

    """
    estates_individual = {}

    for page, r in collector.items():
        for estate in r['_embedded']['estates']: 

            estate_relevant = pd.Series(dtype="object")

            estate_relevant['price'] = int(estate['price'])
            estate_relevant['price_czk'] = int(estate['price_czk']["value_raw"])
            estate_relevant['price_czk_unit'] = estate['price_czk']["unit"]
            estate_relevant['price_czk_name'] = estate['price_czk']["name"]
            estate_relevant['area'] = get_area_from_name(estate['name'])

            lat, lon = get_gps_lat_lon(estate)
            estate_relevant.loc['lat'] = lat
            estate_relevant.loc['lon'] = lon
            estate_relevant['locality'] = estate['locality']
            if category_main == 1:
                estate_relevant['apartment_type'] = get_flat_type_from_name(estate['name'])
            estate_relevant['is_auction'] = estate['is_auction']
            estate_relevant['exclusively_at_rk'] = estate['exclusively_at_rk']

            estate_relevant['category_main'] = estate["seo"]["category_main_cb"]
            estate_relevant['category_sub'] = estate["seo"]["category_sub_cb"]
            estate_relevant['category_type'] = estate["seo"]["category_type_cb"]

            company_id, company_name = get_company_details(estate)
            estate_relevant['company_id'] = company_id
            estate_relevant['company_name'] = company_name
            estate_relevant["date_download"]=str(date.today())
            
            estates_individual[estate['hash_id']] = estate_relevant
    
    # transforming into pandas df
    df = pd.concat(estates_individual).unstack()
    df.reset_index(inplace=True)
    df = df.rename(columns = {'index':'hash_id'})
    
    return df

# creating ultimated function for downloading and transforming into pandas df
def download_re_offers(category_main: int, 
    category_type: int, 
    locality_region_id: int, 
    category_sub: list=None):
    """

    Parameters
    ----------
    category_main :
        
    category_type :
        
    category_sub :
        
    locality_region_id :
        
    Returns
    -------

    """

    category_main_input=category_main
    category_type_input=category_type
    category_sub_input=category_sub
    locality_region_id_input=locality_region_id

    collector=download_lists(category_main=category_main_input, 
    category_type=category_type_input, 
    category_sub=category_sub_input, 
    locality_region_id=locality_region_id_input)

    df=decode_collector(collector, category_main=category_main_input)
    
    if isinstance(locality_region_id, int):
        df["locality_region_id"][0]
    elif isinstance(locality_region_id, list):
        df["locality_region_id"] = locality_region_id_input[0]
    else:
        print("TypeError: locality_region_id must be an integer or a list")
    
    return df

# Saving data (SQLite)

def save_re_offers(df: pd.DataFrame, path_to_sqlite: str, category_main: int, category_type: int):
    """

    Parameters
    ----------
    df :
        
    path_to_sqlite :
        

    Returns
    -------

    """
    con = sqlite3.connect(path_to_sqlite) # We must choose the name for our DB !

    # Creates a table or appends if exists
    db_table_name=create_db_table_name(category_main=category_main, category_type=category_type)
    db_table_name_offers="OFFERS_"+db_table_name

    # if table with offers exists - addition of columns that are not in description table
    # checking if db exists
    c=con.cursor()
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}' ".format(db_table_name_offers))
    if c.fetchone()[0]==1:
        cursor = con.execute('select * from {}'.format(db_table_name_offers))
        list_of_colnames=list(map(lambda x: x[0], cursor.description))

        for i in df.columns:
            if i not in list_of_colnames:
                c.execute("ALTER TABLE {} ADD {} VARCHAR(100);".format(db_table_name_offers, i))

    df.to_sql(name = db_table_name_offers, con= con, index = False, if_exists = 'append')
    # Loading again: df = pd.read_sql('SELECT * FROM OFFERS_TABLE', con = con)

    # Closing the connection
    con.close()

def get_re_offers(path_to_sqlite: str, category_main: str, category_type: str, 
locality_region: str|list, category_sub: str|list=None):
    """

    Parameters
    ----------
    path_to_sqlite :
        
    category_main :
        
    category_type :
        
    category_sub :
        
    locality_region_id :
        

    Returns
    -------

    """

    # inputs to further functions
    if isinstance(category_main, str):
        if category_main not in category_main_dict.keys():
            raise ValueError("category_main: must be one of %r." % list(category_main_dict.keys()))
        else:
            category_main_input=category_main_dict[category_main]
    else:
        raise TypeError("category_main: must be a string")

    if isinstance(category_type, str):
        if category_type not in category_type_dict.keys():
            raise ValueError("category_type: must be one of %r." % list(category_type_dict.keys()))
        else:
            category_type_input=category_type_dict[category_type]
    else:
        raise TypeError("category_type: must be a string")
    
    category_sub_input = []
    if isinstance(category_sub, str):
        if category_sub not in category_sub_dict.keys():
                raise ValueError("locality_region: must be one or more of %r." % list(category_sub_dict.keys()))
        category_sub_input.append(category_sub_dict[category_sub])
    elif isinstance(category_sub, list):
       for idx in category_sub:
            if idx not in category_sub_dict.keys():
                raise ValueError("category_sub: must be one or more of %r." % list(category_sub_dict.keys()))
            category_sub_input.append(category_sub_dict[idx])
    else:
        raise TypeError("category_sub: must be a list of string or a string")

    locality_region_id_input = []
    if isinstance(locality_region, str):
        if locality_region not in locality_region_id_dict.keys():
                raise ValueError("locality_region: must be one or more of %r." % list(locality_region_id_dict.keys()))
        locality_region_id_input.append(locality_region_id_dict[locality_region])
    elif isinstance(locality_region, list):
       for idx in locality_region:
            if idx not in locality_region_id_dict.keys():
                raise ValueError("locality_region: must be one of %r." % list(locality_region_id_dict.keys()))
            locality_region_id_input.append(locality_region_id_dict[idx])
    elif len(locality_region)>1:
        raise ValueError("locality_region: this package version is not able to handle more than one value")
    else:
        raise TypeError("locality_region: must be a list of strings or a string")
    
    if isinstance(path_to_sqlite, str):
        path_to_sqlite_input=path_to_sqlite
    else:
        raise TypeError("path_to_sqlite: must be a string")
    
    # starting functions
    print("initiating download of offers")

    df=download_re_offers(category_main=category_main_input, 
    category_type=category_type_input, 
    category_sub=category_sub_input, 
    locality_region_id=locality_region_id_input)

    db_table_name=create_db_table_name(category_main=category_main_input, category_type=category_type_input)
    db_table_name_offers="OFFERS_"+db_table_name

    print("saving offers to database (table name {})".format(db_table_name_offers))

    save_re_offers(df, 
    path_to_sqlite=path_to_sqlite_input, 
    category_main=category_main_input, 
    category_type=category_type_input)

    print("saved offers to database (table name {})".format(db_table_name_offers))

    print("initiating download of description of offers")

    get_re_offers_description(path_to_sqlite=path_to_sqlite_input, 
    category_main=category_main_input, category_type=category_type_input)

# INPUTS
#sleep(2)
#path_to_sqlite='estate_data.sqlite'

#category_main = "apartments" # 1=byty, 2=domy, 3=pozemky, 4=komerční, 5=ostatní
#category_type = "sale" # 1=prodej, 2=nájem, 3=dražba
#category_sub = [] # 34=garáže, 52=garážové stání
#locality_region = ["Královéhradecký kraj"] #10=Praha, 11=Středočeský kraj, 5: Liberecký kraj, 1: Českobudějovický kraj

#category_main = 1 # 1=byty, 2=domy, 3=pozemky, 4=komerční, 5=ostatní
#category_type = 1 # 1=prodej, 2=nájem, 3=dražba
#category_sub = [] # 34=garáže, 52=garážové stání
#locality_region_id = [13] #10=Praha, 11=Středočeský kraj, 5: Liberecký kraj, 1: Českobudějovický kraj

#get_re_offers(path_to_sqlite="estate_data.sqlite", 
#category_main="apartments", 
#category_type="sale", 
#category_sub=[], 
#locality_region=["Královéhradecký kraj"])