# File di entry point per Streamlit Cloud
# Questo file importa ed esegue l'app principale

import sys
import os

# Aggiungi la directory corrente al path per gli import
sys.path.append(os.path.dirname(__file__))

# Importa ed esegui l'app principale
from app import *