import pandas as pd
# percorcorsi file
TCP_f = "input/LISTINO GRANDI CLIENTI.xlsx"
ban_f = "input/ban.xlsx"
cor_brand = "input/cor-brand.xlsx"

#importa file
df = pd.read_excel(TCP_f)

# Rinominare le colonne
df.rename(columns={'BRAND': 'BRAND','BELTRAMI CODE': 'B-CODICE',
                   'MANUFACTURER CODE': 'CODICE PRODUTTORE',
                   'EAN CODE': 'EAN','DESCRIPTION': 'DESCRIZIONE',
                   'DESCRIPTION IN ENGLISH':'DESCRIZIONE INGLESE',
                   'LISTINO GRANDI CLIENTI': 'PREZZO ACQUISTO',
                   'LISTINO NEGOZIO (IVA ESCL.)': 'PREZZO VENDITA',
                   'MSRP': 'PUBBLICO'}, inplace=True)
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

# normalizza CODICE PRODUTTORE in stringa: in Excel alcuni codici sono salvati
# come numero anziche' come testo (Excel interpreta i punti come separatore
# delle migliaia e li perde). Senza questa conversione .str.replace()
# trasforma silenziosamente in NaN tutti i valori non-stringa, facendo
# perdere il match con l'anagrafica IMIO per quei prodotti.
# Lo schema corretto per il gruppo SRAM/ZIPP/TIME/TRUVATIV e' NN.NNNN.NNN.NNN
# (12 cifre), confermato dai codici dello stesso gruppo gia' salvati come
# testo nel listino (es. "00.1918.290.000").
def _normalizza_codice(x):
    if pd.isna(x):
        return x
    if isinstance(x, (int, float)):
        cifre = str(int(x)) if isinstance(x, float) else str(x)
        if len(cifre) == 12:
            return f"{cifre[0:2]}.{cifre[2:6]}.{cifre[6:9]}.{cifre[9:12]}"
        return cifre
    return x

df['CODICE PRODUTTORE'] = df['CODICE PRODUTTORE'].apply(_normalizza_codice)
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
