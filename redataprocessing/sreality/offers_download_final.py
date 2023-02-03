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

from sreality_api_dictionaries import *
from description_download_decoding_final import *


# INPUTS
#path_to_sqlite='estate_data.sqlite'

#category_main = 1 # 1=byty, 2=domy, 3=pozemky, 4=komerční, 5=ostatní
#category_type = 1 # 1=prodej, 2=nájem, 3=dražba
#category_sub = [] # 34=garáže, 52=garážové stání
#locality_region_id = [10] #10=Praha, 11=Středočeský kraj, 5: Liberecký kraj, 1: Českobudějovický kraj

# requesting information from sreality api

def download_lists(category_main, category_type, category_sub, locality_region_id):
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

    category_sub_string = '%7C'.join(str(v) for v in category_sub)
    locality_region_id_string = '%7C'.join(str(v) for v in locality_region_id)

    collector={}
    i=0
    run=True

    # solving issues with ssl requests (OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /etc/ssl/certs/ca-certificates.crt)
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), certifi.where())

    while run==True:
        
        base_url = "https://www.sreality.cz/api/cs/v2/estates"
        
        params={"category_main_cb":category_main,
            "category_type_cb":category_type,
            "locality_region_id":locality_region_id_string,
            "per_page":60,
            "page":i}
            
        if len(category_sub)>0:
            params=params|{"category_sub_cb":category_sub_string}


        r = requests.get(base_url, params=params, verify= True)

        print("starting sleep")
        sleep(randint(1,3))

        if r.status_code==404:
            break
        elif r.status_code==200:
            r_dict=r.json()

            if len(r_dict["_embedded"]["estates"]) == 0:
                print(f"Page {i+1} is blank.")
                break

            collector[i]=r_dict
            
            print(f"Page {i+1} was scraped.")

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
  
def get_area_from_name(name: str):
    """

    Parameters
    ----------
    name: str :
        

    Returns
    -------

    """
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

def decode_collector(collector):
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
            estate_relevant['type'] = estate['type']
            estate_relevant['category'] = estate['category']
            estate_relevant['is_auction'] = estate['is_auction']
            estate_relevant['exclusively_at_rk'] = estate['exclusively_at_rk']

            estate_relevant['category_main'] = estate["seo"]["category_main"]
            estate_relevant['category_sub'] = estate["seo"]["category_sub"]
            estate_relevant['category_type'] = estate["seo"]["category_type"]

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
def download_re_offers(category_main, 
    category_type, 
    category_sub, 
    locality_region_id):
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

    collector=download_lists(category_main=category_main, 
    category_type=category_type, 
    category_sub=category_sub, 
    locality_region_id=locality_region_id)

    df=decode_collector(collector)

    return df

# Saving data (SQLite)

def save_re_offers(df, path_to_sqlite, category_main, category_type):
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
    db_table_name=create_db_table_name(category_main, category_type)
    db_table_name_offers="OFFERS_"+db_table_name

    df.to_sql(name = db_table_name_offers, con= con, index = False, if_exists = 'append')
    # Loading again: df = pd.read_sql('SELECT * FROM OFFERS_TABLE', con = con)

    # Closing the connection
    con.close()

def get_re_offers(path_to_sqlite, category_main, category_type, category_sub, locality_region_id):
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
    
    df=download_re_offers(category_main=category_main, 
    category_type=category_type, 
    category_sub=category_sub, 
    locality_region_id=locality_region_id)

    save_re_offers(df, path_to_sqlite, category_main, category_type)

    get_re_offers_description(path_to_sqlite, category_main, category_type)

#get_re_offers(path_to_sqlite=path_to_sqlite, category_main=category_main, category_type=category_type, category_sub=category_sub, locality_region_id=locality_region_id)