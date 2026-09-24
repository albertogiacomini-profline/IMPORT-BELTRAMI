import os
import pandas as pd
import numpy as np
from colorama import Fore, init
# aquisizione data
from datetime import date

init(autoreset=True)

today = date.today()
d1 = today.strftime("%d-%m-%Y")

# definizione lista listini
listini = ["amc", 'amb', 'ama', 'oemc', 'oemb', 'oema']

ord_f = "output/ord-merged_imio.xlsx"
sconti_f = "input/sconti.xlsx"
if not os.path.exists(ord_f):
    raise FileNotFoundError(f"Non trovo '{ord_f}': lancia prima '3ordina e aggiungi colonne.py'.")
if not os.path.exists(sconti_f):
    raise FileNotFoundError(f"Non trovo '{sconti_f}' (tabella sconti per famiglia).")

# lettura file
dfO = pd.read_excel(ord_f)
dfS = pd.read_excel(sconti_f)
iva = 1.22

colonne_richieste = ['FAMIGLIA', 'PREZZO-VENDITA', 'PUBBLICO']
colonne_mancanti = [c for c in colonne_richieste if c not in dfO.columns]
if colonne_mancanti:
    raise ValueError(f"In '{ord_f}' mancano le colonne {colonne_mancanti}: controlla lo step precedente.")
if 'FAMIGLIA' not in dfS.columns:
    raise ValueError(f"In '{sconti_f}' manca la colonna 'FAMIGLIA'.")

# Elimina le righe con valori vuoti o NaN nella colonna 'famiglia'
dfO = dfO.dropna(subset=['FAMIGLIA'])
dfO = dfO[dfO['FAMIGLIA'] != '']
# merge sconti
dfP = dfO.merge(dfS, how='left', on='FAMIGLIA', suffixes=('', '-I'))

# Moltiplicare le colonne specificate nella lista per la colonna 'Maglia_NERA'

for col in listini:
    dfP[col] = np.ceil(dfP[col] * dfP['PREZZO-VENDITA'] * 100) / 100

# righe che restano senza prezzo finale perché in sconti.xlsx manca ancora la percentuale per
# quella famiglia (viene aggiunta vuota in automatico da 2ImportIMIO.py, va compilata a mano)
famiglie_senza_sconto = sorted(dfP.loc[dfP['ama'].isna(), 'FAMIGLIA'].dropna().unique().tolist())
if famiglie_senza_sconto:
    print(Fore.RED + f"Prezzo finale mancante per {len(famiglie_senza_sconto)} famiglie "
                      f"(sconto da compilare in {sconti_f}): {', '.join(famiglie_senza_sconto)}")
else:
    print(Fore.GREEN + "Prezzo finale mancante: 0")

#stampa excell con tabella prezzi listini completa
dfP.to_excel(r"output/DFP.xlsx", index=False, sheet_name='Articoli_listino_vendita')


# Nuovo set di colonne richiesto
new_columns = [
    'skupadre', 'ean', 'sku', 'urlkey', 'descrizione breve', 'peso', 'volume', 'famiglia', 'merceologico', 'um',
    'codice_produttore', 'codice_barre_produttore', 'descrizione', 'gemini_export',
    'stato_origine', 'lvp', 'ama', 'amb', 'amc', 'oema', 'oemb', 'oemc'
]

# Creazione di un nuovo DataFrame con le nuove colonne
dft2_new = pd.DataFrame(columns=new_columns)

# Mappatura delle colonne esistenti alle nuove colonne se applicabile
column_mapping = {
    'CODICE INTERNO': 'sku',
    'Codice-a-barre': 'ean',
    'DESCRIZIONE INTERNA': 'descrizione',
    'UM': 'um',
    'MERCEOLOGICO': 'merceologico',
    'FAMIGLIA': 'famiglia',
    'CODICE PRODUTTORE': 'codice_produttore',
    'BARCODE PRODUTTORE': 'codice_barre_produttore',
    'Volume': 'volume',
    'Peso-lordo': 'peso',
    'PUBBLICO': 'lvp',
    'amc': 'amc',
    'amb': 'amb',
    'ama': 'ama',
    'oemc': 'oemc',
    'oemb': 'oemb',
    'oema': 'oema'
}

# Copia dei dati dal DataFrame originale a quello nuovo
for old_col, new_col in column_mapping.items():
    if old_col in dfP.columns:
        if new_col == 'lvp':
            dft2_new[new_col] = np.round(dfP[old_col] / iva, 2)
        else:
            dft2_new[new_col] = dfP[old_col]

# Impostazione di default per le colonne rimanenti se necessario
for col in new_columns:
    if col not in dft2_new.columns:
        dft2_new[col] = None  # o qualsiasi valore predefinito desiderato

# Le celle con valore 0 per peso e volume devono risultare vuote nel file finale
for col in ['peso', 'volume']:
    if col in dft2_new.columns:
        numeric_values = pd.to_numeric(dft2_new[col], errors='coerce')
        dft2_new.loc[numeric_values == 0, col] = None

# Nel file finale non devono esserci duplicati sulla chiave sku:
# manteniamo la riga con più informazioni valorizzate.
dft2_new['_info_count'] = dft2_new.apply(
    lambda row: sum(
        pd.notna(value) and str(value).strip() != ''
        for value in row
    ),
    axis=1
)
dft2_new = (
    dft2_new
    .sort_values('_info_count', ascending=False)
    .drop_duplicates(subset=['sku'], keep='first')
    .drop(columns=['_info_count'])
)

dft2_new.to_excel(r"output/beltrami-"+d1+".xlsx", index=False, sheet_name='Articoli_listino_vendita')
