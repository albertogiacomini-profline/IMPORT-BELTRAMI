import pandas as pd
import numpy as np
import os
import shutil
# import foglio uno

file_obbligatorio = "file/file_intermedi/merged_imio.xlsx"
file = [file_obbligatorio, "file/file_intermedi/To_add.xlsx", "file/file_intermedi/To_no_famiglia.xlsx", "file/file_intermedi/To_ambigui.xlsx"]

if not os.path.exists(file_obbligatorio):
    raise FileNotFoundError(
        f"Non trovo '{file_obbligatorio}': lancia prima 2ImportIMIO.py."
    )

colonne_richieste = ['Codice', 'Descrizione', 'Codice-a-barre', 'UM', 'Codice-merceologico', 'Famiglia',
                      'Codice-produttore', 'PUBBLICO', 'PREZZO-VENDITA', 'PREZZO-ACQUISTO', 'Peso-lordo', 'Volume']

for F in file:
    if os.path.exists(F):
        df = pd.read_excel(F)
        # fprmattazione file
        colonne_mancanti = [c for c in colonne_richieste if c not in df.columns]
        if colonne_mancanti:
            raise ValueError(f"In '{F}' mancano le colonne {colonne_mancanti}: controlla lo step precedente.")
        dfO = df[colonne_richieste]
        dfO = dfO.rename(columns={'Codice': 'CODICE INTERNO', 'Descrizione': 'DESCRIZIONE INTERNA',
                                  'CODICE-A-BARRE-': 'BARCODE INTERNO', 'Codice-merceologico': 'MERCEOLOGICO',
                                  'Famiglia': 'FAMIGLIA', 'Codice-produttore': 'CODICE PRODUTTORE'}, inplace=False)
        dfO.insert(6, 'CONTROPARTITA CONTABILE', value=np.nan)
        dfO.insert(7, 'TIPOLOGIA RAEE', value=np.nan)
        dfO.insert(9, 'BARCODE PRODUTTORE', value=np.nan)
        dfO.insert(10, 'PREZZO PRODUTTORE', value=np.nan)
        dfO.insert(11, 'PREZZO', value=np.nan)
        dfO.insert(12, 'SCONTI', value=np.nan)
        # export
        dfO.to_excel("output/ord-" + os.path.basename(F), index=False)

