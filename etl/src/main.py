from extraction import load_excel_files, load_zaklady_data
from transformation import *
from loading import save_all_dimensions, save_institute_data
from config import ZAKLADY_DATA_PATH, ANKIETY_DATA_PATH, PROCESSED_DATA_PATH

def main():
    print("Starting ETL process...")

    print("\nEXTRACTION PHASE")
    print("-" * 50)

    try:
        excel_data = load_excel_files(ANKIETY_DATA_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}")
        print("Proces ETL przerwany.\n")
        return
    
    zaklady_data = load_zaklady_data(ZAKLADY_DATA_PATH)

    print("\nTRANSFORMATION PHASE")
    print("-" * 50)
    
    print("Building dimensions...")
    dim_struktura = build_struktura_wydzialu()
    dim_prowadzacy = build_dim_prowadzacy(excel_data['prowadzacy'], zaklady_data, dim_struktura)
    dim_przedmiot = build_dim_przedmiot(excel_data['przedmioty'])
    dim_pytania = build_dim_pytania(excel_data['questions'])
    dim_semestr = build_dim_semestr(excel_data['raw_files'])
    dim_ankiety, enriched_files = build_dim_ankiety(excel_data['raw_files'], dim_prowadzacy, dim_przedmiot, dim_semestr)
    fact_ankiety = build_fact_ankiety(enriched_files, dim_pytania)

    dimensions = {
        'dim_struktura': dim_struktura,
        'dim_prowadzacy': dim_prowadzacy,
        'dim_przedmiot': dim_przedmiot,
        'dim_pytanie': dim_pytania,
        'dim_semestr': dim_semestr,
        'dim_ankieta': dim_ankiety,
        'fact_oceny': fact_ankiety
    }
   
    print("\nLOADING PHASE")
    print("-" * 50)
    
    save_all_dimensions(dimensions, PROCESSED_DATA_PATH)

    save_institute_data(dimensions, PROCESSED_DATA_PATH)
    
    print("\nETL process completed successfully!")
    
    print("\nSUMMARY:")
    print("-" * 50)
    for name, df in dimensions.items():
        if df is not None:
            print(f"  {name}: {len(df)} records")
        else:
            print(f"  {name}: None")

if __name__ == "__main__":
    main()