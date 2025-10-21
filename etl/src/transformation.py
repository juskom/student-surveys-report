import pandas as pd
from config import INSTYTUTY, ZAKLADY
from utils import split_prowadzacy, extract_question_number

def build_struktura_wydzialu():
    print("Creating dim_struktura...")
    
    records = []
    struktura_id_counter = 1
    
    for zaklad_skrot, (zaklad_nazwa, inst_skrot) in ZAKLADY.items():
        inst_nazwa = INSTYTUTY[inst_skrot]
        records.append({
            "StrukturaID": struktura_id_counter,
            "Instytut": inst_nazwa,
            "InstytutSkrot": inst_skrot,
            "Zakład": zaklad_nazwa,
            "ZakladSkrot": zaklad_skrot
        })
        struktura_id_counter += 1
    
    dim_struktura = pd.DataFrame(records)
    print(f"dim_struktura created with {len(dim_struktura)} records")
    return dim_struktura

def build_dim_prowadzacy(prowadzacy_data, pracownicy_zaklady, dim_struktura):
    print("Creating dim_prowadzacy...")
    
    if not prowadzacy_data:
        print("No instructor data found!")
        return pd.DataFrame()

    df_all_prow = pd.DataFrame(prowadzacy_data)
    
    df_all_prow = df_all_prow.drop_duplicates()
    print(f"  Unique instructor records: {len(df_all_prow)}")

    df_all_prow[["Tytuł", "Nazwisko", "Imiona", "Nazwisko Imiona"]] = df_all_prow.apply(
        split_prowadzacy, axis=1, result_type="expand"
    )
    
    df_all_prow = df_all_prow.reset_index(drop=True)
    df_all_prow["ProwadzacyID"] = range(1, len(df_all_prow) + 1)
    
    dim_prowadzacy = df_all_prow[["ProwadzacyID", "Prowadzący", "Tytuł", "Nazwisko", "Imiona", "Nazwisko Imiona"]].copy()

    dim_prowadzacy = assign_zaklady_to_prowadzacy(dim_prowadzacy, pracownicy_zaklady)

    print(f"dim_prowadzacy created with {len(dim_prowadzacy)} instructors")
    return dim_prowadzacy

def assign_zaklady_to_prowadzacy(dim_prowadzacy, pracownicy_zaklady):
    print("Assigning zakłady to prowadzacy...")
    
    dim_prowadzacy['Zakład'] = None
    matched_count = 0
    
    for idx, row in dim_prowadzacy.iterrows():
        nazwisko = str(row['Nazwisko']).strip().lower() if pd.notna(row['Nazwisko']) else ''
        imie = str(row['Imiona']).strip().lower() if pd.notna(row['Imiona']) else ''
    
        zaklad_found = None

        if nazwisko and imie:
            key = f"{nazwisko} {imie}"
            if key in pracownicy_zaklady:
                zaklad_found = pracownicy_zaklady[key]
                dim_prowadzacy.at[idx, 'Zakład'] = zaklad_found
                matched_count += 1

            else:
                dim_prowadzacy.at[idx, 'Zakład'] = 'brak'
                print(f"No match by full name: {key}")

    print(f"  Matched {matched_count}/{len(dim_prowadzacy)} prowadzacy to zaklady")

    return dim_prowadzacy


def build_dim_przedmiot(przedmiot_data):
    print("Creating dim_przedmiot...")
    
    if not przedmiot_data:
        print("No course data found!")
        return pd.DataFrame()
    
    df_all_przedmiot = pd.DataFrame(przedmiot_data)
    df_all_przedmiot = df_all_przedmiot.drop_duplicates()
    print(f"  Unique course records: {len(df_all_przedmiot)}")
   
    df_all_przedmiot['Kod_parsed'] = df_all_przedmiot['Kod zajęć'].fillna('').astype(str)
    code_parts = df_all_przedmiot['Kod_parsed'].str.split('-', expand=True)
    
    df_all_przedmiot['Kod wydziału'] = code_parts[0] if len(code_parts.columns) > 0 else ''
    df_all_przedmiot['Kod kierunku'] = code_parts[1] if len(code_parts.columns) > 1 else ''
    df_all_przedmiot['Kod trybu'] = code_parts[2] if len(code_parts.columns) > 2 else ''
    df_all_przedmiot['Kod przedmiotu'] = code_parts[3] if len(code_parts.columns) > 3 else ''
    
    
    df_all_przedmiot['Wydział'] = df_all_przedmiot['Kod wydziału'].map({
        '1040': 'Elektryczny'
    }).fillna('nieznany')
    
    df_all_przedmiot['Kierunek'] = df_all_przedmiot['Kod kierunku'].map({
        'AR': 'Automatyka i Robotyka Stosowana',
        'EL': 'Elektrotechnika',
        'EM': 'Elektromobilność',
        'IN': 'Informatyka Stosowana',
        'xx': 'Nie dotyczy'
    }).fillna('nieznany')
    
    df_all_przedmiot['Stopień'] = df_all_przedmiot['Kod trybu'].str[0].map({
        'I': 'inżynierskie',
        'M': 'magisterskie',
    }).fillna('nieznany')
    
    df_all_przedmiot['Tryb'] = df_all_przedmiot['Kod trybu'].str[1].map({
        'S': 'stacjonarne',
        'N': 'niestacjonarne',
    }).fillna('nieznany')
    
    df_all_przedmiot['Język'] = df_all_przedmiot['Kod trybu'].str[2].map({
        'A': 'anglojęzyczne',
        'P': 'polskojęzyczne',
    }).fillna('nieznany')
    
    df_all_przedmiot['Semestr'] = df_all_przedmiot['Kod przedmiotu'].str[4]

    df_all_przedmiot['Dawca'] = df_all_przedmiot['Dawca'].astype(str).map({
        '104000': 'WE',
        '102000': 'WCH',
        '105000': 'WF',
        '112000': 'WMINI',
        '115000': 'WSIMR',
        '116000': 'WT',
        '118000': 'WANS',
    }).fillna('nieznany')
    
    df_all_przedmiot = df_all_przedmiot.reset_index(drop=True)
    df_all_przedmiot["PrzedmiotID"] = range(1, len(df_all_przedmiot) + 1)
 
    dim_przedmiot = df_all_przedmiot[[
        "PrzedmiotID", "Nazwa przedmiotu", "Dawca", "Kod zajęć", 
        "Wydział", "Kierunek", "Stopień", "Tryb", "Język", "Semestr"
    ]].copy()
    
    print(f"dim_przedmiot created with {len(dim_przedmiot)} courses")
    return dim_przedmiot


def build_dim_pytania(questions_set):
    print("Creating dim_pytania...")
    
    if not questions_set:
        print("No questions found!")
        return pd.DataFrame()
    
    unique_questions = sorted(list(questions_set))
    
    dim_pytania = pd.DataFrame({
        'PytanieID': range(1, len(unique_questions) + 1),
        'Pytanie': unique_questions,
        'Numer pytania': [extract_question_number(q) for q in unique_questions]
    })
    
    print(f"dim_pytania created with {len(dim_pytania)} questions")
    return dim_pytania


def build_dim_semestr(raw_files_data):
    print("Creating dim_semestr...")
    
    semester_records = []
    semester_id_counter = 1
    semesters = set()

    for file_data in raw_files_data:
        semester = file_data['metadata']['semester']
        if semester and semester not in semesters:
            semesters.add(semester)

    sorted_semesters = sorted(list(semesters))
    for semester in sorted_semesters:
            year = semester[:4] if len(semester) >= 4 else None
            season = semester[4:] if len(semester) > 4 else None

            year = int(year) if year else None
            
            season_name = {
                'L': 'letni',
                'Z': 'zimowy'
            }.get(season, 'nieznany')
            if year and season:
                rok_akademicki = f"{year}/{year+1}" if season == 'Z' else f"{year-1}/{year}"

            semester_records.append({
                'SemestrID': semester_id_counter,
                'Cykl': semester,
                'Rok akademicki': rok_akademicki,
                'Rok': year,
                'Sezon': season_name
            })
            semester_id_counter += 1

    if semester_records:
        dim_semestr = pd.DataFrame(semester_records)
        print(f"dim_semestr created with {len(dim_semestr)} records")
        return dim_semestr
    else:
        print("No semester data found!")
        return pd.DataFrame()



def build_dim_ankiety(raw_files_data, dim_prowadzacy, dim_przedmiot, dim_semestr):
    print("Creating dim_ankiety...")
    
    if not raw_files_data:
        print("No survey data found!")
        return pd.DataFrame()
    
    ankieta_records = []
    ankieta_id_counter = 1

    for file_data in raw_files_data:
        semester = file_data['metadata']['semester']
        semester_match = dim_semestr[dim_semestr['Cykl'] == semester]
        if semester_match.empty:
            print(f" Warning: Semester '{semester}' from file not found in dim_semestr!")
        semester_id = semester_match.iloc[0]['SemestrID']

        df_subset = file_data['df_subset'].dropna(how='all')
        
        df_with_ids = df_subset.merge(dim_prowadzacy[['Prowadzący', 'ProwadzacyID']], on='Prowadzący', how='left'
                    ).merge(dim_przedmiot[['Kod zajęć', 'PrzedmiotID']], on='Kod zajęć', how='left')

        df_with_ids = df_with_ids.dropna(subset=['ProwadzacyID', 'PrzedmiotID'])
        
        if df_with_ids.empty:
            continue

        df_with_ids = df_with_ids.dropna(subset=['ProwadzacyID', 'PrzedmiotID'])
        
        df_ankieta = pd.DataFrame({
            'AnkietaID': range(ankieta_id_counter, ankieta_id_counter + len(df_with_ids)),
            'Rodzaj zajęć': df_with_ids['Rodzaj zajęć'],
            'Język prowadzenia zajęć': df_with_ids['Język prowadzenia zajęć'],
            'Liczba wypełnionych ankiet': df_with_ids['Liczba wypełnionych ankiet'],
            'Liczba studentów w grupie': df_with_ids['Liczba studentów w grupie'],
            'Procent wypełnionych ankiet': df_with_ids['Procent wypełnionych ankiet'],
            'ProwadzacyID': df_with_ids['ProwadzacyID'],
            'PrzedmiotID': df_with_ids['PrzedmiotID'],
            'SemestrID': semester_id,
            'Kryteria wypełnienia': file_data['metadata']['fill_condition'],
            'Jednostka': file_data['metadata']['unit_code'],
            'Rodzaj': file_data['metadata']['file_type']
        })
        
        df_ankieta['Procent wypełnionych ankiet'] = (df_ankieta['Procent wypełnionych ankiet']
            .astype(str).str.replace('.', ',', regex=False)
        )
        
        ankieta_records.append(df_ankieta)
        ankieta_id_counter += len(df_with_ids)
    
    if ankieta_records:
        dim_ankiety = pd.concat(ankieta_records, ignore_index=True)
        print(f"dim_ankiety created with {len(dim_ankiety)} records")     

        return dim_ankiety
    else:
        print("No ankiety data found!")
        return pd.DataFrame()
    

def build_fact_ankiety(raw_files_data, dim_prowadzacy, dim_przedmiot, dim_ankiety, dim_pytania, dim_semestr):
    print("Creating fact_ankiety...")
    
    if not raw_files_data or dim_ankiety.empty:
        print("No fact data to process!")
        return pd.DataFrame()
    
    fact_data_list = []

    ankiety_keys = dim_ankiety[['AnkietaID','ProwadzacyID', 'PrzedmiotID', 'SemestrID', 'Rodzaj zajęć']]
    
    for file_data in raw_files_data:
        question_cols = file_data['questions']
        df_subset = file_data['df_subset']
        
        valid_question_cols = [col for col in question_cols if col in df_subset.columns]
        if not valid_question_cols:
            continue

        semester = file_data['metadata']['semester']
        semester_match = dim_semestr[dim_semestr['Cykl'] == semester]
        semester_id = semester_match.iloc[0]['SemestrID'] if not semester_match.empty else None

        df_with_ids = df_subset.merge(dim_prowadzacy[['Prowadzący', 'ProwadzacyID']], on='Prowadzący', how='left'
            ).merge(dim_przedmiot[['Kod zajęć', 'PrzedmiotID']], on='Kod zajęć', how='left')

        df_with_ids['SemestrID'] = semester_id
        df_with_ids = df_with_ids.merge(ankiety_keys, on=['ProwadzacyID', 'PrzedmiotID', 'SemestrID', 'Rodzaj zajęć'], how='left')


        df_with_ids = df_with_ids.dropna(subset=['AnkietaID'])
        
        if df_with_ids.empty:
            continue
        id_vars = [c for c in df_with_ids.columns if c not in valid_question_cols]

        df_melted = df_with_ids.melt(
            id_vars=['AnkietaID'],
            value_vars=valid_question_cols,
            var_name='Pytanie',
            value_name='Ocena'
        )
        
        df_melted = df_melted.merge(dim_pytania[['Pytanie', 'PytanieID']],on='Pytanie', how='left')
        df_melted = df_melted.dropna(subset=['PytanieID'])

        df_melted['Ocena'] = (df_melted['Ocena'].astype(str).str.replace('.', ',', regex=False))
        df_melted = df_melted[df_melted['Ocena'] != 'bd']
        df_melted = df_melted.dropna(subset=['Ocena'])
        df_fact = df_melted[['AnkietaID', 'PytanieID', 'Ocena']].copy()
        fact_data_list.append(df_fact)
    
    if fact_data_list:
        fact_ankiety = pd.concat(fact_data_list, ignore_index=True)
        print(f"fact_ankiety created with {fact_ankiety.shape[0]} rows")
        return fact_ankiety
    else:
        print("No fact data processed!")
        return pd.DataFrame()