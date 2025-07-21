### Questo file contiene funzioni di utilità per il Timesheet Dashboard ###

import sqlite3
import pandas as pd

# === Parametri modificabili manualmente ===
FILTRO_DATE = True
DATA_INIZIO = "2024-01-01"
DATA_FINE = "2025-12-31"

def get_data():
    """
    Recupera e pre-processa i dati dal database SQLite.
    Unisce le tabelle UTENTI e DIPENDENTI e applica un filtro per data.
    """
    # Connessione al database
    conn = sqlite3.connect("database.db", check_same_thread=False)
    df_attivita = pd.read_sql_query("SELECT * FROM UTENTI", conn)
    df_dipendenti = pd.read_sql_query("SELECT * FROM DIPENDENTI", conn)
    conn.close()

    # Merge e preparazione dati
    df = df_attivita.merge(df_dipendenti, on="ID_UTENTE", how="left")
    df["DATA"] = pd.to_datetime(df["DATA"])

    # Filtro per date
    if FILTRO_DATE:
        data_inizio = pd.to_datetime(DATA_INIZIO)
        data_fine = pd.to_datetime(DATA_FINE)
        df = df[(df["DATA"] >= data_inizio) & (df["DATA"] <= data_fine)]
    
    # Aggiungi colonna DIPENDENTE per facilitare i raggruppamenti
    df["DIPENDENTE"] = df["COGNOME"] + " " + df["NOME"]
    
    return df