# File PRINCIPALE DI IntelliSheet
import streamlit as st
import os
from fpdf import FPDF
import io
from tests.test_kpi import run_kpi_analysis, grafico_confronto_dipendenti, grafico_dipendenti_per_progetto, grafico_progetti_ore_totali, get_complete_data
from timesheet_dashboard.timesheet_dashboard import support, export
from timesheet_dashboard.timesheet_dashboard.docs import show_docs_page
### da questo file si lancia l'applicazione Streamlit

# intanto impostiamo il wide mode per l'applicazione
st.set_page_config(layout="wide")

def dashboard_page():
    """
    Dashboard principale con grafici KPI
    """
    st.header("📈 Dashboard KPI IntelliSheet")
    st.write("Analisi KPI basata sui dati del database")

    # Ottieni i dati dal database
    df = get_complete_data()
    
    if df.empty:
        st.error("❌ Nessun dato disponibile nel database")
        st.info("💡 Esegui prima il processing dei file Excel con: `python tests/test_sql.py`")
        return
    
    # Mostra statistiche generali
    st.subheader("📊 Statistiche Generali")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Totale Record", len(df))
    with col2:
        st.metric("Dipendenti", df['DIPENDENTE'].nunique())
    with col3:
        st.metric("Progetti", df['PROGETTO_COMPLETO'].nunique())
    with col4:
        st.metric("Ore Totali", int(df['ORE_LAVORATE'].sum()))
    
    st.markdown("---")
    
    # I tre grafici KPI richiesti
    st.subheader("1️⃣ Confronto Ore Totali Lavorate per Dipendente")
    fig1 = grafico_confronto_dipendenti(df)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.error("Errore nella generazione del grafico 1")
    
    st.subheader("2️⃣ Ore Lavorate per Dipendente e Progetto")
    dipendenti_disponibili = sorted(df['DIPENDENTE'].unique())

    #Multiselect
    dipendenti_selezionati = st.multiselect(
        "👥 Seleziona dipendenti da visualizzare:",
        options=dipendenti_disponibili,
        default=dipendenti_disponibili,  # Tutti selezionati di default
        key="multiselect_dipendenti"
    )

    # Mostra status compatto
    if dipendenti_selezionati:
        selezionati_str = ", ".join(dipendenti_selezionati)
        st.success(f"📊 Visualizzando: {selezionati_str}")
        
        # Filtra i dati in base ai dipendenti selezionati
        df_filtered = df[df['DIPENDENTE'].isin(dipendenti_selezionati)]
        
        # Genera il grafico con i dati filtrati
        fig2 = grafico_dipendenti_per_progetto(df_filtered)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("Errore nella generazione del grafico 2")
    else:
        st.warning("⚠️ Seleziona almeno un dipendente per visualizzare il grafico")
        
    st.markdown("---")    
    
    st.subheader("3️⃣ Ore Totali Lavorate per Progetto")
    fig3 = grafico_progetti_ore_totali(df)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("Errore nella generazione del grafico 3")
    
    st.success("✅ Dashboard KPI caricata con successo!")

def data_processing_page():
    """
    Pagina per il processing dei dati
    """
    st.header("🔄 Data Processing")
    st.write("Gestione e processing dei file Excel")
    
    # Mostra file disponibili
    salvataggi_dir = 'salvataggi'
    if os.path.exists(salvataggi_dir):
        excel_files = [f for f in os.listdir(salvataggi_dir) if f.endswith(('.xlsx', '.xls'))]
        
        if excel_files:
            st.subheader("📁 File Excel Disponibili")
            for file in excel_files:
                st.write(f"• {file}")
            
            # Pulsante per processare i file
            if st.button("🚀 Processa File Excel", type="primary"):
                with st.spinner("Processing in corso..."):
                    # Esegui il processing
                    import subprocess
                    result = subprocess.run(['python', 'tests/test_sql.py'], 
                                          capture_output=True, text=True, cwd='.')
                    
                    if result.returncode == 0:
                        st.success("✅ Processing completato con successo!")
                        st.code(result.stdout)
                        st.rerun()  # Ricarica la pagina
                    else:
                        st.error("❌ Errore durante il processing")
                        st.code(result.stderr)
        else:
            st.warning("⚠️ Nessun file Excel trovato nella directory 'salvataggi'")
    else:
        st.error("❌ Directory 'salvataggi' non trovata")
    
    # Informazioni sul database
    if os.path.exists('database.db'):
        st.subheader("💾 Stato Database")
        st.success("✅ Database presente")
        
        # Mostra statistiche database se disponibili
        try:
            df = get_complete_data()
            if not df.empty:
                st.write(f"📊 Record totali: {len(df)}")
                st.write(f"👥 Dipendenti: {df['DIPENDENTE'].nunique()}")
                st.write(f"📋 Progetti: {df['PROGETTO_COMPLETO'].nunique()}")
        except:
            st.warning("⚠️ Errore nella lettura del database")
    else:
        st.warning("⚠️ Database non presente - esegui il processing")

# Generatore di funzioni con nome univoco per pagine placeholder
def make_named_page(name):
    def page():
        st.header(name)
        st.write(f"Contenuto della pagina: {name}")
        st.info("🚧 Pagina in costruzione")
    page.__name__ = f"page_{name.replace(' ', '_')}"
    return page

# Crea le pagine con titoli e nomi univoci
pages = {
    "Dashboard": [st.Page(dashboard_page, title="KPI Dashboard")],
    "Data":      [
        st.Page(data_processing_page, title="Processing"),
        st.Page(make_named_page("Data Import"), title="Import"),
        st.Page(export.create_report, title="Export")
    ],        
    "Help":      [
        st.Page(show_docs_page, title="Docs"),
        st.Page(support.show_support_page, title="Supporto & Contatto")
    ],
}

# Sidebar
# Costruisci il percorso corretto per il logo
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    # Fallback: cerca il logo nella directory corrente
    if os.path.exists("logo.jpg"):
        st.sidebar.image("logo.jpg", width=200)
    else:
        st.sidebar.write("🧠 IntelliSheet")  # Fallback senza logo
st.sidebar.title("🧠 IntelliSheet")
st.sidebar.header("Quick Actions")

# File uploader per importare i dati
uploaded_file = st.sidebar.file_uploader(
    "📤 Importa un file Excel",
    type=["xlsx", "xls"],
    help="Carica file Excel timesheet per il processing"
)

if uploaded_file is not None:
    # Crea la directory 'salvataggi' se non esiste
    save_path = "salvataggi"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Salva il file nella directory 'salvataggi'
    file_path = os.path.join(save_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.success(f"✅ File '{uploaded_file.name}' salvato!")
    print(f"File '{uploaded_file.name}' salvato in '{os.path.abspath(save_path)}'")

# Pulsante per processare dati
if st.sidebar.button("🔄 Process Data", help="Processa tutti i file Excel in salvataggi/"):
    with st.spinner("Processing..."):
        import subprocess
        result = subprocess.run(['python', 'tests/test_sql.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            st.sidebar.success("✅ Processing completato!")
        else:
            st.sidebar.error("❌ Errore nel processing")

# Pulsante per esportare un report
if st.sidebar.button("📄 Export Report", help="Genera report PDF con grafici KPI"):
    with st.spinner("Generazione report..."):
        try:
            pdf_data = export.create_report()
            
            # FPDF restituisce stringa, convertiamo in bytes per Streamlit
            if isinstance(pdf_data, str):
                pdf_bytes = pdf_data.encode('latin1')
            else:
                pdf_bytes = pdf_data
                
            st.sidebar.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="IntelliSheet_KPI_Report.pdf",
                mime="application/pdf",
            )
            st.sidebar.success("✅ Report generato!")
        except Exception as e:
            st.sidebar.error(f"❌ Errore: {e}")
            
if st.sidebar.button("🎁CSV Export", help = "Genera Report in file CSV"):
    with st.spinner("Generazione SCV in corso, attendere prego..."):
        try:
            import pandas as pd
            df = get_complete_data()
            if not df.empty:
                csv_data = df.to_csv(index=False)
                st.sidebar.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name="IntelliSheet_Data.csv",
                    mime="text/csv",
                )
                st.sidebar.success("✅ CSV generato!")
            else:
                st.sidebar.warning("⚠️ Nessun dato disponibile per l'esportazione")
        except Exception as e:
            st.sidebar.error(f"❌ Errore: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Stato Sistema")

# Mostra stato del sistema
if os.path.exists('database.db'):
    st.sidebar.success("✅ Database OK")
else:
    st.sidebar.warning("⚠️ Database mancante")

salvataggi_count = 0
if os.path.exists('salvataggi'):
    salvataggi_count = len([f for f in os.listdir('salvataggi') if f.endswith(('.xlsx', '.xls'))])

st.sidebar.info(f"📁 File Excel: {salvataggi_count}")

# Barra di navigazione in alto
current_page = st.navigation(pages, position="top")

# Esegui la pagina attiva
current_page.run()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>IntelliSheet v1.0 - Sistema di Analisi Timesheet di APM Tech</p>
    <p>Sviluppato con ❤️ da Ruben Novello usando Streamlit</p>
</div>
""", unsafe_allow_html=True)
