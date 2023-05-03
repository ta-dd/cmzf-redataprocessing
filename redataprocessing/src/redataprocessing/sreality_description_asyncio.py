"""Asynchronous download of description of sreality offers.

This module contains async functions for asynchronous requesting of
description data. Description data is requested for those offers that 
were already downloaded from sreality based on their hash_id identificator.

"""

import asyncio
import aiohttp
import ssl
import certifi
import random

import nest_asyncio

# async download of offer description
nest_asyncio.apply()

async def get_response(session: aiohttp.ClientSession, url: str) -> dict:
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    # choose a random user-agent from the list
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    ]

    headers = {'User-Agent': random.choice(user_agents)}

    try:
        async with session.get(url, ssl=sslcontext, headers=headers) as response:
            response_text =  await response.json()
            #here response can be processed further
            return response_text

    except aiohttp.ClientError as e:
        return f"Error occured for {url} : {e}"

async def main(urls: list, chunk_size: int) -> list:
    async with aiohttp.ClientSession() as session: 
        all_responses=[]
        chunks = [urls[i:i+chunk_size] for i in range(0, len(urls), chunk_size)]

        for chunk_idx, chunk in enumerate(chunks):
            #here you process first batch -> request go async

            tasks = [get_response(session, url) for url in chunk]
            #here they come together
            responses = await asyncio.gather(*tasks)

            finished_count=min(((chunk_idx+1)*chunk_size), len(urls))
            print(f'downloaded description of offers: {finished_count} out of {len(urls)}')
            
            #here we sqlite can be used
            #to name each observation you could use: response["_embedded"]["favourite"]["_links"]["self"]["href"][17:]
            all_responses=all_responses+responses
        return all_responses # returns list

def get_responses(urls: list, workers:int=5) -> list:
    """

    Parameters
    ----------
    urls : list :
        list of urls to API
        
    workers : int :
         (Default value = 5)

    Returns
    -------
    output_list - list of requested data in json
    """
    loop = asyncio.get_event_loop()
    output_list = loop.run_until_complete(main(urls, workers))
    
    # Getting rid of NaN rows
    output_list = [i for i in output_list if i not in [item for item in output_list if len(item) == 1]]
    return output_list
