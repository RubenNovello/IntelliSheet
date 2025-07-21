import streamlit as st

def show_support_page():
    """
    Pagina di supporto e contatto per IntelliSheet
    """
    st.header("🆘 Supporto & Contatto")
    st.write("Benvenuto nella sezione di supporto di IntelliSheet")
    
    # Sezione FAQ
    st.subheader("❓ Domande Frequenti (FAQ)")
    
    with st.expander("Come importare i file Excel?"):
        st.write("""
        1. Utilizza il file uploader nella sidebar
        2. Seleziona un file Excel (.xlsx o .xls)
        3. Il file verrà salvato automaticamente nella directory 'salvataggi'
        4. Clicca su 'Process Data' per elaborare i dati
        """)
    
    with st.expander("Come visualizzare i grafici KPI?"):
        st.write("""
        1. Assicurati di aver processato almeno un file Excel
        2. Vai alla sezione 'Dashboard' nel menu principale
        3. I grafici verranno generati automaticamente dai dati del database
        """)
    
    with st.expander("Come esportare un report PDF?"):
        st.write("""
        1. Clicca su 'Export Report' nella sidebar
        2. Il sistema genererà automaticamente un PDF con tutti i grafici KPI
        3. Scarica il file utilizzando il pulsante di download
        """)
    
    with st.expander("Problemi con il database?"):
        st.write("""
        - Se il database non è presente, esegui il processing dei file Excel
        - Verifica che i file Excel siano nel formato corretto
        - Controlla lo stato del sistema nella sidebar
        """)
    
    # Sezione Contatti
    st.subheader("📞 Informazioni di Contatto")
    
    st.write("Per assistenza tecnica o domande generali, puoi contattarci:")    
    st.info("""
        **Supporto Tecnico**
        
        📧 Email: marco.barca@apm-tech.it
        
        📱 Telefono: +39 333 666 777
        
        🕒 Orari: Lun-Ven 9:00-18:00
        """)