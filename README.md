# ETL System - Analiza Ankiet Studenckich

System ETL do przetwarzania i analizy ankiet ewaluacyjnych zajęć dydaktycznych na Wydziale Elektrycznym Politechniki Warszawskiej.

## Opis projektu

Aplikacja ETL (Extract, Transform, Load) służąca do:
- Ekstrakcji danych z plików Excel zawierających wyniki ankiet studenckich
- Transformacji danych do struktury wymiarowej
- Ładowania przygotowanych danych do analizy w Power BI

## Architektura

```
├── src/
│   ├── config.py
│   ├── extraction.py
│   ├── transformation.py
│   ├── loading.py
│   ├── utils.py
│   └── main.py
├── data/
│   ├── raw_data/
|   |   ├── ankiety - pliki Excel z wynikami ankietyzacji
|   |   └── zakłady - pliki CSV z pracownikami poszczególnych Zakładów
│   └── transformed_data/
├── .gitignore
├── requirements.txt  
└── README.md
```

## Model danych

- `dim_struktura` - Struktura organizacyjna (instytuty, zakłady)
- `dim_prowadzacy` - Prowadzący zajęcia
- `dim_przedmiot` - Przedmioty
- `dim_pytania` - Pytania ankietowe
- `dim_semestr` - Semestry akademickie
- `dim_ankiety` - Dane dotyczące ankietyzacji
- `fact_ankiety` - Wyniki dla poszczególnych pytań ankietowych



