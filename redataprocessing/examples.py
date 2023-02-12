import redataprocessing as rdp

rdp.get_re_offers(path_to_sqlite="estate_data.sqlite", 
category_main="apartments", 
category_type="sale", 
locality_region=["Královéhradecký kraj"])
