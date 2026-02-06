import pandas as pd
# percorcorsi file
TCP_f = "input/LISTINO_GRANDI CLIENTI.xlsx"
ban_f = "input/ban.xlsx"
cor_brand = "input/cor-brand.xlsx"

#importa file
df = pd.read_excel(TCP_f)

# Rinominare le colonne
df.rename(columns={'BRAND': 'BRAND','BELTRAMI CODE': 'B-CODICE','MANUFACTURER CODE': 'CODICE PRODUTTORE',
                   'EAN CODE': 'EAN','DESCRIPTION': 'DESCRIZIONE', 'DESCRIPTION IN ENGLISH':'DESCRIZIONE INGLESE',
                   'LISTO GRANDI CLIENTI (IVA ESCL.)': 'PREZZO ACQUISTO',
                   'LISTINO NEGOZIO (IVA ESCL.)': 'PREZZO VENDITA','MSRP': 'PUBBLICO'}, inplace=True)
#corB = pd.read_excel(cor_brand)

# Iterazione sui valori del DataFrame corB e aggiornamento del DataFrame df
#for index, row in corB.iterrows():
#   start_value = row['start_value']
#   brand_value = row['brand_value']
#   df.loc[df['DESCRIZIONE'].fillna('').str.startswith(start_value), 'BRAND'] = brand_value

# import banlist
dfBAN = pd.read_excel(ban_f)
# trasforma in lista
ban = dfBAN['BRAND'].values
# applico banlist
df.drop(df[df['BRAND'].isin(ban)].index, axis=0, inplace=True)

# rimuovi spazi da codici
df['B-CODICE'] = df['B-CODICE'].str.replace(' ', '', regex=True)
df['CODICE PRODUTTORE'] = df['CODICE PRODUTTORE'].str.replace(' ', '', regex=True)
df['CODICE PRODUTTORE'] = df['CODICE PRODUTTORE'].str.replace('*', '', regex=False)
df['CODICE PRODUTTORE'] = df['CODICE PRODUTTORE'].str.replace('™', '', regex=False)
#RIMUOVI CARATTERI STRANI DA DESCIZIONE
df['DESCRIZIONE'] = df['DESCRIZIONE'].str.replace('*', '', regex=False)
df['DESCRIZIONE'] = df['DESCRIZIONE'].str.replace('™', '', regex=False)
#RIMUOVI DOPPI SPAZI
for x in range(6):
    df['DESCRIZIONE'] = df['DESCRIZIONE'].str.replace('  ', ' ', regex=True)

# cancella righe con valori null in codice
df.dropna(subset=["B-CODICE"], inplace=True)

# sostituisco a capo nei titoli
df.columns = [c.replace("\n", "_") for c in df.columns]

# rimuovi N.C. e omaggio
df['PUBBLICO'] = pd.to_numeric(df['PUBBLICO'], errors='coerce')
df['PREZZO VENDITA'] = pd.to_numeric(df['PREZZO VENDITA'], errors='coerce')
df['PREZZO ACQUISTO'] = pd.to_numeric(df['PREZZO ACQUISTO'], errors='coerce')

# export
df.to_excel("file/file_intermedi/clean.xlsx", index=False)
