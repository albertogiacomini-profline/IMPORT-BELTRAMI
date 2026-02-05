import pandas as pd


df = pd.read_excel('output/ord-To_add.xlsx', sheet_name=0)
dfF = pd.read_excel('output/ord-To_no_famiglia.xlsx', sheet_name=0)

df = df.drop(columns=['CONTROPARTITA CONTABILE', 'TIPOLOGIA RAEE', 'PREZZO PRODUTTORE', 'PREZZO', 'SCONTI', 'PUBBLICO', 'PREZZO-VENDITA','PREZZO-ACQUISTO', 'BARCODE PRODUTTORE'])
dfF = dfF.drop(columns=[ 'CONTROPARTITA CONTABILE', 'TIPOLOGIA RAEE', 'PREZZO PRODUTTORE', 'PREZZO', 'SCONTI', 'PUBBLICO', 'PREZZO-VENDITA','PREZZO-ACQUISTO', 'BARCODE PRODUTTORE'])
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