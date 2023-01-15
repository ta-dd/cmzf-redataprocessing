import asyncio
import aiohttp
import pandas as pd

file_name="Prague_apartments_sale_2023-01-14.gzip"

desc_indices=pd.read_parquet(file_name, columns=["hash_id"])
desc_indices=desc_indices.drop_duplicates()

urls=["https://www.sreality.cz/api/cs/v2/estates/"+str(i) for i in desc_indices["hash_id"]]

async def get_response(session, url):
    try:
        async with session.get(url) as response:
            response_text =  await response.json() #parse response to json/ o response.text() for text
            #here you can process each further
            return response_text
    except aiohttp.ClientError as e:
        return f"Error occured for {url} : {e}"

async def main(urls, chunk_size):
    async with aiohttp.ClientSession() as session: 
        all_responses=[]
        chunks = [urls[i:i+chunk_size] for i in range(0, len(urls), chunk_size)]
        for chunk_idx, chunk in enumerate(chunks):
            print(f'running chunk {chunk_idx+1} out of {len(chunks)} chunks ({chunk_size} items)')
            #here you process first batch -> request go async

            tasks = [get_response(session, url) for url in chunk]
            #here they come together
            responses = await asyncio.gather(*tasks)
            
            #responses can be saved -> csv, sqlite etc
            #here we incorporate sqlite
            #to name each observation you could use: response["_embedded"]["favourite"]["_links"]["self"]["href"][17:]
            all_responses=all_responses+responses
        return all_responses

loop=asyncio.new_event_loop()
my_resp=loop.run_until_complete(main(urls, 5))
loop.close()