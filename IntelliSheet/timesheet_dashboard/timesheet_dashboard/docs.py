import streamlit as st

def show_docs_page():
    st.title("IntelliSheet - Documentazione")
    st.markdown("Benvenuto nella documentazione di IntelliSheet, l'applicazione per l'analisi dei timesheet aziendali.")
    
    # Contenuto della documentazione

    st.title("IntelliSheet")
    st.markdown("""Prevede la realizzazione di una'applicazione Python che analizza i dati relativi ai timesheet aziendali.
    L'applicazione raccoglie automaticamente i file CSV (Command Separated Values) contenenti le ore lavorate dai dipendenti sui vari progetti e commesse, aggrega e visualizza tali dati in una dashboard interattiva.
    """)

    st.header("Obiettivi", divider=True)
    st.markdown("""
                - Automatizzare la raccolta e la visualizzazione dei dati relativi ai timesheet.
    - Fornire insight strategici e operativi per supportare decisioni di HR, project management e direzione.
    - Ottimizzare l’utilizzo delle risorse aziendali e identificare tempestivamente anomalie o inefficienze.
    """)

    st.header("Funzionalità Principali", divider=True)
    st.markdown("""
    - Caricamento automatico e lettura di file CSV da una directory predefinita.
    - Aggregazione e pulizia automatica dei dati.
    - Calcolo dinamico di KPI (Key Performance Indicator) (ore totali, media giornaliera, overtime/straordinario, distribuzione per progetto/commesse)
    - Visualizzazione tramite grafici interattivi e indicatori numerici.
    - Filtri dinamici per dipendente, progetto, commessa, intervalli temporali.
    - Generazione di insights testuali automatizzati
    """)

    st.header("KPI e Insight Generati", divider=True)
    st.markdown("""
    L'applicazione risponderà a domande strategiche quali:
    - Quali progetti o commesse stanno superando le ore previste?
    - Quali dipendenti sono sovraccarichi o sotto-utilizzati?
    - Qual è il trend delle attività non fatturabili (da parte)
    - Ci sono dipendenti troppo concentrati su singole commesse?
    - Quali sono i tempi medi per la chiusura di una commessa?
    """)

    st.header("Tecnologie", divider=True)
    st.markdown("""
    - **Linguaggio**: Python
    - **Database**: SQLite
    - **Analisi dati**: pandas, numpy
    - **Visualizzazione dati**: plotly (eventualmente Altair/Matplotlib/Bokeh)
    - **Dashboard e interfaccia web**: streamlit
    - **Monitoraggio automatico file**: watchdog
    """)

    st.header("Deliverable Finali", divider=True)
    st.markdown("""
    - Applicazione Python completa e funzionante
    - Dashboard interattiva con grafici e KPI aggiornati dinamicamente
    - Codice documentato e versionato
    - Guida all'uso (README.md)
    - Demo finale e Presentazione dei risultati
    """)

    st.header("Funzionalità Opzionali", divider=True)
    st.markdown("""
    - Predizione delle ore future necessarie per concludere progetti basati su dati storici
    - Sezione interattiva con Chatbot AI per rispondere a domande sui dati e fornire analisi aggiuntive""")