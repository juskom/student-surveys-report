import pandas as pd
import glob
import os
import re
from utils import clean_surname

def load_excel_files(raw_data_path):
    excel_files = glob.glob(os.path.join(raw_data_path, "*.xlsx"))
    
    excel_files = [f for f in excel_files if not os.path.basename(f).startswith('~$')]

    if not excel_files:
        raise FileNotFoundError(f"Nie znaleziono plików ankiet w katalogu: {raw_data_path}")
    
    print(f"\nZnaleziono {len(excel_files)} plików ankiet do przetworzenia")

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
        else:
            print(f"Skipped: Plik nie zawiera danych lub jest uszkodzony")
 
 
    if not raw_files_data:
        raise ValueError("Brak danych w plikach Excel - nie znaleziono prawidłowych arkuszy z ankietami")
    
    if not all_prowadzacy_rows:
        raise ValueError("Brak danych prowadzących - sprawdź czy pliki zawierają kolumny: 'Prowadzący', 'Nazwisko'")
    
    if not all_przedmiot_rows:
        raise ValueError("Brak danych przedmiotów - sprawdź czy pliki zawierają kolumny: 'Nazwa przedmiotu', 'Kod zajęć'")
    
    if not questions_set:
        raise ValueError("Brak pytań ankietowych - sprawdź czy pliki zawierają kolumny z numerami pytań")
    
    print(f"\nZaładowano dane:")
    print(f"  - {len(all_prowadzacy_rows)} rekordów prowadzących")
    print(f"  - {len(all_przedmiot_rows)} rekordów przedmiotów")
    print(f"  - {len(questions_set)} pytań ankietowych")
    print(f"  - {len(raw_files_data)} plików z danymi")
    
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

            semester_content = re.search(r'(\d{4}[LZ])', content_text)
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
 

    missing_metadata = []
    if not metadata['semester']:
        missing_metadata.append('Cykl')
    if not metadata['fill_condition']:
        missing_metadata.append('Kryteria wypełnienia')
    if not metadata['unit_code']:
        missing_metadata.append('Kod jednostki (6-cyfrowy)')
    if not metadata['file_type']:
        missing_metadata.append('Typ (dawca/biorca)')
    
    if missing_metadata:
        print(f"Plik '{filename}' ma uszkodzony nagłówek")
        print(f"Brakuje metadanych: {', '.join(missing_metadata)}")
        metadata['is_valid'] = False
    else:
        metadata['is_valid'] = True
    
    return metadata

def process_excel_file(file_path, metadata):
    filename = metadata['filename']
    
    if not metadata.get('is_valid', True):
        return None
    
    try:
        df_raw = pd.read_excel(file_path, skiprows=2)
        df_cleaned = df_raw.dropna(how='all')
        
        prowadzacy_cols = ['Nazwisko', 'Prowadzący']
        przedmiot_cols = ['Nazwa przedmiotu', 'Kod zajęć', 'Dawca']
        ankiety_cols = ['Rodzaj zajęć', 'Język prowadzenia zajęć', 
                       'Liczba wypełnionych ankiet', 'Liczba studentów w grupie', 
                       'Procent wypełnionych ankiet', 'Prowadzący', 'Kod zajęć']
        
        missing_cols = []
        for col in prowadzacy_cols + przedmiot_cols + ankiety_cols:
            if col not in df_cleaned.columns:
                if col not in missing_cols:
                    missing_cols.append(col)
        
        if missing_cols:
            print(f"ERROR: Plik '{filename}' brakuje wymaganych kolumn: {', '.join(missing_cols)}")
            return None

        df_cleaned['Nazwisko'] = df_cleaned['Nazwisko'].apply(clean_surname)
        
        prowadzacy_data = []
        df_prow = df_cleaned[prowadzacy_cols].dropna(how='all')
        df_prow = df_prow[df_prow['Prowadzący'].notna()]
        prowadzacy_data = df_prow.to_dict('records')

        przedmiot_data = []
        df_przedmiot = df_cleaned[przedmiot_cols].dropna(how='all')
        df_przedmiot = df_przedmiot[df_przedmiot['Nazwa przedmiotu'].notna()]
        przedmiot_data = df_przedmiot.to_dict('records')

        question_cols = [col for col in df_cleaned.columns 
                        if re.match(r'^\d+\s', str(col)) or str(col).strip().isdigit()]
        
        if not question_cols:
            print(f"ERROR: Plik '{filename}' nie zawiera żadnych kolumn z pytaniami")
            return None

        relevant_cols = ankiety_cols + question_cols
        relevant_cols = [col for col in relevant_cols if col in df_cleaned.columns]
        df_subset = df_cleaned[relevant_cols].copy()
        
        # print(f"Loaded: {len(prowadzacy_data)} prowadzący, {len(przedmiot_data)} przedmioty, {len(question_cols)} pytania")
        
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
    
    if not os.path.exists(raw_data_path):
        print(f"\nWARNING: Katalog zakładów nie istnieje: {raw_data_path}")
        return {}
    
    pracownicy_zaklady = {}
    missing_files = []
    found_files = 0
    
    for zaklad_skrot, filename in zaklady_files.items():
        file_path = os.path.join(raw_data_path, filename)
        
        if os.path.exists(file_path):
            found_files += 1
            try:
                df_zaklad = pd.read_csv(file_path)
                print(f"  Loaded {filename}: {len(df_zaklad)} records")
                df_zaklad['Nazwisko_Clean'] = df_zaklad['Nazwisko'].str.strip()
                df_zaklad['Imie_Clean'] = df_zaklad['Imiona'].str.strip()
                
                for _, row in df_zaklad.iterrows():
                    nazwisko = row['Nazwisko_Clean'].lower()
                    imie = row['Imie_Clean'].lower()

                    if nazwisko and imie:
                        prowadzacy_key = f"{nazwisko} {imie}"

                        if prowadzacy_key in pracownicy_zaklady:
                            existing_zaklad = pracownicy_zaklady[prowadzacy_key]
                            if existing_zaklad != zaklad_skrot:
                                print(f"  CONFLICT: '{prowadzacy_key}' exists in {existing_zaklad} and {zaklad_skrot}")
                        else:
                            pracownicy_zaklady[prowadzacy_key] = zaklad_skrot


            except Exception as e:
                print(f"  Error loading {filename}: {e}")
        else:
            missing_files.append(filename)
            print(f"  WARNING: File not found: {filename}")

   
    if missing_files:
        print(f"\nWARNING: Brakuje {len(missing_files)}/{len(zaklady_files)} plików zakładów:")
        for mf in missing_files:
            print(f"  - {mf}")
        print(f"Proces kontynuowany z {found_files} dostępnymi plikami.")
    else:
        print(f"\nZaładowano wszystkie {found_files} plików zakładów pomyślnie.")
    
    return pracownicy_zaklady