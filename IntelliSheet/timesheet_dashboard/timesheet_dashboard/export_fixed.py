import pandas as pd
from fpdf import FPDF
import tempfile
import os
import sys
import plotly.express as px
import sqlite3

def get_complete_data_local(db_path='IntelliSheet/database.db'):
    """
    Estrae tutti i dati necessari dal database con JOIN completo
    Versione locale per evitare problemi di import
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

def grafico_confronto_dipendenti_local(df):
    """
    Grafico 1: Confronto tra dipendenti - ore totali lavorate
    Versione locale per evitare problemi di import
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

def grafico_progetti_ore_totali_local(df):
    """
    Grafico 3: Confronto tra progetti e le ore di lavoro impiegate
    Versione locale per evitare problemi di import
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

def grafico_dipendenti_per_progetto_colorato(df):
    """
    Versione modificata del grafico dipendenti per progetto con colori forzati
    """
    if df.empty:
        return None
        
    # Raggruppa per dipendente e progetto
    ore_per_dip_prog = df.groupby(['DIPENDENTE', 'PROGETTO_COMPLETO'])['ORE_LAVORATE'].sum().reset_index()
    
    # Definisci una palette di colori specifica
    color_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
    ]
    
    fig = px.bar(
        ore_per_dip_prog,
        x='DIPENDENTE',
        y='ORE_LAVORATE',
        color='PROGETTO_COMPLETO',
        title='Ore Lavorate per Dipendente e Progetto',
        labels={'ORE_LAVORATE': 'Ore Lavorate', 'DIPENDENTE': 'Dipendente', 'PROGETTO_COMPLETO': 'Progetto'},
        text='ORE_LAVORATE',
        barmode='group',
        color_discrete_sequence=color_palette  # Forza i colori
    )
    
    fig.update_layout(
        title_x=0.5,
        height=600,
        xaxis_tickangle=-45,
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white',
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

def generate_colored_chart_image(fig, width=900, height=500):
    """
    Genera un'immagine PNG colorata da un grafico Plotly con margini corretti
    """
    try:
        # Forza il tema e i colori prima dell'export con margini adeguati
        fig.update_layout(
            template="plotly_white",  # Usa template bianco per migliore contrasto
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=80, t=80, b=80),  # Margini generosi per evitare ritagli
            autosize=False,
            width=width,
            height=height
        )
        
        # Configura le opzioni per preservare i colori
        img_bytes = fig.to_image(
            format="png",
            width=width,
            height=height,
            engine="kaleido",
            scale=1.5  # Scala ottimizzata per qualità e dimensioni
        )
        return img_bytes
    except Exception as e:
        print(f"Errore nella generazione dell'immagine colorata: {e}")
        return None

def create_report():
    """
    Crea un report PDF con i dati della dashboard KPI
    Versione completamente autonoma senza dipendenze esterne
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Titolo principale
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, 'Dashboard KPI IntelliSheet', 0, 1, 'C')
    pdf.ln(5)
    
    # Sottotitolo
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, 'Analisi KPI basata sui dati del database', 0, 1, 'C')
    pdf.ln(10)

    # Ottieni i dati per i grafici usando la funzione locale
    df = get_complete_data_local()
    if df.empty:
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, 'Nessun dato disponibile nel database', 0, 1)
        pdf.ln(5)
        pdf.cell(0, 10, 'Esegui prima il processing dei file Excel', 0, 1)
        return pdf.output(dest='S')

    # --- STATISTICHE GENERALI ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'Statistiche Generali', 0, 1)
    pdf.ln(3)
    
    # Calcola le statistiche
    totale_record = len(df)
    num_dipendenti = df['DIPENDENTE'].nunique()
    num_progetti = df['PROGETTO_COMPLETO'].nunique()
    ore_totali = int(df['ORE_LAVORATE'].sum())
    
    # Mostra le statistiche in formato tabella
    pdf.set_font("Arial", size=11)
    
    # Riga 1: Totale Record e Dipendenti
    pdf.cell(45, 8, 'Totale Record:', 1, 0, 'L')
    pdf.cell(45, 8, str(totale_record), 1, 0, 'C')
    pdf.cell(45, 8, 'Dipendenti:', 1, 0, 'L')
    pdf.cell(45, 8, str(num_dipendenti), 1, 1, 'C')
    
    # Riga 2: Progetti e Ore Totali
    pdf.cell(45, 8, 'Progetti:', 1, 0, 'L')
    pdf.cell(45, 8, str(num_progetti), 1, 0, 'C')
    pdf.cell(45, 8, 'Ore Totali:', 1, 0, 'L')
    pdf.cell(45, 8, str(ore_totali), 1, 1, 'C')
    
    pdf.ln(10)

    # --- GRAFICO 1: Confronto Dipendenti ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, '1. Confronto Ore Totali Lavorate per Dipendente', 0, 1)
    pdf.ln(3)
    
    # Genera il grafico colorato usando la funzione locale
    fig1 = grafico_confronto_dipendenti_local(df)
    if fig1:
        img1_bytes = generate_colored_chart_image(fig1, 900, 500)
    else:
        img1_bytes = None
    
    if img1_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(img1_bytes)
            tmp_file.flush()
            pdf.image(tmp_file.name, x=10, w=190)
        os.unlink(tmp_file.name)
    else:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, 'Errore nella generazione del grafico 1', 0, 1)
    
    pdf.ln(10)

    # --- GRAFICO 2: Dipendenti per Progetto ---
    pdf.add_page()  # Nuova pagina per il secondo grafico
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, '2. Ore Lavorate per Dipendente e Progetto', 0, 1)
    pdf.ln(3)
    
    # Genera il grafico colorato con palette forzata
    fig2 = grafico_dipendenti_per_progetto_colorato(df)
    if fig2:
        img2_bytes = generate_colored_chart_image(fig2, 900, 600)
    else:
        img2_bytes = None
    
    if img2_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(img2_bytes)
            tmp_file.flush()
            pdf.image(tmp_file.name, x=10, w=190)
        os.unlink(tmp_file.name)
    else:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, 'Errore nella generazione del grafico 2', 0, 1)
    
    pdf.ln(10)

    # --- GRAFICO 3: Progetti Ore Totali ---
    pdf.add_page()  # Nuova pagina per il terzo grafico
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, '3. Ore Totali Lavorate per Progetto', 0, 1)
    pdf.ln(3)
    
    # Genera il grafico colorato usando la funzione locale
    fig3 = grafico_progetti_ore_totali_local(df)
    if fig3:
        img3_bytes = generate_colored_chart_image(fig3, 900, 600)
    else:
        img3_bytes = None
    
    if img3_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(img3_bytes)
            tmp_file.flush()
            pdf.image(tmp_file.name, x=10, w=190)
        os.unlink(tmp_file.name)
    else:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, 'Errore nella generazione del grafico 3', 0, 1)
    
    # Footer
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, 'IntelliSheet v1.0 - Sistema di Analisi Timesheet di APM Tech', 0, 1, 'C')
    pdf.cell(0, 5, 'Sviluppato con Streamlit e Python', 0, 1, 'C')
    
    return pdf.output(dest='S')