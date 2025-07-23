import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import sys
import os

def get_complete_data(db_path='IntelliSheet/database.db'):
    """
    Estrae tutti i dati necessari dal database con JOIN completo
    """
    try:
        conn = sqlite3.connect(db_path)
        query = """
        SELECT
            t.DATA,
            t.ORE_LAVORATE,
            d.NOME,
            d.COGNOME,
            p.NOME as PROGETTO,
            c.CODICE as CODICE_COMMESSA,
            c.ID_COMMESSA
        FROM
            TIMESHEET t
        JOIN DIPENDENTI d ON t.ID_UTENTE = d.ID_UTENTE
        JOIN COMMESSE c ON t.ID_COMMESSA = c.ID_COMMESSA
        JOIN PROGETTI p ON c.ID_PROGETTO = p.ID_PROGETTO
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            print("Nessun dato trovato nel database.")
            return pd.DataFrame()

        # Crea colonna dipendente completa
        df['DIPENDENTE'] = df['COGNOME'] + ' ' + df['NOME']
        
        # Crea nome progetto con commessa se presente
        df['PROGETTO_COMPLETO'] = df.apply(lambda row:
            f"{row['PROGETTO']} ({row['CODICE_COMMESSA']})" if row['CODICE_COMMESSA'] and row['CODICE_COMMESSA'] != 'None' else row['PROGETTO'],
            axis=1)
        
        # Converti tipi di dati
        df['DATA'] = pd.to_datetime(df['DATA'])
        df['ORE_LAVORATE'] = pd.to_numeric(df['ORE_LAVORATE'])
        
        print(f"Dati estratti con successo: {len(df)} record")
        return df
        
    except Exception as e:
        print(f"Errore nell'estrazione dati: {e}")
        return pd.DataFrame()

def grafico_confronto_dipendenti(df):
    """
    Grafico 1: Confronto tra dipendenti - ore totali lavorate
    """
    if df.empty:
        return None
        
    # Raggruppa per dipendente
    ore_per_dipendente = df.groupby('DIPENDENTE')['ORE_LAVORATE'].sum().reset_index()
    ore_per_dipendente = ore_per_dipendente.sort_values('ORE_LAVORATE', ascending=False)
    
    fig = px.bar(
        ore_per_dipendente,
        x='DIPENDENTE',
        y='ORE_LAVORATE',
        title='Confronto Ore Totali Lavorate per Dipendente',
        labels={'ORE_LAVORATE': 'Ore Totali', 'DIPENDENTE': 'Dipendente'},
        text='ORE_LAVORATE',
        color='ORE_LAVORATE',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        title_x=0.5,
        height=500,
        showlegend=False
    )
    fig.update_traces(textposition='outside')
    
    return fig

def grafico_dipendenti_per_progetto(df):
    """
    Grafico 2: Confronto dipendenti per quantità di lavoro su progetto
    """
    if df.empty:
        return None
        
    # Raggruppa per dipendente e progetto
    ore_per_dip_prog = df.groupby(['DIPENDENTE', 'PROGETTO_COMPLETO'])['ORE_LAVORATE'].sum().reset_index()
    
    fig = px.bar(
        ore_per_dip_prog,
        x='DIPENDENTE',
        y='ORE_LAVORATE',
        color='PROGETTO_COMPLETO',
        title='Ore Lavorate per Dipendente e Progetto',
        labels={'ORE_LAVORATE': 'Ore Lavorate', 'DIPENDENTE': 'Dipendente', 'PROGETTO_COMPLETO': 'Progetto'},
        text='ORE_LAVORATE',
        barmode='group'
    )
    
    fig.update_layout(
        title_x=0.5,
        height=600,
        xaxis_tickangle=-45,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    fig.update_traces(textposition='outside')
    
    return fig

def grafico_progetti_ore_totali(df):
    """
    Grafico 3: Confronto tra progetti e le ore di lavoro impiegate
    """
    if df.empty:
        return None
        
    # Raggruppa per progetto
    ore_per_progetto = df.groupby('PROGETTO_COMPLETO')['ORE_LAVORATE'].sum().reset_index()
    ore_per_progetto = ore_per_progetto.sort_values('ORE_LAVORATE', ascending=False)
    
    fig = px.bar(
        ore_per_progetto,
        x='PROGETTO_COMPLETO',
        y='ORE_LAVORATE',
        title='Ore Totali Lavorate per Progetto',
        labels={'ORE_LAVORATE': 'Ore Totali', 'PROGETTO_COMPLETO': 'Progetto'},
        text='ORE_LAVORATE',
        color='ORE_LAVORATE',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        title_x=0.5,
        height=600,
        xaxis_tickangle=-45,
        showlegend=False
    )
    fig.update_traces(textposition='outside')
    
    return fig

def run_kpi_analysis(db_path='IntelliSheet/database.db'):
    """
    Esegue l'analisi KPI completa e genera tutti i grafici richiesti
    """
    print("=== AVVIO ANALISI KPI ===")
    
    # Estrai i dati
    df = get_complete_data(db_path)
    
    if df.empty:
        print("Impossibile procedere: nessun dato disponibile.")
        return None, None, None
    
    print(f"Dati caricati: {len(df)} record")
    print(f"Dipendenti: {df['DIPENDENTE'].nunique()}")
    print(f"Progetti: {df['PROGETTO_COMPLETO'].nunique()}")
    
    # Genera i grafici
    print("\n1. Creazione grafico confronto dipendenti...")
    fig1 = grafico_confronto_dipendenti(df)
    
    print("2. Creazione grafico dipendenti per progetto...")
    fig2 = grafico_dipendenti_per_progetto(df)
    
    print("3. Creazione grafico progetti e ore totali...")
    fig3 = grafico_progetti_ore_totali(df)
    
    print("\n=== ANALISI KPI COMPLETATA ===")
    
    return fig1, fig2, fig3

def verifica_database():
    """
    Funzione integrata per verificare il database
    """
    conn = sqlite3.connect('IntelliSheet/database.db')
    cursor = conn.cursor()
    
    print("=== VERIFICA DATABASE ===")
    
    # Verifica dipendenti
    cursor.execute('SELECT * FROM DIPENDENTI')
    dipendenti = cursor.fetchall()
    print(f"\nDIPENDENTI ({len(dipendenti)}):")
    for dip in dipendenti:
        print(f"  ID: {dip[0]}, {dip[1]} {dip[2]}")
    
    # Verifica progetti
    cursor.execute('SELECT * FROM PROGETTI')
    progetti = cursor.fetchall()
    print(f"\nPROGETTI ({len(progetti)}):")
    for prog in progetti:
        print(f"  ID: {prog[0]}, Nome: {prog[1]}")
    
    # Verifica commesse
    cursor.execute('SELECT * FROM COMMESSE')
    commesse = cursor.fetchall()
    print(f"\nCOMMESSE ({len(commesse)}):")
    for comm in commesse:
        print(f"  ID: {comm[0]}, ID_Progetto: {comm[1]}, Codice: {comm[2]}")
    
    # Verifica timesheet totale
    cursor.execute('SELECT COUNT(*) FROM TIMESHEET')
    total_records = cursor.fetchone()[0]
    print(f"\nTOTALE RECORD TIMESHEET: {total_records}")
    
    # Riepilogo per dipendente
    print("\n=== RIEPILOGO PER DIPENDENTE ===")
    cursor.execute('''
        SELECT d.COGNOME, d.NOME, COUNT(t.ID_TIMESHEET) as NUM_RECORD, SUM(t.ORE_LAVORATE) as TOTALE_ORE
        FROM DIPENDENTI d
        LEFT JOIN TIMESHEET t ON d.ID_UTENTE = t.ID_UTENTE
        GROUP BY d.ID_UTENTE, d.COGNOME, d.NOME
        ORDER BY d.COGNOME
    ''')
    
    riepilogo = cursor.fetchall()
    for r in riepilogo:
        print(f"  {r[0]} {r[1]}: {r[2]} record, {r[3] or 0} ore totali")
    
    conn.close()

def mostra_riepilogo_kpi():
    """
    Funzione integrata per mostrare riepilogo KPI
    """
    print("=" * 60)
    print("RIEPILOGO KPI - INTELLISHEET")
    print("=" * 60)
    
    conn = sqlite3.connect('IntelliSheet/database.db')
    
    # Query completa per ottenere tutti i dati
    query = """
    SELECT
        t.DATA,
        t.ORE_LAVORATE,
        d.NOME,
        d.COGNOME,
        p.NOME as PROGETTO,
        c.CODICE as CODICE_COMMESSA
    FROM
        TIMESHEET t
    JOIN DIPENDENTI d ON t.ID_UTENTE = d.ID_UTENTE
    JOIN COMMESSE c ON t.ID_COMMESSA = c.ID_COMMESSA
    JOIN PROGETTI p ON c.ID_PROGETTO = p.ID_PROGETTO
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Crea colonne utili
    df['DIPENDENTE'] = df['COGNOME'] + ' ' + df['NOME']
    df['PROGETTO_COMPLETO'] = df.apply(lambda row:
        f"{row['PROGETTO']} ({row['CODICE_COMMESSA']})" if row['CODICE_COMMESSA'] and row['CODICE_COMMESSA'] != 'None' else row['PROGETTO'],
        axis=1)
    
    print("\n1. CONFRONTO TRA DIPENDENTI (Ore Totali)")
    print("-" * 40)
    ore_per_dipendente = df.groupby('DIPENDENTE')['ORE_LAVORATE'].sum().sort_values(ascending=False)
    for dipendente, ore in ore_per_dipendente.items():
        print(f"  {dipendente}: {ore} ore")
    
    print("\n2. ORE PER PROGETTO")
    print("-" * 40)
    ore_per_progetto = df.groupby('PROGETTO_COMPLETO')['ORE_LAVORATE'].sum().sort_values(ascending=False)
    for progetto, ore in ore_per_progetto.items():
        print(f"  {progetto}: {ore} ore")
    
    print("\n3. DETTAGLIO DIPENDENTI PER PROGETTO")
    print("-" * 40)
    dettaglio = df.groupby(['DIPENDENTE', 'PROGETTO_COMPLETO'])['ORE_LAVORATE'].sum().reset_index()
    dettaglio = dettaglio.sort_values(['DIPENDENTE', 'ORE_LAVORATE'], ascending=[True, False])
    
    current_dipendente = None
    for _, row in dettaglio.iterrows():
        if row['DIPENDENTE'] != current_dipendente:
            current_dipendente = row['DIPENDENTE']
            print(f"\n  {current_dipendente}:")
        print(f"    - {row['PROGETTO_COMPLETO']}: {row['ORE_LAVORATE']} ore")
    
    print("\n4. STATISTICHE GENERALI")
    print("-" * 40)
    print(f"  Totale record: {len(df)}")
    print(f"  Totale dipendenti: {df['DIPENDENTE'].nunique()}")
    print(f"  Totale progetti: {df['PROGETTO_COMPLETO'].nunique()}")
    print(f"  Totale ore lavorate: {df['ORE_LAVORATE'].sum()}")
    print(f"  Media ore per record: {df['ORE_LAVORATE'].mean():.2f}")
    
    # Periodo coperto
    df['DATA'] = pd.to_datetime(df['DATA'])
    print(f"  Periodo: dal {df['DATA'].min().strftime('%d/%m/%Y')} al {df['DATA'].max().strftime('%d/%m/%Y')}")
    print("=" * 60)

if __name__ == '__main__':
    print("=== ESECUZIONE TEST KPI ===")
    
    # Verifica se il database esiste
    if not os.path.exists('IntelliSheet/database.db'):
        print("[ERROR] Database non trovato. Esegui prima 'python tests/test_sql.py'")
        exit(1)
    
    # Esegui l'analisi completa
    fig1, fig2, fig3 = run_kpi_analysis()
    
    if fig1 and fig2 and fig3:
        print("\n=== VISUALIZZAZIONE GRAFICI ===")
        
        print("Mostrando Grafico 1: Confronto Ore Totali per Dipendente...")
        fig1.show()
        
        print("Mostrando Grafico 2: Ore per Dipendente e Progetto...")
        fig2.show()
        
        print("Mostrando Grafico 3: Ore Totali per Progetto...")
        fig3.show()
        
        print("\n[SUCCESS] Tutti i grafici KPI sono stati generati!")
        
        # Opzioni aggiuntive per debug
        print("\n=== OPZIONI AGGIUNTIVE ===")
        print("Per verificare il database: verifica_database()")
        print("Per riepilogo testuale: mostra_riepilogo_kpi()")
        
    else:
        print("\n[ERROR] Errore nella generazione dei grafici.")
        
    print("\n=== FINE TEST KPI ===")
