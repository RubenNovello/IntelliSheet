# Piano di Risoluzione: Errore ModuleNotFoundError fpdf

## Problema Identificato
L'applicazione IntelliSheet presenta un errore `ModuleNotFoundError: No module named 'fpdf'` nel file `run.py` alla riga 4.

### Analisi del Problema
- **File coinvolti**: `IntelliSheet/run.py` e `IntelliSheet/timesheet_dashboard/timesheet_dashboard/export.py`
- **Importazioni problematiche**: `from fpdf import FPDF`
- **Dipendenza nel requirements.txt**: `fpdf2` (riga 29)
- **Conflitto**: Il codice importa `fpdf` ma il requirements.txt specifica `fpdf2`

## Soluzione Scelta
**Installare il pacchetto fpdf originale** (soluzione più semplice che non richiede modifiche al codice)

## Piano di Implementazione

### Passo 1: Modifica del requirements.txt
**File**: `IntelliSheet/requirements.txt`
**Azione**: Sostituire `fpdf2` con `fpdf` alla riga 29

**Prima**:
```
# PDF Export
fpdf2
kaleido
```

**Dopo**:
```
# PDF Export
fpdf
kaleido
```

### Passo 2: Installazione delle Dipendenze
**Comando da eseguire**:
```bash
cd /workspaces/IntelliSheet/IntelliSheet
pip install -r requirements.txt
```

**Alternativa specifica**:
```bash
pip install fpdf
```

### Passo 3: Verifica dell'Installazione
**Test di importazione**:
```python
python -c "from fpdf import FPDF; print('fpdf importato con successo')"
```

### Passo 4: Test dell'Applicazione
**Avvio dell'applicazione**:
```bash
cd /workspaces/IntelliSheet/IntelliSheet
streamlit run run.py
```

**Funzionalità da testare**:
1. Avvio dell'applicazione senza errori di importazione
2. Funzionalità di export PDF (pulsante "📄 Export Report" nella sidebar)
3. Generazione corretta dei report PDF con grafici

## Possibili Problemi e Soluzioni Alternative

### Se fpdf non funziona correttamente
**Opzione A**: Tornare a fpdf2 e modificare il codice
- Mantenere `fpdf2` nel requirements.txt
- Modificare le importazioni in `run.py` e `export.py` da `from fpdf import FPDF` a `from fpdf2 import FPDF`

**Opzione B**: Installare entrambi i pacchetti
- Aggiungere sia `fpdf` che `fpdf2` al requirements.txt
- Testare quale funziona meglio

### Se ci sono conflitti di dipendenze
**Soluzione**: Creare un ambiente virtuale pulito
```bash
python -m venv venv_intellisheet
source venv_intellisheet/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Note Tecniche

### Differenze tra fpdf e fpdf2
- **fpdf**: Libreria originale, più stabile ma meno mantenuta
- **fpdf2**: Fork moderno con miglioramenti e correzioni di bug
- **Compatibilità**: fpdf2 dovrebbe essere retrocompatibile con fpdf per la maggior parte dei casi d'uso

### File che utilizzano fpdf
1. `IntelliSheet/run.py` (riga 4): Importazione principale
2. `IntelliSheet/timesheet_dashboard/timesheet_dashboard/export.py` (riga 2): Utilizzato per generare report PDF

### Funzionalità che dipendono da fpdf
- Generazione di report PDF con grafici KPI
- Export di dashboard in formato PDF
- Funzionalità di download PDF dalla sidebar

## Risultato Atteso
Dopo l'implementazione di questo piano:
1. L'applicazione IntelliSheet si avvierà senza errori di importazione
2. La funzionalità di export PDF sarà completamente operativa
3. Gli utenti potranno generare e scaricare report PDF contenenti i grafici KPI

## Prossimi Passi
1. Passare alla modalità Code
2. Implementare le modifiche al requirements.txt
3. Installare le dipendenze
4. Testare l'applicazione
5. Verificare la funzionalità di export PDF
