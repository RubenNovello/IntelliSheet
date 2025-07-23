# IntelliSheet - Deployment su Streamlit Cloud

## Configurazione per Streamlit Cloud

### File principali per il deployment:
- `app.py` - File principale dell'applicazione (nella root)
- `requirements.txt` - Dipendenze Python
- `.streamlit/config.toml` - Configurazione Streamlit

### Struttura del progetto:
```
/
├── app.py                    # File principale Streamlit
├── requirements.txt          # Dipendenze
├── .streamlit/config.toml   # Configurazione
└── IntelliSheet/            # Codice sorgente
    ├── tests/
    │   ├── test_kpi.py      # Funzioni KPI
    │   └── test_sql.py      # Processing database
    ├── salvataggi/          # File Excel di esempio
    │   ├── Barca_Giu_2025_Apm Tech.xlsx
    │   └── Novello_Giu_2025_Apm Tech.xlsx
    └── timesheet_dashboard/ # Moduli dashboard
```

### Funzionalità implementate:

1. **Inizializzazione automatica del database**
   - L'app controlla se il database esiste
   - Se non esiste o è vuoto, esegue automaticamente il processing
   - Utilizza i file Excel di esempio nella directory `IntelliSheet/salvataggi/`

2. **Dashboard KPI con grafici interattivi**
   - Confronto ore totali per dipendente
   - Ore lavorate per dipendente e progetto (con filtri)
   - Ore totali per progetto

3. **Processing automatico dei dati**
   - Upload di nuovi file Excel
   - Processing automatico in background
   - Aggiornamento real-time della dashboard

### Per deployare su Streamlit Cloud:

1. Assicurati che tutti i file siano nella repository GitHub
2. Su Streamlit Cloud, seleziona il file `app.py` come main file
3. L'app si inizializzerà automaticamente al primo avvio

### URL dell'app:
https://intellisheet.streamlit.app/

L'app ora dovrebbe mostrare automaticamente i grafici KPI con i dati di esempio!