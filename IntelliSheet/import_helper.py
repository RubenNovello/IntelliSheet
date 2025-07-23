"""
Helper per gestire le importazioni in modo robusto per tutti gli ambienti
"""
import os
import sys
import importlib.util

def safe_import_kpi_functions():
    """
    Importa le funzioni KPI in modo sicuro per tutti gli ambienti
    """
    # Percorsi possibili per il file test_kpi.py
    possible_paths = [
        # Percorso relativo dalla directory corrente
        os.path.join(os.path.dirname(__file__), 'tests', 'test_kpi.py'),
        # Percorso assoluto dalla root del progetto
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'IntelliSheet', 'tests', 'test_kpi.py'),
        # Percorso per deployment cloud
        '/mount/src/intellisheet/IntelliSheet/tests/test_kpi.py',
        # Altri percorsi possibili
        'tests/test_kpi.py',
        'IntelliSheet/tests/test_kpi.py'
    ]
    
    for kpi_path in possible_paths:
        if os.path.exists(kpi_path):
            try:
                spec = importlib.util.spec_from_file_location("test_kpi", kpi_path)
                test_kpi = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_kpi)
                
                return {
                    'grafico_confronto_dipendenti': test_kpi.grafico_confronto_dipendenti,
                    'grafico_progetti_ore_totali': test_kpi.grafico_progetti_ore_totali,
                    'get_complete_data': test_kpi.get_complete_data,
                    'grafico_dipendenti_per_progetto': test_kpi.grafico_dipendenti_per_progetto,
                    'run_kpi_analysis': test_kpi.run_kpi_analysis
                }
            except Exception as e:
                print(f"Errore nell'importazione da {kpi_path}: {e}")
                continue
    
    # Se nessun percorso funziona, prova con import standard
    try:
        from tests.test_kpi import grafico_confronto_dipendenti, grafico_progetti_ore_totali, get_complete_data, grafico_dipendenti_per_progetto, run_kpi_analysis
        return {
            'grafico_confronto_dipendenti': grafico_confronto_dipendenti,
            'grafico_progetti_ore_totali': grafico_progetti_ore_totali,
            'get_complete_data': get_complete_data,
            'grafico_dipendenti_per_progetto': grafico_dipendenti_per_progetto,
            'run_kpi_analysis': run_kpi_analysis
        }
    except ImportError:
        pass
    
    raise ImportError("Impossibile importare le funzioni KPI da nessun percorso disponibile")

# Esporta le funzioni
try:
    kpi_functions = safe_import_kpi_functions()
    grafico_confronto_dipendenti = kpi_functions['grafico_confronto_dipendenti']
    grafico_progetti_ore_totali = kpi_functions['grafico_progetti_ore_totali']
    get_complete_data = kpi_functions['get_complete_data']
    grafico_dipendenti_per_progetto = kpi_functions['grafico_dipendenti_per_progetto']
    run_kpi_analysis = kpi_functions['run_kpi_analysis']
except Exception as e:
    print(f"ERRORE CRITICO nell'importazione delle funzioni KPI: {e}")
    raise