"""Example NumPy style docstrings.

This module demonstrates documentation as specified by the `NumPy
Documentation HOWTO`_. Docstrings may extend over multiple lines. Sections
are created with a section header followed by an underline of equal length.

Example
-------
Examples can be given using either the ``Example`` or ``Examples``
sections. Sections support any reStructuredText formatting, including
literal blocks::

    $ python example_numpy.py


Section breaks are created with two blank lines. Section breaks are also
implicitly created anytime a new section starts. Section bodies *may* be
indented:

Notes
-----
    This is an example of an indented section. It's like any other section,
    but the body is indented to help it stand out from surrounding text.

If a section is indented, then a section break is created by
resuming unindented text.

Attributes
----------
module_level_variable1 : int
    Module level variables may be documented in either the ``Attributes``
    section of the module docstring, or in an inline docstring immediately
    following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.


.. _NumPy Documentation HOWTO:
   https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

"""

import pandas as pd
import numpy as np
import sqlite3

from typing import Dict

from tqdm.auto import tqdm

from redataprocessing.sreality_api_dictionaries import *
from redataprocessing.sreality_description_asyncio import *

# preparation of urls for async
def getting_offers_without_downloaded_description(path_to_sqlite: str, category_main: int, category_type: int) -> list:
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

def urls_from_indices(indices:list) -> list:
    """

    Parameters
    ----------
    indices : list of hash_ids
        
    Returns
    -------
    urls - list of urls to APIs
    """
    urls=["https://www.sreality.cz/api/cs/v2/estates/"+str(i) for i in indices]
    return urls

# %%
# preparation of functions for decoding

def note_missing_values(r_dict_names_all:Dict) -> None:
    """

    Parameters
    ----------
    r_dict_names_all : dictionary with Czech and English column names to be scrapped
        
    Returns
    -------
    nothing (prints the missing values which could be added to dictionary and be scrapped)
    """
    if  len(r_dict_names_all[~r_dict_names_all.isin(description_items_dict.keys())])>0:
        print("Add these values to description_items_dict in sreality_api_dictionaries.py:")
        print(r_dict_names_all[~r_dict_names_all.isin(description_items_dict.keys())])
    else:
        return None

def individual_description_into_pd_df(description_individual) -> pd.DataFrame:
    """

    Parameters
    ----------
    description_individual :    

    Returns
    -------
    dataframe
    """
    df_desc = pd.concat(description_individual).unstack()
    df_desc["equipped"]=df_desc["equipped"].map({True: "ano", False: "ne", "Částečně":"částečně"}) 
    df_desc.reset_index(inplace=True)
    df_desc = df_desc.rename(columns = {'index':'hash_id'})
    return df_desc

# decoding of requests
def description_decoding(responses_list: list) -> pd.DataFrame:
    """

    Parameters
    ----------
    responses_list : list : list of responses of real estate descriptions downloaded from sreality
    
    Returns
    -------
    decoded dataframe
    """
        
    description_individual = {}
    r_dict_names_all=pd.Series(dtype="object")
    r_dict_types_all=pd.DataFrame(columns=["name", "type"])
    
    total=len(responses_list)

    with tqdm(total=total, desc="decoding responses with description of offers: ") as pbar:
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
        
            pbar.update(1)

              
    note_missing_values(r_dict_names_all)

    df_final=individual_description_into_pd_df(description_individual)

    return df_final

# %% [markdown]
# save of description data to SQLite

# We transform columns with list so we could save to DB
def transformer(value) -> str:
    """

    Parameters
    ----------
    value : value to be transformed        

    Returns
    -------
    string sperating the values with double spaces
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
    df : pandas data frame : dataframe to be saved
        
    path_to_sqlite : str : 
        path to sqlite database where the dataframe will be stored
        
    category_main : int : code of main real estate category

    category_type : int : code of real estate type

    Returns
    -------
    nothing (SQLite will be saved)
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

def get_re_offers_description(path_to_sqlite: str, category_main: int, category_type: int) -> None:
    """

    Parameters
    ----------
    path_to_sqlite : str : 
        path to sqlite database where table with offers is already stored
    category_main : int : 
        code of main real estate category
    category_type : 
        code of real estate type
        
    Returns
    -------
    This function downloads description of all offers of chosen category in the database that do not have the description already downloaded.
    Creates a table in the sqlite database. If the table already exists it appends new data to the respective table.

    """
    
    category_main_input=category_main
    category_type_input=category_type
    path_to_sqlite_input=path_to_sqlite
    
    indices=getting_offers_without_downloaded_description(path_to_sqlite=path_to_sqlite_input, 
    category_main=category_main_input, 
    category_type=category_type_input)

    if len(indices)==0:
        print("all descriptions of offers already loaded")
        return None

    urls=urls_from_indices(indices)
    output_list=get_responses(urls, workers=20)

    df = description_decoding(output_list)

    db_table_name=create_db_table_name(category_main=category_main_input, category_type=category_type_input)
    db_table_name_description="DESCRIPTION_"+db_table_name
    print("saving description of offers to database (table {})".format(db_table_name_description))

    save_to_db(df, path_to_sqlite=path_to_sqlite_input, category_main=category_main_input, category_type=category_type_input)
    print("saved description of offers to database (table {})".format(db_table_name_description))