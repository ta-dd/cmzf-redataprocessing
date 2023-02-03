# based on https://1.im.cz/seznam/blog/articles/import.pdf

#import pandas as pd

def category_main_cb_dict():
    dict={1:"byty", 2:"domy", 3:"pozemky", 4:"komerční", 5:"ostatní"}
    return(dict)

#category_main_cb_dict=pd.DataFrame.from_dict(category_main_cb_dict, orient="index", columns=["category_main_cb"])
#print(category_main_cb_dict)

def db_table_names_main():
    dict={1:"APARTMENTS", 2:"HOUSES", 3:"LANDPLOTS", 4:"COMMERCIAL", 5:"OTHERS"}
    return(dict)

def category_sub_cb_dict():
    dict={
    2:"1+kk", 
    3:"1+1", 
    4:"2+kk", 
    5:"2+2", 
    6:"2+kk",
    34:"garáž",
    52:"garážové stání"}
    #category_sub_cb_dict=pd.DataFrame.from_dict(category_sub_cb_dict, orient="index", columns=["category_sub_cb"])
    #print(category_sub_cb_dict)
    return(dict)

def category_type_cb_dict():
    dict={1:"prodej", 2:"nájem", 3:"dražba"}
    #category_type_cb_dict=pd.DataFrame.from_dict(category_type_cb_dict, orient="index", columns=["category_type_cb"])
    #print(category_type_cb_dict)
    return(dict)

def db_table_names_type():
    dict={1:"SALE", 2:"RENT", 3:"AUCTION"}
    return(dict)

def locality_region_id_dict():
    dict={10:"Praha", 11:"Středočeský kraj", 5:"Liberecký kraj"}
    #locality_region_id_dict=pd.DataFrame.from_dict(locality_region_id_dict, orient="index", columns=["locality_region_id"])
    #print(locality_region_id_dict)
    return(dict)

def description_items_dict():
    dict ={"Zlevněno":"discounted", 
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
    "Termín 1. prohlídky":"date_tour_first",
    "Termín 2. prohlídky":"date_tour_second",
    "Termín 3. prohlídky":"date_tour_third",
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
    return dict

columns_w_list = ["transport", "electricity", "traffic_communication", "water", "gas", "waste", "heating", "telecommunication"]

def create_db_table_name(category_main_cb, category_type_cb):
    db_table_name=db_table_names_main()[category_main_cb] + "_"+ db_table_names_type()[category_type_cb]
    return(db_table_name)