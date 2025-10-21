import pandas as pd
import glob
import os
import re

def load_excel_files(raw_data_path):
    excel_files = glob.glob(os.path.join(raw_data_path, "*.xlsx"))

    all_prowadzacy_rows = []
    all_przedmiot_rows = []
    questions_set = set()
    raw_files_data = [] 

    for file_path in excel_files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing file: {filename}")
        
        metadata = extract_metadata_from_file(file_path)
        
        file_data = process_excel_file(file_path, metadata)
        
        if file_data:
            all_prowadzacy_rows.extend(file_data['prowadzacy'])
            all_przedmiot_rows.extend(file_data['przedmioty'])
            questions_set.update(file_data['questions'])
            raw_files_data.append(file_data)
    
    return {
        'prowadzacy': all_prowadzacy_rows,
        'przedmioty': all_przedmiot_rows,
        'questions': questions_set,
        'raw_files': raw_files_data
    }


def extract_metadata_from_file(file_path):
    filename = os.path.basename(file_path)
    
    semester_match = re.search(r'(20\d{2}[LZ])', filename)
    fill_cond = 'spełnia' if 'tylko spełniające' in filename else 'nie spełnia'
    
    metadata = {
        'filename': filename,
        'semester': semester_match.group(1) if semester_match else None,
        'fill_condition': None,
        'unit_code': None,
        'file_type': None
    }

    try:
        df_header = pd.read_excel(file_path, header=None, nrows=2)
        if len(df_header) >= 2:
            first_row = str(df_header.iloc[0, 0]) if not pd.isna(df_header.iloc[0, 0]) else ""
            second_row = str(df_header.iloc[1, 0]) if len(df_header) > 1 and not pd.isna(df_header.iloc[1, 0]) else ""
 
            content_text = first_row + " " + second_row

            semester_content = re.search(r'(20\d{2}[LZ])', content_text)
            if semester_content:
                metadata['semester'] = semester_content.group(1)
            
            if 'tylko spełniające' in content_text.lower():
                metadata['fill_condition'] = 'spełnia'
            elif 'wszystkie wyniki' in content_text.lower():
                metadata['fill_condition'] = 'nie spełnia'
            
            unit_match = re.search(r'(\d{6})', content_text)
            if unit_match:
                metadata['unit_code'] = unit_match.group(1)
            
            if 'biorca' in content_text.lower():
                metadata['file_type'] = 'biorca'
            elif 'dawca' in content_text.lower():
                metadata['file_type'] = 'dawca'
    
    except Exception as e:
        print(f"Error reading header from {filename}: {e}")
    
    return metadata

def process_excel_file(file_path, metadata):
    try:
        df_raw = pd.read_excel(file_path, skiprows=2)
        df_cleaned = df_raw.dropna(how='all')

        if 'Nazwisko' in df_cleaned.columns:
            from utils import clean_surname
            df_cleaned['Nazwisko'] = df_cleaned['Nazwisko'].apply(clean_surname)
        

        prowadzacy_data = []
        if all(col in df_cleaned.columns for col in ['Nazwisko', 'Prowadzący']):
            df_prow = df_cleaned[['Nazwisko', 'Prowadzący']].dropna(how='all')
            df_prow = df_prow[df_prow['Prowadzący'].notna()]
            prowadzacy_data = df_prow.to_dict('records')
        

        przedmiot_data = []
        if all(col in df_cleaned.columns for col in ['Nazwa przedmiotu', 'Kod zajęć', 'Dawca']):
            df_przedmiot = df_cleaned[['Nazwa przedmiotu', 'Kod zajęć', 'Dawca']].dropna(how='all')
            df_przedmiot = df_przedmiot[df_przedmiot['Nazwa przedmiotu'].notna()]
            przedmiot_data = df_przedmiot.to_dict('records')
        

        question_cols = [col for col in df_cleaned.columns 
                        if re.match(r'^\d+\s', str(col)) or str(col).strip().isdigit()]
        
        if not question_cols:
            return None

        ankiety_cols = ['Rodzaj zajęć', 'Język prowadzenia zajęć', 
                       'Liczba wypełnionych ankiet', 'Liczba studentów w grupie', 
                       'Procent wypełnionych ankiet', 'Prowadzący', 'Kod zajęć']
        
        relevant_cols = ankiety_cols + question_cols
        relevant_cols = [col for col in relevant_cols if col in df_cleaned.columns]
        df_subset = df_cleaned[relevant_cols].copy()
        
        return {
            'metadata': metadata,
            'prowadzacy': prowadzacy_data,
            'przedmioty': przedmiot_data,
            'questions': question_cols,
            'df_subset': df_subset
        }
        
    except Exception as e:
        print(f"Error processing {metadata['filename']}: {e}")
        return None


def load_zaklady_data(raw_data_path):
    zaklady_files = {
        'ZAIAE': 'zaiae.csv', 'ZEP': 'zep.csv', 'ZETIIS': 'zetiis.csv',
        'ZNE': 'zne.csv', 'ZS': 'zs.csv', 'ZSIP': 'zsip.csv',
        'ZSISE': 'zsise.csv', 'ZTIGE': 'ztige.csv', 'ZTS': 'zts.csv',
        'ZWNIKE': 'zwnike.csv'
    }
    
    pracownicy_zaklady = {}
    
    for zaklad_skrot, filename in zaklady_files.items():
        file_path = os.path.join(raw_data_path, filename)
        
        if os.path.exists(file_path):
            try:
                df_zaklad = pd.read_csv(file_path)
                print(f"  Loaded {filename}: {len(df_zaklad)} records")

                #pomyslec czy tylko nazwisko i imie czy calosc
                #df_zaklad['Nazwisko_Clean'] = df_zaklad['Nazwisko'].str.strip().str.title()
                df_zaklad['Nazwisko_Clean'] = df_zaklad['Nazwisko'].str.strip()
                df_zaklad['Imie_Clean'] = df_zaklad['Imiona'].str.strip()
                #df_zaklad['Prowadzacy_Full'] = (df_zaklad['Tytuł'].fillna('').astype(str).str.strip() + ' ' + df_zaklad['Nazwisko'].str.strip() + ' ' + df_zaklad['Imiona'].fillna('').astype(str).str.strip()).str.strip()
                #df_zaklad['Prowadzacy'] = (df_zaklad['Nazwisko_Clean'] + ' ' + df_zaklad['Imie_Clean']).str.strip()
    
                for _, row in df_zaklad.iterrows():
                    nazwisko = row['Nazwisko_Clean'].lower()
                    imie = row['Imie_Clean'].lower()
                    #prowadzacy_key = row['Prowadzacy_Full'].lower()
                    #pracownicy_zaklady[prowadzacy_key] = zaklad_skrot
                    if nazwisko and imie:
                        prowadzacy_key = f"{nazwisko} {imie}"

                        if prowadzacy_key in pracownicy_zaklady:
                            existing_zaklad = pracownicy_zaklady[prowadzacy_key]
                            if existing_zaklad != zaklad_skrot:
                                print(f"  CONFLICT: '{prowadzacy_key}' exists in {existing_zaklad} and {zaklad_skrot}")
                        else:
                            pracownicy_zaklady[prowadzacy_key] = zaklad_skrot
                            # print(f"Added: '{prowadzacy_key}' -> {zaklad_skrot}")

            except Exception as e:
                print(f"  Error loading {filename}: {e}")
        else:
            print(f"  File not found: {filename}")
    
    return pracownicy_zaklady