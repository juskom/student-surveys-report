import pandas as pd
import re
import os

def clean_surname(nazwisko):
    if pd.isna(nazwisko):
        return None
    nazwisko = str(nazwisko).strip()
    nazwisko = re.sub(r'[A]$', '', nazwisko)
    return nazwisko

def split_prowadzacy(row):
    nazwisko = str(row["Nazwisko"]).strip()
    prowadzacy = str(row["Prowadzący"]).strip()

    idx = prowadzacy.find(nazwisko)
    if idx == -1:
        return "", nazwisko, prowadzacy

    tytul = prowadzacy[:idx].strip()
    if tytul == "":
        tytul = "brak"
    nazwisko_full = nazwisko
    imiona = prowadzacy[idx + len(nazwisko):].strip()

    nazwisko_imie = nazwisko_full + " " + imiona

    return tytul, nazwisko_full, imiona, nazwisko_imie

def extract_question_number(question_text):
    question_str = str(question_text).strip()
    match = re.match(r'^(\d+)\s', question_str)
    if match:
        return int(match.group(1))
    if question_str.isdigit():
        return int(question_str)
    return None

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)