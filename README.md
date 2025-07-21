# IntelliSheet

# IntelliSheet: Dashboard per l'Analisi dei Timesheet

**IntelliSheet**
Prevede la realizzazione di una'applicazione Python che analizza i dati relativi ai timesheet aziendali.
L'applicazione raccoglie automaticamente i file CSV (Command Separated Values) contenenti le ore lavorate dai dipendenti sui vari progetti e commesse, aggrega e visualizza tali dati in una dashboard interattiva.

## Obiettivi

- Automatizzare la raccolta e la visualizzazione dei dati relativi ai timesheet.
- Fornire insight strategici e operativi per supportare decisioni di HR, project management e direzione.
- Ottimizzare l’utilizzo delle risorse aziendali e identificare tempestivamente anomalie o inefficienze.

## Funzionalità Principali
- Caricamento automatico e lettura di file CSV da una directory predefinita.
- Aggregazione e pulizia automatica dei dati.
- Calcolo dinamico di KPI (Key Performance Indicator) (ore totali, media giornaliera, overtime/straordinario, distribuzione per progetto/commesse)
- Visualizzazione tramite grafici interattivi e indicatori numerici.
- Filtri dinamici per dipendente, progetto, commessa, intervalli temporali.
- Generazione di insights testuali automatizzati

## KPI e Insights Generati

L'applicazione risponderà a domande strategiche quali:
    - Quali progetti o commesse stanno superando le ore previste?
    - Quali dipendenti sono sovraccarichi o sotto-utilizzati?
    - Qual è il trend delle attività non fatturabili (da parte)
    - Ci sono dipendenti troppo concentrati su singole commesse?
    - Quali sono i tempi medi per la chiusura di una commessa?

## Tecnologie

- **Linguaggio**: Python
- **Database**: SQLite
- **Analisi dati**: pandas, numpy
- **Visualizzazione dati**: plotly (eventualmente Altair/Matplotlib/Bokeh)
- **Dashboard e interfaccia web**: streamlit
- **Monitoraggio automatico file**: watchdog

## Struttura del Progetto (Pattern MVC)

```

timesheet-dashboard/
├── timesheet_input/          # CSV input (potrebbe diventare parte di /data o /resources)
├── timesheet_dashboard/      # Pacchetto principale dell'applicazione
│   ├── _init_.py
│   ├── app.py                # Entry-point (Streamlit)
│   ├── kpi.py                # Calcolo KPI
│   ├── grafici.py            # Gestione grafici
│   ├── dashboard.py          # UI
│   └── utils.py              # Funzioni condivise
├── requirements.txt
├── README.md
└── run.py                    # Lancia from timesheet_dashboard.app import main --> entry point dell'app
```
## Roadmap di sviluppo
settimane           Attività principali
Settimana 1         Setup Progetto, parsing CSV, struttura dashboard, primi KPI
Settimana 2         Implementazione KPI avanzati, visualizzazione grafiche
Settimana 3         Dashboard interattiva completa, insight testuali
Settimana 4         Rifinitura finale, testing, Versione Demo

## Deliverable Finali

- Applicazione Python completa e funzionante
- Dashboard interattiva con grafici e KPI aggiornati dinamicamente
- Codice documentato e versionato
- Guida all'uso (README.md)
- Demo finale e Presentazione dei risultati

# Funzionalità Opzionali

Predizione delle ore future necessarie per concludere progetti basati su dati storici
Sezione interattiva con Chatbot AI per rispondere a domande sui dati e fornire analisi aggiuntive#
