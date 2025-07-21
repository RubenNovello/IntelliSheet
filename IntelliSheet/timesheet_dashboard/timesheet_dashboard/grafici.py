### Questo file gestisce i grafici per IntelliSheet ###

import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# === Parametri modificabili manualmente ===
FILTRO_DATE = True
DATA_INIZIO = "2024-01-01"
DATA_FINE = "2025-12-31"

def get_data():
    # Connessione al database
    conn = sqlite3.connect("database.db", check_same_thread=False)
    df_timesheet = pd.read_sql_query("SELECT * FROM TIMESHEET", conn)
    df_dipendenti = pd.read_sql_query("SELECT * FROM DIPENDENTI", conn)
    conn.close()

    # Merge e preparazione dati
    df = df_timesheet.merge(df_dipendenti, on="ID_UTENTE", how="left")
    df["DATA"] = pd.to_datetime(df["DATA"])

    # Filtro per date
    if FILTRO_DATE:
        data_inizio = pd.to_datetime(DATA_INIZIO)
        data_fine = pd.to_datetime(DATA_FINE)
        df = df[(df["DATA"] >= data_inizio) & (df["DATA"] <= data_fine)]
    return df

def get_ore_lavorate_per_dipendente():
    df = get_data()
    ore_per_dip = df.groupby(["COGNOME", "NOME"])["ORE_LAVORATE"].sum().reset_index()
    ore_per_dip["DIPENDENTE"] = ore_per_dip["COGNOME"] + " " + ore_per_dip["NOME"]
    fig = px.bar(ore_per_dip, x="DIPENDENTE", y="ORE_LAVORATE", title="Ore lavorate per dipendente")
    return fig

def get_ore_lavorate_per_progetto():
    df = get_data()
    ore_per_proj = df.groupby("PROGETTO")["ORE_LAVORATE"].sum().reset_index()
    fig = px.bar(ore_per_proj, x="PROGETTO", y="ORE_LAVORATE", title="Ore lavorate per progetto")
    return fig

def get_andamento_ore_nel_tempo():
    df = get_data()
    trend = df.groupby("DATA")["ORE_LAVORATE"].sum().reset_index()
    fig = px.line(trend, x="DATA", y="ORE_LAVORATE", title="Ore lavorate nel tempo")
    return fig
