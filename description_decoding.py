import pandas as pd
import numpy as np

file_name="Prague_apartments_sale_2023-01-14_desc_list"

#my_resp= ((add sqlite code))

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

def note_missing_values(r_dict_names_all):
        print("Add these values to your dictionary:")
        print(r_dict_names_all[~r_dict_names_all.isin(items_dict.keys())])

def individual_description_into_pd_df(description_individual):
        df_desc = pd.concat(description_individual).unstack()
        df_desc["equipped"]=df_desc["equipped"].map({True: "ano", False: "ne", "Částečně":"částečně"}) 
        df_desc.reset_index(inplace=True)
        df_desc = df_desc.rename(columns = {'index':'hash_id'})
        return df_desc

def description_decoding(responses_list):
        description_individual = {}
        r_dict_names_all=pd.Series(dtype="object")
        r_dict_types_all=pd.DataFrame(columns=["name", "type"])

        for r_dict in responses_list:
                
                info_relevant = pd.Series(dtype="object")
                info_relevant["description"]=r_dict["text"]["value"]

                r_dict_values=pd.DataFrame(r_dict["items"], columns =['type', 'name', 'value'])

                r_dict_names=r_dict_values["name"]
                r_dict_names_all=pd.concat([r_dict_names_all, r_dict_names[~r_dict_names.isin(r_dict_names_all)]])

                r_dict_types=r_dict_values[["type", "name"]]
                r_dict_types_all=pd.concat([r_dict_types_all, r_dict_types.loc[~r_dict_types["name"].isin(r_dict_types_all["name"]),:]])

                for name_raw in items_dict.keys():

                        name_clean=items_dict[name_raw]

                        if name_raw not in r_dict_names.values:
                                info_relevant[name_clean]=np.nan
                        elif r_dict_values[r_dict_names==name_raw]["type"].all()=="set":
                                index_nr=int(r_dict_values.index[r_dict_values['name'] == name_raw].tolist()[0])
                                info_relevant[name_clean]=r_dict_values["value"][r_dict_values["name"]==name_raw][index_nr][0]["value"].values[0]
                                del index_nr
                        else:
                                info_relevant[name_clean]=r_dict_values["value"][r_dict_values["name"]==name_raw].values[0]

                description_individual[r_dict["_embedded"]["favourite"]["_links"]["self"]["href"][17:]] = info_relevant
        
        note_missing_values(r_dict_names_all)

        df_final=individual_description_into_pd_df(description_individual)

        return df_final

df= description_decoding(my_resp)

df.to_parquet((file_name[:-5]+"_desc.gzip"))