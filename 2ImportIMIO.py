import pandas as pd
# import foglio uno
imio_f = "input/Esportazione_Articoli - Vista Grid.xlsx"
cp_f = "file/file_intermedi/clean.xlsx"
iniziali = "input/iniziali.xlsx"
Schifo = "input/SCHIFO.xlsx"
output_file = 'output/MARCA NON RICONOSCIUTA.xlsx'
dfI = pd.read_excel(imio_f)
dfC = pd.read_excel(cp_f)

# sostituisco a capo nei titoli
dfI.columns = [c.replace("\n", "_") for c in dfI.columns]
dfI.columns = [c.replace(" ", "-") for c in dfI.columns]
# cancella colonne vuote file imio
dfI.dropna(axis="columns", how='all', inplace=True)

# separa articoli attivi e articoli in fine utilizzo
fine_utilizzo_col = 'Fine-utilizzo'
has_fine_utilizzo = dfI[fine_utilizzo_col].notna() & dfI[fine_utilizzo_col].astype(str).str.strip().ne('')
dfI_attivi = dfI[~has_fine_utilizzo].copy()
dfI_fine_utilizzo = dfI[has_fine_utilizzo].copy()

# Aggiungi una nuova colonna chiamata 'SKU' al DataFrame dfC
dfC['SKU'] = pd.NA


# BRAND CON CODICE PRODUTTORE VALIDO

# import iniziali
dfin = pd.read_excel(iniziali)
# Ottieni i valori unici della colonna 'BRAND'
unique_brands = dfin['BRAND'].unique()

for brand in unique_brands:
    # Condizione per filtrare le righe con il brand corrente e CODICE PRODUTTORE vuoto o NaN
    condition = (dfC['BRAND'] == brand) & (dfC['CODICE PRODUTTORE'].isna() | dfC['CODICE PRODUTTORE'].eq(''))

    # Droppa le righe che soddisfano la condizione
    dfC = dfC.drop(dfC[condition].index)

    # Ottieni il valore di 'INIT' per il brand corrente dal DataFrame dfin
    init_value = dfin.loc[dfin['BRAND'] == brand, 'INIT'].astype(str).values[0]

    # Popola la colonna 'SKU' per le righe con il brand corrente
    dfC.loc[dfC['BRAND'] == brand, 'SKU'] = init_value + dfC['CODICE PRODUTTORE'].astype(str)


# BRAND CON CODICE PRODUTTORE SCHIFO
'''


# import iniziali
dfins = pd.read_excel(Schifo)
# Ottieni i valori unici della colonna 'BRAND'
unique_brands = dfins['BRAND'].unique()

for brand in unique_brands:
    # Condizione per filtrare le righe con il brand corrente e CODICE PRODUTTORE vuoto o NaN
    condition = (dfC['BRAND'] == brand) & (dfC['B-CODICE'].isna() | dfC['B-CODICE'].eq(''))

    # Droppa le righe che soddisfano la condizione
    dfC = dfC.drop(dfC[condition].index)

    # Ottieni il valore di 'INIT' per il brand corrente dal DataFrame dfin
    init_value2 = dfins.loc[dfins['BRAND'] == brand, 'INIT'].astype(str).values[0]

    # Popola la colonna 'SKU' per le righe con il brand corrente
    dfC.loc[dfC['BRAND'] == brand, 'SKU'] = init_value2 + dfC['B-CODICE'].astype(str)

#BRAND NON RICONOSCIUTI


# Seleziona le righe di dfC dove la colonna SKU è vuota
sku_empty_dfC = dfC[dfC['SKU'].isnull() | dfC['SKU'].eq('')]

# Scrivi il DataFrame filtrato in un file Excel
if not sku_empty_dfC.empty:
    sku_empty_dfC.to_excel(output_file, index=False)
'''



# Rinominare le colonne
dfC.rename(columns={'SKU': 'Codice','B-CODICE': 'B-CODICE','CODICE PRODUTTORE': 'Codice-produttore',
                   'EAN': 'Codice-a-barre','DESCRIZIONE': 'Descrizione',
                   'PREZZO GRANDI CLIENTI (IVA ESCL.)': 'PREZZO ACQUISTO',
                   'PREZZO NEGOZIO (IVA ESCL.)': 'PREZZO VENDITA','MSRP': 'PUBBLICO'}, inplace=True)

# merge con i soli articoli attivi
dfM = dfC.merge(dfI_attivi, how='left', on='Codice', suffixes=('', '-I'))

# fallback su codice produttore: necessario quando il codice articolo è cambiato,
# ma il codice produttore punta a un articolo attivo
dfM_not_found = dfM[dfM['Descrizione-I'].isna()].copy()
if not dfM_not_found.empty and 'Codice-produttore' in dfI_attivi.columns:
    dfI_attivi_by_prod = (
        dfI_attivi.dropna(subset=['Codice-produttore'])
        .drop_duplicates(subset='Codice-produttore', keep='first')
    )
    dfM_not_found_by_prod = dfM_not_found[
        dfM_not_found['Codice-produttore'].notna() & dfM_not_found['Codice-produttore'].astype(str).str.strip().ne('')
    ].merge(
        dfI_attivi_by_prod,
        how='left',
        on='Codice-produttore',
        suffixes=('', '-FB')
    )

    cols_fb = [c for c in dfM_not_found_by_prod.columns if c.endswith('-FB')]
    if cols_fb:
        first_col_fb = cols_fb[0]
        matched_fb = dfM_not_found_by_prod[first_col_fb].notna()
        for col in cols_fb:
            target_col = col.replace('-FB', '')
            if target_col in dfM.columns:
                merged_map = dfM_not_found_by_prod.loc[matched_fb, ['Codice', col]].drop_duplicates(subset='Codice')
                if not merged_map.empty:
                    dfM = dfM.merge(merged_map, on='Codice', how='left', suffixes=('', '-TMP'))
                    dfM[target_col] = dfM[target_col].combine_first(dfM[col])
                    dfM.drop(columns=[col], inplace=True)
dfM.columns = [c.replace("\n", "_") for c in dfM.columns]
dfM.columns = [c.replace(" ", "-") for c in dfM.columns]

# Elimina le colonne in col_drop da dfM
col_drop = ['Obsoleto',	'MRP',	'Vecchio-codice',	'Rit_EscludiCalcolo', 'StampaForfait_Flg',
          'Lst-scaglioni-VEN',	'Lst-scaglioni-ACQ', 'Peso-netto', 'Colli', 'Lunghezza','Larghezza', 'Altezza',
          'PezziConfezione', 'PrevSpe_CalcoloTp', 'ExportTp', 'OmaggioTp', 'Gest.-distinta-fantasma', 'GG_Scadenza',
          'Attivita_Flg', 'Rapp_FatturazioneTp', 'IdStato_OrigineMerce', 'ValoreUnit_Siae', 'Data-ultima-modifica',
          'Fine-utilizzo', 'Descrizione-breve']
dfM = dfM.drop(columns=col_drop)

# genero dataframe not found
dfMN = dfM[~dfM['Codice'].notna()]
# Elimina le righe con SKU vuoto da dfC
dfC = dfC[dfC['Codice'].notna()]

# rende maiscole le descrizioni
dfM['Descrizione'] = dfM['Descrizione'].str.upper()
dfM['UM'] = dfM['UM'].str.upper()
dfM['Codice-merceologico'] = dfM['Codice-merceologico'].str.upper()

# rendo NF Nan
dfM.loc[dfM['Famiglia'] == 'NF', 'Famiglia'] = pd.NA
dfM.loc[dfM['Famiglia'] == '', 'Famiglia'] = pd.NA

# genero dataframe famiglia mancante
dfFN = dfM[dfM['Famiglia'].isna()]
dfFN = dfFN.dropna(subset=["Codice"], inplace=False)

# drop not found
dfM = dfM.dropna(subset=["Codice"], inplace=False)

# output
dfM.drop_duplicates(subset='Codice', keep='first', inplace=True, ignore_index=True)
dfM.to_excel("file/file_intermedi/merged_imio.xlsx", index=False)

if not dfMN.empty:
    dfMN.drop_duplicates(subset='Codice-produttore', keep='first', inplace=True, ignore_index=True)
    dfMN.to_excel("file/file_intermedi/To_add.xlsx", index=False)
if not dfFN.empty:
    dfFN.drop_duplicates(subset='Codice', keep='first', inplace=True, ignore_index=True)
    dfFN.to_excel("file/file_intermedi/To_no_famiglia.xlsx", index=False)

# segnala articoli trovati solo tra i codici in fine utilizzo
if not dfMN.empty and not dfI_fine_utilizzo.empty:
    codici_fine_utilizzo = set(dfI_fine_utilizzo['Codice'].dropna().astype(str).str.strip())
    cod_prod_fine_utilizzo = set()
    if 'Codice-produttore' in dfI_fine_utilizzo.columns:
        cod_prod_fine_utilizzo = set(dfI_fine_utilizzo['Codice-produttore'].dropna().astype(str).str.strip())

    in_fine_utilizzo = dfMN['Codice'].astype(str).str.strip().isin(codici_fine_utilizzo)
    if 'Codice-produttore' in dfMN.columns:
        in_fine_utilizzo = in_fine_utilizzo | dfMN['Codice-produttore'].astype(str).str.strip().isin(cod_prod_fine_utilizzo)

    dfFU = dfMN[in_fine_utilizzo].copy()
    if not dfFU.empty:
        dfFU.drop_duplicates(subset='Codice-produttore', keep='first', inplace=True, ignore_index=True)
        dfFU.to_excel("file/file_intermedi/To_fine_utilizzo.xlsx", index=False)

# Estrai i valori unici dalla colonna "FAMIGLIA"
famiglia_unique = dfM['Famiglia'].drop_duplicates()
# Rimuovi i valori NaN da famiglia_unique
famiglia_unique = famiglia_unique.dropna()

#leggi file sconti
dfS = pd.read_excel("input/sconti.xlsx")

# Verifica quali valori non sono presenti in famiglia_unique
valori_da_aggiungere = famiglia_unique[~famiglia_unique.isin(dfS['FAMIGLIA'])]
print(valori_da_aggiungere)
# Aggiungi i valori mancanti a dfS
if not valori_da_aggiungere.empty:
    nuove_righe = pd.DataFrame({'FAMIGLIA': valori_da_aggiungere})
    dfS = pd.concat([dfS, nuove_righe], ignore_index=True)
    print(dfS)
    dfS.to_excel("input/sconti.xlsx", index=False)
