# Questo file è un file di test python per la generazione di un database SQLite
# che contiene le tabelle necessarie per il funzionamento del programma.

import sqlite3
import pandas as pd
import glob
import test_numpy as tp
import json
import os
import sys
import subprocess
import tempfile
import shutil


class TestSql:

    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def setup_database(self):
        # Gestisce la cancellazione e creazione del database
        if self.connection:
            self.chiudi_connessione()
        
        if os.path.exists(self.db_name):
            try:
                os.remove(self.db_name)
            except PermissionError:
                print(f"ATTENZIONE: Impossibile accedere al file '{self.db_name}'. Potrebbe essere aperto in un altro programma.")
                print("Per favore, chiudi il file e riesegui lo script.")
                sys.exit(1)
        
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def crea_tabelle(self):
        # Crea la tabella dei dipendenti
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS DIPENDENTI (
                ID_UTENTE INTEGER PRIMARY KEY AUTOINCREMENT,
                COGNOME TEXT NOT NULL,
                NOME TEXT NOT NULL,
                UNIQUE(COGNOME, NOME)
            )
        ''')

        # Crea la tabella dei progetti
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PROGETTI (
                ID_PROGETTO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOME TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Crea la tabella delle commesse
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS COMMESSE (
                ID_COMMESSA INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PROGETTO INTEGER,
                CODICE VARCHAR(50),
                DESCRIZIONE TEXT,
                FOREIGN KEY (ID_PROGETTO) REFERENCES PROGETTI(ID_PROGETTO)
            )
        ''')
        
        # Crea la tabella delle attività degli utenti
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TIMESHEET (
                ID_TIMESHEET INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_UTENTE INTEGER NOT NULL,
                ID_COMMESSA INTEGER NOT NULL,
                DATA DATE NOT NULL,
                ORE_LAVORATE INTEGER,
                FOREIGN KEY (ID_UTENTE) REFERENCES DIPENDENTI(ID_UTENTE),
                FOREIGN KEY (ID_COMMESSA) REFERENCES COMMESSE(ID_COMMESSA)
            )
        ''')

        self.connection.commit()

    def inserisci_dati(self, file_path):
        print(f"DEBUG: Lettura del file: {file_path}")
        
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.xlsx':
                df = pd.read_excel(file_path, header=None)
            elif file_extension == '.csv':
                # Aggiunto sep=None per auto-detect, engine='python' è più robusto
                df = pd.read_csv(file_path, header=None, sep=None, engine='python', on_bad_lines='skip')
            else:
                print(f"ATTENZIONE: Formato file non supportato per {os.path.basename(file_path)}. File saltato.")
                return None
        except Exception as e:
            print(f"ERRORE: Impossibile leggere il file {os.path.basename(file_path)}: {e}")
            return None
            
        print(f"DEBUG: dimensioni del dataframe: {df.shape}")
        
        # La cella Q2 corrisponde a iloc[1, 16]
        try:
            cell_value = df.iloc[1, 16]
            print(f"DEBUG: Valore cella Q2 (iloc[1, 16]): '{cell_value}'")
            full_name = str(df.iloc[1, 16]).strip()
            print(f"DEBUG: Nome dopo strip: '{full_name}'")
        except IndexError as e:
            print(f"DEBUG: Errore accesso cella: {e}")
            print(f"DEBUG: Controllare se la cella Q2 esiste nel file")
            return None
        # Spiegazione di questo pezzo di codice, in particolare, del ciclo try:
        # con cell-value, si cerca il valore della cella di excel corrispondente a Q2, dove risiede il COGNOME e nome del dipendente.
        # con df, si identifica il DataFrame.
        #con iloc si intende l'integer location
        # la lista [1, 16] indica la riga 1 e la colonna 16 (Q2 in Excel)
        # il resto del codice è del tutto interpretabile, e si può descrivere abbastanza facilmente.
        # attenzione solo a str(df.iloc[1, 16]).strip() perche è un casting della variabile.
        #nello specifico, visto e considerato che ci troviamo in test_sql.py, serve a dire che un determinato valore, lo trasformiamo in una stringa di valore
        # Python e Excel sono due ingredienti di una strana maionese: questo pezzo di codice try è come il glutine che lega tutto insieme.
        # quindi... per chiunque se lo chieda, la maionese naturale è glute-free. questo codice no... 🤯
      
        # Parsing del nome
        name_parts = full_name.split()
        print(f"DEBUG: Parti del nome: {name_parts}")
        
        cognome = name_parts[0] if name_parts else "N/A"
        nome = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        print(f"DEBUG: Cognome estratto: '{cognome}'")
        print(f"DEBUG: Nome estratto: '{nome}'")

        # Controlla se il dipendente esiste già
        self.cursor.execute("SELECT ID_UTENTE FROM DIPENDENTI WHERE COGNOME = ? AND NOME = ?", (cognome, nome))
        result = self.cursor.fetchone()
        print(f"DEBUG: Risultato ricerca esistente: {result}")

        if result:
            id_utente = result[0]
            print(f"DEBUG: Dipendente già esistente con ID: {id_utente}")
            
        else:
            # Inserisce il nuovo dipendente e ottiene il suo ID
            print(f"DEBUG: Inserimento nuovo dipendente: {cognome}, {nome}")
            self.cursor.execute("INSERT INTO DIPENDENTI (COGNOME, NOME) VALUES (?, ?)", (cognome, nome))
            self.connection.commit()
            id_utente = self.cursor.lastrowid
            print(f"DEBUG: Nuovo dipendente inserito con ID: {id_utente}")
            
        # Verifica finale - controlla cosa c'è nella tabella
        self.cursor.execute("SELECT * FROM DIPENDENTI")
        tutti_dipendenti = self.cursor.fetchall()
        print(f"DEBUG: Tutti i dipendenti nella tabella: {tutti_dipendenti}")    
        
        return id_utente

    def chiudi_connessione(self):
        # Chiude la connessione al database
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None
        
    def retrieve_project(self, nome):
        self.cursor.execute("SELECT ID_PROGETTO FROM PROGETTI WHERE NOME = ? ", (str(nome),))
        result = self.cursor.fetchone()

        if result:
            id_project = result[0]
        else:
            # Inserisce il nuovo progetto e ottiene il suo ID
            self.cursor.execute("INSERT INTO PROGETTI (NOME) VALUES (?)", (str(nome),))
            self.connection.commit()
            id_project = self.cursor.lastrowid
            
        return id_project
    
    def trova_commessa(self, progetto, commessa):
        id_project = self.retrieve_project(progetto)
        self.cursor.execute("SELECT ID_COMMESSA FROM COMMESSE WHERE CODICE = ? AND ID_PROGETTO = ?", (str(commessa), id_project))
        result = self.cursor.fetchone()

        if result:
            id_commessa = result[0]
        else:
            # Inserisce la nuova commessa e ottiene il suo ID
            self.cursor.execute("INSERT INTO COMMESSE (ID_PROGETTO, CODICE) VALUES (?, ?)", (id_project, str(commessa)))
            self.connection.commit()
            id_commessa = self.cursor.lastrowid
            
        return [id_project, id_commessa]

    def popola_tabelle(self, json_path, id_utente):
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"DEBUG: Dati JSON caricati da {json_path}")
        df = tp.process_timesheet_data(json_data)
        print("DEBUG: Dati del timesheet processati con la logica di normalizzazione (fuzzy logic).")
        
        df['ID_UTENTE'] = id_utente
        
        commessa_id_cache = {}

        for _, row in df.iterrows():
            progetto = row['PROGETTO']
            commessa_code = row['COMMESSA']
            
            id_commessa = None
            if (progetto, commessa_code) in commessa_id_cache:
                id_commessa = commessa_id_cache.get((progetto, commessa_code))
            else:
                _, id_commessa = self.trova_commessa(progetto, commessa_code)
                commessa_id_cache[(progetto, commessa_code)] = id_commessa

            if id_commessa:
                self.cursor.execute('''
                    INSERT INTO TIMESHEET (ID_COMMESSA, ID_UTENTE, DATA, ORE_LAVORATE) VALUES (?, ?, ?, ?)
                ''', (id_commessa, id_utente, row['DATA'], row['ORE_LAVORATE']))

        self.connection.commit()
        print(f"DEBUG: Tabella TIMESHEET popolata per l'utente {id_utente}.")
        
    def esegui(self, file_path, json_path):
        self.crea_tabelle()
        id_utente = self.inserisci_dati(file_path)
        self.popola_tabelle(json_path, id_utente)

    def chiudi_connessione(self):
        self.connection.close()

### CLASSE PER OPERAZIONI CRUD SUL DATABASE

class operazioniCrud:

    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def aggiungi_dipendente(self, cognome, nome):
        self.cursor.execute("INSERT INTO DIPENDENTI (COGNOME, NOME) VALUES (?, ?)", (cognome, nome))
        self.connection.commit()

    def aggiungi_attivita(self, id_utente, data, progetto, commessa, ore_lavorate):
        # Prima trova o crea la commessa
        test_sql = TestSql(self.db_name)
        [id_project, id_commessa] = test_sql.trova_commessa(progetto, commessa)
        
        self.cursor.execute('''
            INSERT INTO TIMESHEET (ID_UTENTE, ID_COMMESSA, DATA, ORE_LAVORATE)
            VALUES (?, ?, ?, ?)
        ''', (id_utente, id_commessa, data, ore_lavorate))
        self.connection.commit()

    def chiudi_connessione(self):
        self.connection.close()

def process_excel_to_json(excel_file_path):
    """
    Processa un singolo file Excel e genera il JSON corrispondente usando test_pandas.py
    
    Args:
        excel_file_path (str): Percorso del file Excel da processare
        
    Returns:
        str: Percorso del file JSON generato
    """
    #Francamente, non avrei voluto creare un file di processamento che va da excel a json
    #eppure, lo fa… non mi piace, ma il codice che ho generato, si rifa ai vada test di pandas e numpy, che parsano in maniera diversa i file di excel
    # Teniamocelo, anche se preferisco spingere attraverso una strozzatura l’intero file excel, così da salvarmi spazio nella directory…
    # Amen, così sia!

    
    # Crea una copia temporanea del file Excel come timesheet.xlsx
    temp_timesheet_path = os.path.join('tests', 'timesheet.xlsx')
    
    # Backup del file originale se esiste
    backup_path = None
    if os.path.exists(temp_timesheet_path):
        backup_path = temp_timesheet_path + '.backup'
        shutil.copy2(temp_timesheet_path, backup_path)
    
    try:
        # Copia il file Excel corrente come timesheet.xlsx
        shutil.copy2(excel_file_path, temp_timesheet_path)
        print(f"DEBUG: Copiato {os.path.basename(excel_file_path)} come timesheet.xlsx")
        
        # Genera un nome per il file JSON di output basato sul nome del file Excel
        base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
        output_json_path = f"input_json/{base_name}.json"
        
        # Assicurati che la directory input_json esista
        os.makedirs('input_json', exist_ok=True)
        
        # Esegui test_pandas.py per generare il JSON con i parametri corretti
        result = subprocess.run([sys.executable, 'tests/test_pandas.py', temp_timesheet_path, output_json_path],
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            print(f"ERRORE nell'esecuzione di test_pandas.py: {result.stderr}")
            return None
            
        print(f"DEBUG: test_pandas.py eseguito con successo")
        print(f"DEBUG: Output: {result.stdout}")
        
        # Controlla se il file JSON è stato creato
        if not os.path.exists(output_json_path):
            print(f"ERRORE: File JSON non generato: {output_json_path}")
            return None
            
        print(f"DEBUG: File JSON generato: {output_json_path}")
        return output_json_path
        
    finally:
        # Ripristina il file originale se esisteva
        if backup_path and os.path.exists(backup_path):
            shutil.move(backup_path, temp_timesheet_path)
        elif os.path.exists(temp_timesheet_path):
            os.remove(temp_timesheet_path)

#Da qui in poi, il codice prende una piega inaspettata, mo’ la spiego:

#il file comincia con un bel semaforo verde


if __name__ == "__main__":
    print("=== AVVIO PROCESSING INTELLISHEET ===")
    
    # Crea la directory input_json se non esiste
    if not os.path.exists('input_json'):
        os.makedirs('input_json')
    
    # Trova tutti i file Excel nella directory salvataggi
    salvataggi_dir = 'salvataggi'
    excel_files = []
    
    if os.path.exists(salvataggi_dir):
        for file in os.listdir(salvataggi_dir):
            if file.endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(salvataggi_dir, file))
    
    if not excel_files:
        print("[ERROR] Nessun file Excel trovato nella directory 'salvataggi'")
        exit(1)
    
    print(f"[FILES] Trovati {len(excel_files)} file Excel:")
    for file in excel_files:
        print(f"  - {file}")
    
    # Inizializza il database e crea le tabelle
    test_sql = TestSql()
    test_sql.setup_database()
    
    # Directory dove cercare i file
    salvataggi_dir = r'C:\Users\ruben\Desktop\IntelliSheet\salvataggi'
    
    # DEBUG: Controlla cosa c'è nella directory
    print(f"DEBUG: Controllo directory: {salvataggi_dir}")
    try:
        all_files_in_dir = os.listdir(salvataggi_dir)
        print(f"DEBUG: Tutti i file nella directory: {all_files_in_dir}")
    except Exception as e:
        print(f"DEBUG: Errore lettura directory: {e}")
        all_files_in_dir = []

    # Trova tutti i file da processare (ignora le directory)
    files_to_process = [os.path.join(salvataggi_dir, f) for f in all_files_in_dir if os.path.isfile(os.path.join(salvataggi_dir, f))]
    print(f"DEBUG: File trovati da processare: {[os.path.basename(f) for f in files_to_process]}")
    
    if not files_to_process:
        print("Nessun file trovato nella directory salvataggi!")
        exit()
    
    print(f"Trovati {len(files_to_process)} file da processare:")
    for i, file in enumerate(files_to_process, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    print("-" * 50)
    
    # Crea le tabelle una sola volta
    test_sql.crea_tabelle()
    
    # Processa ogni file individualmente
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n=== PROCESSANDO FILE {i}/{len(files_to_process)}: {os.path.basename(file_path)} ===")
        
        try:
            # STEP 1: Genera il JSON specifico per questo file Excel
            json_path = process_excel_to_json(file_path)
            if not json_path:
                print(f"ERRORE: Impossibile generare JSON per {os.path.basename(file_path)}")
                continue
            
            # STEP 2: Inserisci i dati del dipendente
            id_utente = test_sql.inserisci_dati(file_path)
            
            if id_utente:
                print(f"Dipendente inserito/trovato con ID: {id_utente}")
                
                # STEP 3: Popola le tabelle con i dati del timesheet specifici per questo dipendente
                test_sql.popola_tabelle(json_path, id_utente)
                print(f"Dati timesheet aggiunti per il dipendente ID: {id_utente}")
                
                # STEP 4: Pulisci il file JSON temporaneo
                if os.path.exists(json_path):
                    os.remove(json_path)
                    print(f"DEBUG: File JSON temporaneo {json_path} rimosso")
            else:
                # L'errore specifico viene già stampato in inserisci_dati
                print(f"AVVISO: Saltato il file {os.path.basename(file_path)} a causa di un errore o formato non supportato.")

        except Exception as e:
            print(f"ERRORE durante il processing di {os.path.basename(file_path)}: {e}")
            continue
    
    # Chiudi la connessione alla fine
    test_sql.chiudi_connessione()
    print("\n" + "=" * 50)
    print("COMPLETATO: Tutti i file sono stati processati!")
    
    # Mostra un riepilogo finale
    try:
        temp_connection = sqlite3.connect('database.db')
        temp_cursor = temp_connection.cursor()
        
        temp_cursor.execute("SELECT COUNT(*) FROM DIPENDENTI")
        num_dipendenti = temp_cursor.fetchone()[0]
        
        temp_cursor.execute("SELECT COUNT(*) FROM TIMESHEET")
        num_timesheet = temp_cursor.fetchone()[0]
        
        print(f"Riepilogo finale:")
        print(f"- Dipendenti nel database: {num_dipendenti}")
        print(f"- Record timesheet nel database: {num_timesheet}")
        
        # Mostra dettagli per dipendente
        temp_cursor.execute("""
            SELECT d.COGNOME, d.NOME, COUNT(t.ID_TIMESHEET) as NUM_RECORD, SUM(t.ORE_LAVORATE) as TOTALE_ORE
            FROM DIPENDENTI d
            LEFT JOIN TIMESHEET t ON d.ID_UTENTE = t.ID_UTENTE
            GROUP BY d.ID_UTENTE, d.COGNOME, d.NOME
        """)
        dipendenti_dettagli = temp_cursor.fetchall()
        
        print("\nDettagli per dipendente:")
        for cognome, nome, num_record, totale_ore in dipendenti_dettagli:
            print(f"- {cognome} {nome}: {num_record} record, {totale_ore or 0} ore totali")
        
        temp_connection.close()
    except Exception as e:
        print(f"ERRORE nel mostrare il riepilogo: {e}")
        
#Chiunque arrivi a questo punto del file, e ha avuto pazienza a vedersi il codice, allora ha tutta la mia stima.
#ok, sarà che usato tanta iA, ma ho una giustificazione assolutamente valida:
#GitHub ha fatto casini! Lo so, di solito Git non ha casini, e in realtà li ho fatti io
# ma alle 10 di venerdì 11 luglio 2025, stavo per piangere, perché stavo per perdere TUTTO quello che ho fatto nella seconda settimana di stage…

#Marco, abbi pietà di me! Io  mi sto impegnando e come avrai visto, sto anche studiando

# ah già… il pezzettino di codice
#cognome = name_parts[0] if name_parts else "N/A"
#nome = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

#Adesso lo spiego…
#splitta il COGNOME dal nome… essendo che lo stringhiamo e listiamo, 0 corrisponde al cognome, e 1 al nome.
# 0 sarà sempre il cognome, da 1: significa che tutto il resto sarà il nome. E sa ha due, tre o quattro cognomi? Non importa…
