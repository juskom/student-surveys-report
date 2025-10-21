import os
import pandas as pd
from datetime import datetime

def save_all_dimensions(dimensions, output_path):
    transformed_data_path = os.path.join(output_path)
    os.makedirs(transformed_data_path, exist_ok=True)
    
    saved_count = 0
    failed_count = 0
    
    for dimension_name, df in dimensions.items():
        try:
            if df is not None and not df.empty:
                file_path = os.path.join(transformed_data_path, f"{dimension_name}.csv")

                df.to_csv(file_path, index=False, encoding='utf-8')

                saved_count += 1
                
            elif df is not None and df.empty:
                print(f"{dimension_name}: Empty DataFrame - skipped")
                
            else:
                print(f"{dimension_name}: None - skipped")
                
        except Exception as e:
            print(f"Failed to save {dimension_name}: {e}")
            failed_count += 1
    
    print(f"\nLOADING SUMMARY:")
    print(f"  Successfully saved: {saved_count} files")
    print(f"  Failed: {failed_count} files")
    print(f"  Output directory: {transformed_data_path}")
    

def save_institute_data(dimensions, output_path):
    
    dim_struktura = dimensions.get('dim_struktura')
    dim_prowadzacy = dimensions.get('dim_prowadzacy')
    
    if dim_struktura is None or dim_prowadzacy is None:
        return

    institutes = dim_struktura['InstytutSkrot'].unique()
    
    for institute_code in institutes:
        print(f"\nProcessing institute: {institute_code}")

        institute_path = os.path.join(output_path, f'instytut_{institute_code}')
        os.makedirs(institute_path, exist_ok=True)
        
        institute_dimensions = filter_data_for_institute(dimensions, institute_code)
        
        saved_count = 0
        for dim_name, df in institute_dimensions.items():
            if df is not None and not df.empty:
                file_path = os.path.join(institute_path, f"{dim_name}.csv")
                df.to_csv(file_path, index=False, encoding='utf-8')
                print(f"{dim_name}: {len(df)} records")
                saved_count += 1
            else:
                print(f"{dim_name}: No data for {institute_code}")
        


def filter_data_for_institute(dimensions, institute_code):
    dim_struktura = dimensions['dim_struktura']
    dim_prowadzacy = dimensions['dim_prowadzacy']
    dim_przedmiot = dimensions['dim_przedmiot']
    dim_pytania = dimensions['dim_pytania']
    dim_semestr = dimensions['dim_semestr']
    dim_ankiety = dimensions['dim_ankiety']
    fact_ankiety = dimensions.get('fact_ankiety')

    institute_struktura = dim_struktura[dim_struktura['InstytutSkrot'] == institute_code].copy()

    institute_zaklady = institute_struktura['ZakladSkrot'].tolist()

    institute_prowadzacy = dim_prowadzacy[dim_prowadzacy['Zakład'].isin(institute_zaklady)].copy()

    institute_prowadzacy_ids = institute_prowadzacy['ProwadzacyID'].tolist()

    institute_ankiety = dim_ankiety[dim_ankiety['ProwadzacyID'].isin(institute_prowadzacy_ids)].copy()

    institute_ankiety_ids = institute_ankiety['AnkietaID'].tolist()
    
    institute_przedmiot_ids = institute_ankiety['PrzedmiotID'].unique()
    institute_przedmiot = dim_przedmiot[dim_przedmiot['PrzedmiotID'].isin(institute_przedmiot_ids)].copy()
    
    institute_fact = None
    if fact_ankiety is not None:
        institute_fact = fact_ankiety[
            fact_ankiety['AnkietaID'].isin(institute_ankiety_ids)
        ].copy()
    
    institute_pytania = dim_pytania.copy()
    
    institute_semestr = dim_semestr.copy()
    
    return {
        'dim_struktura': institute_struktura,
        'dim_prowadzacy': institute_prowadzacy,
        'dim_przedmiot': institute_przedmiot,
        'dim_pytania': institute_pytania,
        'dim_semestr': institute_semestr,
        'dim_ankiety': institute_ankiety,
        'fact_ankiety': institute_fact
    }

   

def save_single_dimension(df, dimension_name, output_path):
    try:
        if df is None or df.empty:
            print(f"{dimension_name}: No data to save")
            return False
        
        os.makedirs(output_path, exist_ok=True)
        
        file_path = os.path.join(output_path, f"{dimension_name}.csv")
        
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"Failed to save {dimension_name}: {e}")
        return False

def load_dimension(dimension_name, input_path):
    try:
        file_path = os.path.join(input_path, f"{dimension_name}.csv")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        df = pd.read_csv(file_path, encoding='utf-8')
        
        return df
        
    except Exception as e:
        print(f"Failed to load {dimension_name}: {e}")
        return None
