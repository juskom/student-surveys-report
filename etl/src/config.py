import os


ANKIETY_DATA_PATH = "data/raw_data/ankiety"
ZAKLADY_DATA_PATH = "data/raw_data/zakłady"
PROCESSED_DATA_PATH = "data/transformed_data"

INSTYTUTY = {
    "ISEP": "Instytut Sterowania i Elektroniki Przemysłowej",
    "IETISIP": "Instytut Elektrotechniki Teoretycznej i Systemów Informacyjno-Pomiarowych",
    "IE": "Instytut Elektroenergetyki",
    "brak": "Brak przypisania do instytutu"
}


ZAKLADY = {
    # ISEP
    "ZEP": ("Zakład Elektroniki Przemysłowej", "ISEP"),
    "ZNE": ("Zakład Napędu Elektrycznego", "ISEP"),
    "ZS": ("Zakład Sterowania", "ISEP"),
    # IETISIP
    "ZETIIS": ("Zakład Elektrotechniki Teoretycznej i Informatyki Stosowanej", "IETISIP"),
    "ZSIP": ("Zakład Systemów Informacyjno-Pomiarowych", "IETISIP"),
    "ZWNIKE": ("Zakład Wysokich Napięć i Kompatybilności Elektromagnetycznej", "IETISIP"),
    # IE
    "ZSISE": ("Zakład Sieci i Systemów Elektroenergetycznych", "IE"),
    "ZTS": ("Zakład Techniki Świetlnej", "IE"),
    "ZAIAE": ("Zakład Aparatów i Automatyki Elektroenergetycznej", "IE"),
    "ZTIGE": ("Zakład Trakcji i Gospodarki Elektroenergetycznej", "IE"),

    "brak": ("Brak przypisania do zakładu", "brak"),
}