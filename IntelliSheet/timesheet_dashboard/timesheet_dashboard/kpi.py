### Questo file serve a creare le KPI (Key Performance Indicators) per il Timesheet Dashboard ###

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Simuliamo dati di esempio
data = [
    {'lavoratore': 'Mario', 'data': '2025-06-24', 'progetto': 'A', 'commessa': '001', 'ore': 8, 'straordinario': 2},
    {'lavoratore': 'Mario', 'data': '2025-06-25', 'progetto': 'B', 'commessa': '002', 'ore': 7, 'straordinario': 1},
    {'lavoratore': 'Luca', 'data': '2025-06-24', 'progetto': 'A', 'commessa': '001', 'ore': 8, 'straordinario': 0},
    {'lavoratore': 'Luca', 'data': '2025-06-25', 'progetto': 'A', 'commessa': '001', 'ore': 9, 'straordinario': 2},
    {'lavoratore': 'Anna', 'data': '2025-06-24', 'progetto': 'C', 'commessa': '003', 'ore': 6, 'straordinario': 0},
    {'lavoratore': 'Anna', 'data': '2025-06-25', 'progetto': 'C', 'commessa': '003', 'ore': 7, 'straordinario': 1},
]

df = pd.DataFrame(data)
df['data'] = pd.to_datetime(df['data'])

# KPI 1: Ore totali di lavoro settimanale per lavoratore
ore_settimanali = df.groupby('lavoratore')['ore'].sum().reset_index()
fig1 = px.bar(ore_settimanali, x='lavoratore', y='ore', title='Ore totali di lavoro settimanale')

# KPI 2: Media giornaliera di ore lavorate per progetto/commessa
media_giornaliera = df.groupby(['progetto', 'commessa'])['ore'].mean().reset_index()
fig2 = px.bar(media_giornaliera, x='progetto', y='ore', color='commessa', barmode='group', title='Media giornaliera ore per progetto e commessa')

# KPI 3: Lavoro straordinario per lavoratore e distribuzione per progetto/commessa
straordinari = df.groupby(['lavoratore', 'progetto', 'commessa'])['straordinario'].sum().reset_index()
fig3 = px.bar(straordinari, x='lavoratore', y='straordinario', color='progetto', barmode='group', title='Ore straordinarie distribuite per progetto e commessa')

# Mostra grafici
fig1.show()
fig2.show()
fig3.show()
