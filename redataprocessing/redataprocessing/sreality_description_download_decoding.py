# %%
import pandas as pd
import numpy as np
import sqlite3

import asyncio
import aiohttp
import ssl
import certifi

import nest_asyncio

from redataprocessing.sreality_api_dictionaries import *

# async download of offer description

# preparation of urls for async
def getting_offers_without_downloaded_description(path_to_sqlite: str, category_main: int, category_type: int):
    """

    Parameters
    ----------
    path_to_sqlite : string of path to sqlite database where table with offers is already stored
        
    Returns
    -------
    This function downloads description of all offers that do not have the description already downloaded.
    Creates a table in the sqlite database. If the table already exists it appends new data to the table.

    """
    con = sqlite3.connect(path_to_sqlite)

    c = con.cursor()

    # getting table names
    db_table_name=create_db_table_name(category_main, category_type)
    db_table_name_offers="OFFERS_"+db_table_name
    db_table_name_description="DESCRIPTION_"+db_table_name

    # checking if db exists
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}' ".format(db_table_name_description))
    
    # loading indices for which no description was downloaded
    if c.fetchone()[0]==1:
        # if table with description exists
        indices = pd.read_sql("SELECT hash_id FROM {} WHERE hash_id not in (SELECT hash_id FROM {})".format(db_table_name_offers, db_table_name_description), con=con)
    else:
        # loading descriptions for the first time - table with description does not exist
        indices = pd.read_sql("SELECT hash_id FROM {}".format(db_table_name_offers), con=con)
    c.close()
    con.close()

    indices=indices["hash_id"]
    return indices

def urls_from_indices(indices):
    """

    Parameters
    ----------
    indices :
        

    Returns
    -------

    """
    urls=["https://www.sreality.cz/api/cs/v2/estates/"+str(i) for i in indices]
    return urls

# async download
nest_asyncio.apply()

async def get_response(session, url):
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    try:
        async with session.get(url, ssl=sslcontext) as response:
            response_text =  await response.json()
            #here response can be processed further
            return response_text
    except aiohttp.ClientError as e:
        return f"Error occured for {url} : {e}"

async def main(urls, chunk_size):
    async with aiohttp.ClientSession() as session: 
        all_responses=[]
        chunks = [urls[i:i+chunk_size] for i in range(0, len(urls), chunk_size)]

        for chunk_idx, chunk in enumerate(chunks):
            #here you process first batch -> request go async

            tasks = [get_response(session, url) for url in chunk]
            #here they come together
            responses = await asyncio.gather(*tasks)

            print(f'downloaded description of offers: {(chunk_idx+1)*chunk_size} out of {len(urls)}')
            
            #here we sqlite can be used
            #to name each observation you could use: response["_embedded"]["favourite"]["_links"]["self"]["href"][17:]
            all_responses=all_responses+responses
        return all_responses # returns list

def get_responses(urls, workers=5):
    """

    Parameters
    ----------
    urls :
        
    workers :
         (Default value = 5)

    Returns
    -------

    """
    loop = asyncio.get_event_loop()
    output_list = loop.run_until_complete(main(urls, workers))
    
    # Getting rid of NaN rows
    output_list = [i for i in output_list if i not in [item for item in output_list if len(item) == 1]]
    return output_list

# %%
# preparation of functions for decoding

def note_missing_values(r_dict_names_all):
    """

    Parameters
    ----------
    r_dict_names_all :
        

    Returns
    -------

    """
    print("Add these values to description_items_dict in sreality_api_dictionaries.py:")
    print(r_dict_names_all[~r_dict_names_all.isin(description_items_dict.keys())])

def individual_description_into_pd_df(description_individual):
    """

    Parameters
    ----------
    description_individual :
        

    Returns
    -------

    """
    df_desc = pd.concat(description_individual).unstack()
    df_desc["equipped"]=df_desc["equipped"].map({True: "ano", False: "ne", "Částečně":"částečně"}) 
    df_desc.reset_index(inplace=True)
    df_desc = df_desc.rename(columns = {'index':'hash_id'})
    return df_desc

# decoding of requests
def description_decoding(responses_list):
    """

    Parameters
    ----------
    responses_list :
        

    Returns
    -------

    """
        
    description_individual = {}
    r_dict_names_all=pd.Series(dtype="object")
    r_dict_types_all=pd.DataFrame(columns=["name", "type"])

    for r_dict in responses_list:
            try:
                info_relevant = pd.Series(dtype="object")
                info_relevant["description"]=r_dict["text"]["value"]

                r_dict_values=pd.DataFrame(r_dict["items"], columns =['type', 'name', 'value'])

                r_dict_names=r_dict_values["name"]
                r_dict_names_all=pd.concat([r_dict_names_all, r_dict_names[~r_dict_names.isin(r_dict_names_all)]])

                r_dict_types=r_dict_values[["type", "name"]]
                r_dict_types_all=pd.concat([r_dict_types_all, r_dict_types.loc[~r_dict_types["name"].isin(r_dict_types_all["name"]),:]])

                for name_raw in description_items_dict.keys():

                        name_clean=description_items_dict[name_raw]

                        if name_raw not in r_dict_names.values:
                                info_relevant[name_clean]=np.nan
                        elif r_dict_values[r_dict_names==name_raw]["type"].all()=="set":
                                index_nr=int(r_dict_values.index[r_dict_values['name'] == name_raw].tolist()[0])
                                info_relevant[name_clean]=r_dict_values["value"][r_dict_values["name"]==name_raw][index_nr][0]["value"].values[0]
                                del index_nr
                        else:
                                info_relevant[name_clean]=r_dict_values["value"][r_dict_values["name"]==name_raw].values[0]

                description_individual[r_dict["_embedded"]["favourite"]["_links"]["self"]["href"][17:]] = info_relevant
            except:
                print("Something wrong. I guess, the offer disappeared just a moment ago.")
    note_missing_values(r_dict_names_all)

    df_final=individual_description_into_pd_df(description_individual)

    return df_final

# %% [markdown]
# save of description data to SQLite

# We transform columns with list so we could save to DB
def transformer(value):
    """

    Parameters
    ----------
    value :
        

    Returns
    -------

    """
    if type(value) == list:
        string = ""
        for i in value:
            string += i['value'] + "  "
        return string[:-2]

def save_to_db(df: pd.DataFrame, path_to_sqlite: str, category_main: int, category_type: int):
    """

    Parameters
    ----------
    df : pandas data frame
        
    path_to_sqlite : string of path to sqlite database where the dataframe will be stored
        
    columns_w_list :
         (Default value = columns_w_list)

    Returns
    -------

    """
    
    for column in columns_w_list:
        df[column] = df[column].apply(lambda row: transformer(row))

    # Creates a table or appends if exists
    con = sqlite3.connect(path_to_sqlite)
    
    db_table_name=create_db_table_name(category_main, category_type)
    db_table_name_description="DESCRIPTION_"+db_table_name

    # if table with description exists - addition of columns that are not in description table
    # checking if db exists
    c=con.cursor()
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}' ".format(db_table_name_description))

    if c.fetchone()[0]==1:
        cursor = con.execute('select * from {}'.format(db_table_name_description))
        list_of_colnames=list(map(lambda x: x[0], cursor.description))

        for i in df.columns:
            if i not in list_of_colnames:
                c.execute("ALTER TABLE {} ADD {} VARCHAR(100);".format(db_table_name_description, i))

    df.to_sql(name = db_table_name_description, con = con, index = False, if_exists = 'append')

    # Closing the connection
    con.close()

def get_re_offers_description(path_to_sqlite, category_main, category_type):
    """

    Parameters
    ----------
    path_to_sqlite : string of path to sqlite database where table with offers is already stored
    category_main : 
    category_type : 
        
    Returns
    -------
    This function downloads description of all offers that do not have the description already downloaded.
    Creates a table in the sqlite database. If the table already exists it appends new data to the table.

    """
    
    category_main_input=category_main
    category_type_input=category_type
    path_to_sqlite_input=path_to_sqlite
    
    indices=getting_offers_without_downloaded_description(path_to_sqlite=path_to_sqlite_input, 
    category_main=category_main_input, 
    category_type=category_type_input)

    urls=urls_from_indices(indices)
    output_list=get_responses(urls, workers=20)

    print("decoding responses of descriptions")
    df = description_decoding(output_list)
    print("finished decoding responses of descriptions")

    db_table_name=create_db_table_name(category_main=category_main_input, category_type=category_type_input)
    db_table_name_description="DESCRIPTION_"+db_table_name
    print("saving description of offers to database (table {})".format(db_table_name_description))

    save_to_db(df, path_to_sqlite=path_to_sqlite_input, category_main=category_main_input, category_type=category_type_input)
    print("saved description of offers to database (table {})".format(db_table_name_description))