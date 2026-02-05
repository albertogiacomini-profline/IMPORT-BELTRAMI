import pandas as pd
import numpy as np
import os
import shutil
# import foglio uno

file = ["file/file_intermedi/merged_imio.xlsx", "file/file_intermedi/To_add.xlsx", "file/file_intermedi/To_no_famiglia.xlsx"]
for F in file:
    if os.path.exists(F):
        df = pd.read_excel(F)
        # fprmattazione file
        dfO = df[['Codice', 'Descrizione', 'Codice-a-barre', 'UM', 'Codice-merceologico', 'Famiglia', 'Codice-produttore',
                  'PUBBLICO', 'PREZZO-VENDITA', 'PREZZO-ACQUISTO','Peso-lordo','Volume']]
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

