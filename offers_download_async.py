import asyncio
import aiohttp
import pandas as pd

file_name="Prague_apartments_sale_2023-01-14.gzip"

df=pd.read_parquet(file_name, columns=["hash_id"])
df.head()

df=df.head(10)
df.shape

urls=["https://www.sreality.cz/api/cs/v2/estates/"+str(i) for i in df["hash_id"]]

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

            tasks = [get_response(session, url) for url in urls]
            #here they come together
            responses = await asyncio.gather(*tasks)
            
            #responses can be saved -> csv, sqlite etc
            all_responses.append(responses)
        return all_responses

loop = asyncio.get_event_loop()
my_resp=loop.run_until_complete(main(urls, 5))