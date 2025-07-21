#!/usr/bin/env python3
"""
Analizzatore di timesheet JSON con NumPy e Pandas
Converte i dati JSON in una matrice strutturata con: DATA | PROGETTO | COMMESSA | ORE_LAVORATE
"""

import json
import numpy as np
import pandas as pd
import re
from datetime import datetime
import argparse
import sys
from difflib import SequenceMatcher

def normalize_project_name(activity_name):
    """
    Normalizza il nome del progetto usando approccio ibrido:
    1. Normalizzazione base (spazi, caratteri speciali)
    2. Mappature esplicite per pattern noti
    3. Fuzzy matching per casi simili
    
    Args:
        activity_name (str): Nome dell'attività grezza
        
    Returns:
        str: Nome del progetto normalizzato
    """
    
    # Dizionario di mappature esplicite per pattern noti
    explicit_mappings = {
        # Variazioni di Propa
        'propa': 'Propa',
        'propa(834)': 'Propa',
        'propa (834)': 'Propa',
        
        # Variazioni di AttivitàInterne
        'attivitàinterne': 'AttivitàInterne',
        'attivitàinternre': 'AttivitàInterne',  # errore di battitura
        'attività_interne': 'AttivitàInterne',
        'attivitàinterne(innovation)': 'AttivitàInterne(Innovation)',
        'attività_interne(innovation)': 'AttivitàInterne(Innovation)',
        'attività_interne(hubilities)': 'AttivitàInterne(Hubilities)',
        'attivitàinterne(hubilities)': 'AttivitàInterne(Hubilities)',
        
        # Variazioni di EcuMSI
        'ecumsi project': 'EcuMSI Project',
        'ecumsi project (777)': 'EcuMSI Project',
        'ecumsi project(777)': 'EcuMSI Project',
        
        # Altre normalizzazioni
        'formazione(fabric)': 'Formazione(Fabric)',
        'digital_innovation': 'Digital_Innovation',
    }
    
    # Step 1: Normalizzazione base
    normalized = activity_name.strip().lower()
    
    # Rimuove numeri tra parentesi per il matching
    normalized_for_matching = re.sub(r'\s*\(\d+\)', '', normalized)
    
    # Step 2: Controllo mappature esplicite
    if normalized_for_matching in explicit_mappings:
        return explicit_mappings[normalized_for_matching]
    
    if normalized in explicit_mappings:
        return explicit_mappings[normalized]
    
    # Step 3: Fuzzy matching per casi simili
    known_projects = [
        'Propa', 'AttivitàInterne', 'AttivitàInterne(Innovation)', 
        'AttivitàInterne(Hubilities)', 'EcuMSI Project', 'Formazione(Fabric)', 
        'Digital_Innovation'
    ]
    
    best_match = None
    best_score = 0.0
    threshold = 0.8  # 80% di similarità minima
    
    for project in known_projects:
        # Calcola similarità con il nome pulito (senza numeri)
        project_clean = project.lower()
        score = SequenceMatcher(None, normalized_for_matching, project_clean).ratio()
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = project
    
    if best_match:
        return best_match
    
    # Step 4: Se non trova match, restituisce la versione pulita originale
    # Mantiene la capitalizzazione originale ma pulisce caratteri speciali
    cleaned = activity_name.strip()
    cleaned = re.sub(r'_+', '_', cleaned)  # normalizza underscore multipli
    cleaned = re.sub(r'\s+', ' ', cleaned)  # normalizza spazi multipli
    
    return cleaned

def parse_project_name(activity_name):
    """
    Estrae il nome del progetto e la commessa dall'attività con normalizzazione avanzata
    
    Args:
        activity_name (str): Nome dell'attività
        
    Returns:
        tuple: (progetto_normalizzato, commessa)
    """
    # Estrae la commessa prima della normalizzazione
    commessa_pattern = r'\((\d+)\)'
    commessa_match = re.search(commessa_pattern, activity_name)
    
    if commessa_match:
        commessa = commessa_match.group(1)
    else:
        commessa = None
    
    # Normalizza il nome del progetto
    progetto_normalizzato = normalize_project_name(activity_name)
    
    return progetto_normalizzato, commessa

def process_timesheet_data(json_data):
    """
    Processa i dati JSON del timesheet e crea una matrice strutturata
    
    Args:
        json_data (dict): Dati JSON del timesheet
        
    Returns:
        pandas.DataFrame: DataFrame con colonne DATA, PROGETTO, COMMESSA, ORE_LAVORATE
    """
    rows = []
    
    for date_str, activities in json_data.items():
        # Converte la data dal formato DD/MM/YYYY
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"Attenzione: formato data non valido {date_str}")
            formatted_date = date_str
        
        for activity in activities:
            activity_name = activity[0]
            hours = activity[1]
            
            # Estrae progetto e commessa con normalizzazione
            progetto, commessa = parse_project_name(activity_name)
            
            rows.append({
                'DATA': formatted_date,
                'PROGETTO': progetto,
                'COMMESSA': commessa,
                'ORE_LAVORATE': hours
            })
    
    # Crea DataFrame
    df = pd.DataFrame(rows)
    
    # Ordina per data
    df = df.sort_values('DATA').reset_index(drop=True)
    
    return df

def analyze_data(df, json_data=None):
    """
    Analizza i dati e fornisce statistiche
    
    Args:
        df (pandas.DataFrame): DataFrame dei dati timesheet
        json_data (dict): Dati JSON originali per il mapping
    """
    print("\n" + "="*60)
    print("ANALISI DATI TIMESHEET")
    print("="*60)
    
    print(f"\nTotale righe: {len(df)}")
    print(f"Periodo: dal {df['DATA'].min()} al {df['DATA'].max()}")
    print(f"Totale ore lavorate: {df['ORE_LAVORATE'].sum()}")
    
    print("\n--- PROGETTI (dopo normalizzazione) ---")
    progetti_summary = df.groupby('PROGETTO').agg({
        'ORE_LAVORATE': ['sum', 'count'],
        'COMMESSA': lambda x: x.dropna().nunique() if x.dropna().any() else 0
    }).round(2)
    progetti_summary.columns = ['Ore_Totali', 'Giorni_Lavorati', 'Num_Commesse']
    print(progetti_summary)
    
    # Mostra anche le varianti originali che sono state normalizzate
    print("\n--- MAPPING NOMI ORIGINALI → NORMALIZZATI ---")
    original_to_normalized = {}
    
    # Rielabora i dati originali per mostrare il mapping
    if json_data:
        for date_str, activities in json_data.items():
            for activity in activities:
                original_name = activity[0]
                normalized_name = normalize_project_name(original_name)
                if original_name != normalized_name:
                    if normalized_name not in original_to_normalized:
                        original_to_normalized[normalized_name] = set()
                    original_to_normalized[normalized_name].add(original_name)
    
    for normalized, originals in original_to_normalized.items():
        print(f"{normalized}: {', '.join(sorted(originals))}")
    
    if not original_to_normalized:
        print("Nessuna normalizzazione applicata (tutti i nomi erano già corretti)")
    
    print("\n--- COMMESSE ---")
    commesse_df = df[df['COMMESSA'].notna()]
    if not commesse_df.empty:
        commesse_summary = commesse_df.groupby(['PROGETTO', 'COMMESSA']).agg({
            'ORE_LAVORATE': 'sum'
        }).round(2)
        print(commesse_summary)
    else:
        print("Nessuna commessa trovata")
    
    print("\n--- ORE PER GIORNO ---")
    daily_hours = df.groupby('DATA')['ORE_LAVORATE'].sum().round(2)
    print(f"Media ore/giorno: {daily_hours.mean():.2f}")
    print(f"Min ore/giorno: {daily_hours.min()}")
    print(f"Max ore/giorno: {daily_hours.max()}")

def export_data(df, output_format='csv', filename=None):
    """
    Esporta i dati in vari formati
    
    Args:
        df (pandas.DataFrame): DataFrame da esportare
        output_format (str): Formato di output ('csv', 'excel', 'json')
        filename (str): Nome del file (opzionale)
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"timesheet_analysis_{timestamp}"
    
    if output_format.lower() == 'csv':
        output_file = f"{filename}.csv"
        df.to_csv(output_file, index=False)
        print(f"\nDati esportati in: {output_file}")
    
    elif output_format.lower() == 'excel':
        output_file = f"{filename}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\nDati esportati in: {output_file}")
    
    elif output_format.lower() == 'json':
        output_file = f"{filename}.json"
        df.to_json(output_file, orient='records', indent=2)
        print(f"\nDati esportati in: {output_file}")

def main():
    """Funzione principale CLI"""
    parser = argparse.ArgumentParser(
        description='Analizza dati timesheet JSON e crea matrice strutturata'
    )
    parser.add_argument(
        '--input', 
        default=r'./input_json/GIUGNO_2025.json',
        help='File JSON di input (default: C:\\Users\\ruben\\Desktop\\IntelliSheet\\tests\\GIUGNO_2025.json)'
    )
    parser.add_argument(
        '--export', 
        choices=['csv', 'excel', 'json'], 
        help='Esporta risultati nel formato specificato'
    )
    parser.add_argument(
        '--output', 
        help='Nome del file di output (senza estensione)'
    )
    parser.add_argument(
        '--no-analysis', 
        action='store_true', 
        help='Salta l\'analisi statistica'
    )
    
    args = parser.parse_args()
    
    # Carica i dati dal file specificato (default: GIUGNO_2025.json)
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"Dati caricati da: {args.input}")
    except FileNotFoundError:
        print(f"Errore: File {args.input} non trovato nella directory corrente")
        print("Assicurati che il file GIUGNO_2025.json sia presente nella stessa directory dello script")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Errore: File {args.input} non è un JSON valido")
        sys.exit(1)
    
    # Processa i dati
    df = process_timesheet_data(json_data)
    
    # Mostra la matrice
    print("\n" + "="*80)
    print("MATRICE TIMESHEET")
    print("="*80)
    print(df.to_string(index=False))
    
    # Analisi (se richiesta)
    if not args.no_analysis:
        analyze_data(df, json_data)
    
    # Esporta (se richiesto)
    if args.export:
        export_data(df, args.export, args.output)
    
    print(f"\nProcessate {len(df)} righe di dati timesheet.")

if __name__ == "__main__":
    main()