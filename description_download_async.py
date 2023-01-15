import asyncio
import aiohttp
import pandas as pd
import numpy as np

file_name="Prague_apartments_sale_2023-01-14.gzip"

desc_indices=pd.read_parquet(file_name, columns=["hash_id"])
desc_indices=desc_indices.drop_duplicates()

urls=["https://www.sreality.cz/api/cs/v2/estates/"+str(i) for i in desc_indices["hash_id"]]

items_dict={"Zlevněno":"discounted", 
"Původní cena":"price_original", 
"ID zakázky":"id_order", 
"Aktualizace":"date_update", 
"Stavba":"building_type", 
"Stav objektu":"building_condition", 
"Umístění objektu":"building_location", 
"Užitná plocha":"area_net", 
"Plocha podlahová":"area_floor", 
"Celková cena":"price_total", 
"Poznámka k ceně":"price_note", 
"Doprava":"transport", 
"Plocha zastavěná":"area_build_up", 
"Datum nastěhování":"date_moving_in", 
"Rok kolaudace":"date_building_approval", 
"Vybavení":"equipped", 
"Elektřina":"electricity", 
"Komunikace":"traffic_communication", 
"Bezbariérový":"barrier_free", 
"ID":"id", 
#"Cena":"price", 
"Energetická náročnost budovy":"energy_efficient_rating", 
"Výtah":"lift", 
"Typ domu":"building_floor_type", 
"Podlaží":"building_floor", 
"Voda":"water", 
"Plyn":"gas", 
"Odpad":"waste", 
"Topení":"heating", 
"Telekomunikace":"telecommunication", 
"Rok rekonstrukce":"date_year_reconstruction", 
"Průkaz energetické náročnosti budovy":"energy_efficient_rating_card", 
"Stav":"availability", 
"Datum zahájení prodeje":"date_offer_start", 
"Ukazatel energetické náročnosti budovy":"energy_efficient_rating_index", 
"Datum prohlídky":"date_tour", 
"Datum prohlídky do":"date_tour_to", 
"Plocha zahrady":"area_garden",
"Výška stropu":"ceiling_height",
"Parkování":"parking",
"Cena za m²":"price_sqm",
"Počet kanceláří":"office_count",
"Garáž":"garage",
"Počet míst":"place_count",
"Bazén":"basin",
"Plocha pozemku":"area_landplot",
"Velikost podílu":"share_size",
"Vyvolávací cena":"auction_initial_price",
"Znalecký posudek":"expert_opinion_official",
"Minimální příhoz":"auction_min_bid", 
"Aukční jistina":"auction_principal",
"Druh dražby":"auction_type",
"Místo konání dražby":"auction_place",
"Datum konání dražby":"auction_date",
"Dražební vyhláška":"auction_decree",
"Posudek znalce":"expert_opinion"}

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
            all_responses=all_responses+responses
        return all_responses

loop=asyncio.new_event_loop()
my_resp=loop.run_until_complete(main(urls, 5))
loop.close()