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
- `dim_pytanie` - Pytania ankietowe
- `dim_semestr` - Semestry akademickie
- `dim_ankieta` - Dane dotyczące ankietyzacji
- `fact_oceny` - Wyniki dla poszczególnych pytań ankietowych

## Widok raportu
<img width="1418" height="802" alt="Zrzut ekranu 2025-12-26 165844" src="https://github.com/user-attachments/assets/366f4f80-7684-4dfe-9445-fe6c3968529d" />

<img width="1649" height="926" alt="Zrzut ekranu 2025-12-24 204847" src="https://github.com/user-attachments/assets/18ad4fe6-4008-4f02-9277-ce9ddecad594" />

<img width="1650" height="927" alt="Zrzut ekranu 2025-12-24 205031" src="https://github.com/user-attachments/assets/3788ff8c-3559-44d3-928a-a5e9fe1975b4" />






