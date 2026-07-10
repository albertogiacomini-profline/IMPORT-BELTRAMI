import os
import pandas as pd


COLONNE_DA_RIMUOVERE = ['CONTROPARTITA CONTABILE', 'TIPOLOGIA RAEE', 'PREZZO PRODUTTORE', 'PREZZO', 'SCONTI', 'PUBBLICO', 'PREZZO-VENDITA', 'PREZZO-ACQUISTO', 'BARCODE PRODUTTORE']

df = pd.read_excel('output/ord-To_add.xlsx', sheet_name=0)
df = df.drop(columns=COLONNE_DA_RIMUOVERE)

file_no_famiglia = 'output/ord-To_no_famiglia.xlsx'
if os.path.exists(file_no_famiglia):
    dfF = pd.read_excel(file_no_famiglia, sheet_name=0)
    dfF = dfF.drop(columns=COLONNE_DA_RIMUOVERE)
else:
    print(f"File {file_no_famiglia} non presente: nessun articolo senza famiglia da aggiornare.")
    dfF = pd.DataFrame(columns=df.columns)

df2 = pd.read_excel('input/Esportazione_Articoli - Vista Grid.xlsx',
                    )

print("lettura completata")


df = df.rename(columns={'CODICE INTERNO':'Codice','DESCRIZIONE INTERNA':'Descrizione', 'BARCODE INTERNO': 'Codice a barre',
                        'MERCEOLOGICO': 'Codice merceologico', 'FAMIGLIA':'Famiglia', 'CODICE PRODUTTORE': 'Codice produttore', 'Peso-lordo':'Peso lordo'},inplace=False)
dfF = dfF.rename(columns={'CODICE INTERNO':'Codice','DESCRIZIONE INTERNA':'Descrizione', 'Codice-a-barre': 'Codice a barre',
                        'MERCEOLOGICO': 'Codice merceologico', 'FAMIGLIA':'Famiglia', 'CODICE PRODUTTORE': 'Codice produttore', 'Peso-lordo':'Peso lordo'},inplace=False)
# Aggiungere le righe di df2 a df, rendendo NaN i valori mancanti
df2 = pd.concat([df2, df])

# Imposta 'Codice' come indice in entrambi i DataFrame
df2.set_index('Codice', inplace=True)
dfF.set_index('Codice', inplace=True)

# Sostituisci le righe in df2 con quelle di dfF basandoti su 'Codice'
df2.update(dfF)

# Ripristina 'Codice' come colonna
df2.reset_index(inplace=True)

# Salva il DataFrame come file Excel
df2.to_excel('input/Esportazione_Articoli - Vista Grid.xlsx', index=False)