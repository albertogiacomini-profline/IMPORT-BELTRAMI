import pandas as pd
import numpy as np
# aquisizione data
from datetime import date

today = date.today()
d1 = today.strftime("%d-%m-%Y")

# definizione lista listini
listini = ["amc", 'amb', 'ama', 'oemc', 'oemb', 'oema']
# lettura file
dfO = pd.read_excel("output/ord-merged_imio.xlsx")
dfS = pd.read_excel("input/sconti.xlsx")
iva = 1.22
# Elimina le righe con valori vuoti o NaN nella colonna 'famiglia'
dfO = dfO.dropna(subset=['FAMIGLIA'])
dfO = dfO[dfO['FAMIGLIA'] != '']
# merge sconti
dfP = dfO.merge(dfS, how='left', on='FAMIGLIA', suffixes=('', '-I'))

# Moltiplicare le colonne specificate nella lista per la colonna 'Maglia_NERA'

for col in listini:
    dfP[col] = np.ceil(dfP[col] * dfP['PREZZO-VENDITA'] * 100) / 100

#stampa excell con tabella prezzi listini completa
dfP.to_excel(r"output/DFP.xlsx", index=False, sheet_name='Articoli_listino_vendita')


# Nuovo set di colonne richiesto
new_columns = [
    'skupadre', 'ean', 'SKU', 'urlkey', 'categoria', 'descrizione breve',
    'metatitle', 'metadescription', 'status', 'locale', 'componente', 'brand',
    'specialita', 'velocita', 'grupposerie', 'movimento', 'materiale', 'tecnologia forcella',
    'specifica tecnica', 'specifica tecnica 2', 'tipologia freno', 'larghezza mozzo',
    'ingranaggi', 'colore', 'confezione', 'attacco', 'escursione', 'software',
    'tipologia bloccaggio', 'diametro', 'diametro coperture', 'larghezza', 'lunghezza',
    'moltiplica', 'altezza', 'peso', 'volume', 'famiglia', 'merceologico', 'UM',
    'codice_produttore', 'codice_barre_produttore', 'descrizione', 'gemini_export',
    'stato_origine', 'LVP', 'AMA', 'AMB', 'AMC', 'OEMA', 'OEMB', 'OEMC'
]

# Creazione di un nuovo DataFrame con le nuove colonne
dft2_new = pd.DataFrame(columns=new_columns)

# Mappatura delle colonne esistenti alle nuove colonne se applicabile
column_mapping = {
    'CODICE INTERNO': 'SKU',
    'Codice-a-barre': 'ean',
    'DESCRIZIONE INTERNA': 'descrizione',
    'UM': 'UM',
    'MERCEOLOGICO': 'merceologico',
    'FAMIGLIA': 'famiglia',
    'CODICE PRODUTTORE': 'codice_produttore',
    'BARCODE PRODUTTORE': 'codice_barre_produttore',
    'Volume': 'volume',
    'Peso-lordo': 'peso',
    'PUBBLICO': 'LVP',
    'amc': 'AMC',
    'amb': 'AMB',
    'ama': 'AMA',
    'oemc': 'OEMC',
    'oemb': 'OEMB',
    'oema': 'OEMA'
}

# Copia dei dati dal DataFrame originale a quello nuovo
for old_col, new_col in column_mapping.items():
    if old_col in dfP.columns:
        dft2_new[new_col] = dfP[old_col]

# Impostazione di default per le colonne rimanenti se necessario
for col in new_columns:
    if col not in dft2_new.columns:
        dft2_new[col] = None  # o qualsiasi valore predefinito desiderato

dft2_new.to_excel(r"output/beltrami-"+d1+".xlsx", index=False, sheet_name='Articoli_listino_vendita')
