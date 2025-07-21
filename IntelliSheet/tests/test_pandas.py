import pandas as pd
import re
from collections import defaultdict
import json
import sys
import os

def process_excel_file(excel_path, output_json_path):
    """
    Processa un singolo file Excel e genera il JSON corrispondente
    """
    print(f"[PROCESSING] {excel_path}")
    
    # === 1. Estrazione mese e anno dal file ===
    
    # Carichiamo solo le prime 5 righe del foglio, senza intestazioni,
    # per cercare la riga che contiene la scritta "Mese di GIUGNO 2025"
    info_df = pd.read_excel(excel_path, sheet_name='Foglio1', header=None, nrows=5)
    
    mese_anno_str = ''
    # Cerchiamo nella matrice (riga per riga, cella per cella) la stringa desiderata
    for row in info_df.itertuples(index=False):
        for cell in row:
            if isinstance(cell, str) and "Mese di" in cell:
                mese_anno_str = cell
                break
        if mese_anno_str:
            break
    
    if not mese_anno_str:
        raise ValueError(f"Impossibile trovare 'Mese di' nel file {excel_path}")
    
    # Ripuliamo la stringa e la convertiamo in maiuscolo per facilitare la ricerca con regex
    testo = mese_anno_str.strip().upper()
    print(f"[DATE] Mese trovato: '{testo}'")
    
    # Estraiamo il nome del mese e l'anno con una regex flessibile
    match = re.search(r"MESE\s+DI\s+([A-ZÀ-Ù]+)\s+(\d{4})", testo)
    if not match:
        raise ValueError(f"Impossibile estrarre mese e anno da: '{mese_anno_str}'")
    
    mese_nome = match.group(1)  # Es: "GIUGNO"
    anno = int(match.group(2))  # Es: 2025
    
    # Mappa da nome mese in italiano → numero mese (per formattazione data)
    mesi = {
        'GENNAIO': 1, 'FEBBRAIO': 2, 'MARZO': 3, 'APRILE': 4,
        'MAGGIO': 5, 'GIUGNO': 6, 'LUGLIO': 7, 'AGOSTO': 8,
        'SETTEMBRE': 9, 'OTTOBRE': 10, 'NOVEMBRE': 11, 'DICEMBRE': 12
    }
    
    # Verifica che il nome mese sia valido
    if mese_nome not in mesi:
        raise ValueError(f"Mese non riconosciuto: '{mese_nome}'")
    
    mese = mesi[mese_nome]
    print(f"[DATA] Mese estratto: {mese}, Anno: {anno}")
    
    # === 2. Lettura del foglio con intestazioni corrette ===
    
    # Rileggiamo l'intero foglio impostando la riga 5 (indice 4) come intestazione
    df = pd.read_excel(excel_path, sheet_name='Foglio1', header=4)
    
    # Rimuoviamo righe completamente vuote (NaN in tutte le colonne)
    df = df.dropna(how='all')
    
    # Puliamo i nomi delle colonne rimuovendo spazi e a capo
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', ' ', regex=True)
    
    # === 3. Estrazione solo delle colonne utili: Data e Descrizione Attività ===
    
    # Selezioniamo le righe con valore non nullo in 'Descrizione Attività svolta'
    df_attivita = df[['Data', 'Descrizione Attività svolta']].dropna()
    
    # Funzione per formattare il giorno in formato completo dd/mm/yyyy
    def formatta_data(giorno):
        try:
            giorno_int = int(float(giorno))  # Gestisce anche valori float
            return f"{giorno_int:02d}/{mese:02d}/{anno}"
        except:
            return None  # In caso di errore (es. valore non numerico)
    
    # Funzione per estrarre attività e ore da una stringa del tipo:
    # "6h_Propa (834), 2h_AttivitàInterne"
    def parse_attivita(text):
        pattern = r'(\d+)h_([^,]+)'  # Cerca espressioni tipo "6h_nome"
        return [(int(ore), attivita.strip()) for ore, attivita in re.findall(pattern, str(text))]
    
    # === 4. Costruzione struttura finale: dizionario con data → lista di attività ===
    
    attivita_per_data = defaultdict(list)  # dict con valori predefiniti come liste
    
    # Cicliamo su tutte le righe contenenti attività
    for _, row in df_attivita.iterrows():
        data_str = formatta_data(row['Data'])  # es: "03/06/2025"
        if not data_str:
            continue
        # Estraiamo ogni coppia (attività, ore) e la aggiungiamo al giorno corrispondente
        for ore, attivita in parse_attivita(row['Descrizione Attività svolta']):
            attivita_per_data[data_str].append((attivita, ore))
    
    # Ordiniamo il dizionario per data (alfabeticamente, che funziona per formato dd/mm/yyyy)
    attivita_per_data = dict(sorted(attivita_per_data.items()))
    
    # === 5. Stampa della struttura risultato ===
    
    print(f"[ACTIVITIES] Attivita estratte per {len(attivita_per_data)} giorni")
    total_activities = sum(len(activities) for activities in attivita_per_data.values())
    print(f"[TOTAL] Totale attivita: {total_activities}")
    
    # === 6. Esportazione su file JSON ===
    
    # Crea la directory di output se non esiste
    output_dir = os.path.dirname(output_json_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Salva il dizionario nel file JSON con indentazione e caratteri UTF-8
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(attivita_per_data, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] File JSON salvato: {output_json_path}")
    return output_json_path

def main():
    """
    Funzione principale che gestisce i parametri da linea di comando
    """
    if len(sys.argv) < 3:
        print("[ERROR] Uso: python test_pandas.py <file_excel> <output_json>")
        print("[EXAMPLE] python test_pandas.py salvataggi/Barca_Giu_2025.xlsx input_json/Barca_Giu_2025.json")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    output_json_path = sys.argv[2]
    
    # Verifica che il file Excel esista
    if not os.path.exists(excel_path):
        print(f"[ERROR] File Excel non trovato: {excel_path}")
        sys.exit(1)
    
    try:
        # Processa il file
        result_path = process_excel_file(excel_path, output_json_path)
        print(f"[COMPLETE] Processing completato con successo!")
        print(f"[INPUT] {excel_path}")
        print(f"[OUTPUT] {result_path}")
        
    except Exception as e:
        print(f"[ERROR] Errore durante il processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
