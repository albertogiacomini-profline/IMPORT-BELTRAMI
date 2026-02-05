import pandas as pd

# import foglio uno
imio_f = "input/Esportazione_Articoli - Vista Grid.xlsx"
cp_f = "file/file_intermedi/clean.xlsx"


def normalize_text_col(series: pd.Series) -> pd.Series:
    """Converte in stringa pulita mantenendo i NaN."""
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    )


# Carico i file
dfI = pd.read_excel(imio_f)
dfC = pd.read_excel(cp_f)

# Uniformo i nomi colonna del file esportazione articoli
dfI.columns = [c.replace("\n", "_") for c in dfI.columns]
dfI.columns = [c.replace(" ", "-") for c in dfI.columns]

# Elimino colonne completamente vuote
dfI.dropna(axis="columns", how="all", inplace=True)

# Normalizzo il codice produttore in entrambi i dataset
dfC["CODICE PRODUTTORE"] = normalize_text_col(dfC["CODICE PRODUTTORE"])
dfI["Codice-produttore"] = normalize_text_col(dfI["Codice-produttore"])

# Separo export articoli in ATTIVI vs DISATTIVATI
# Attivo = Fine-utilizzo vuota
dfI["Fine-utilizzo"] = normalize_text_col(dfI["Fine-utilizzo"])
dfI_active = dfI[dfI["Fine-utilizzo"].isna()].copy()
dfI_inactive = dfI[dfI["Fine-utilizzo"].notna()].copy()

# Escludo codici di sistema (es. "z") che non rappresentano articoli reali
if "Codice" in dfI_active.columns:
    dfI_active = dfI_active[~dfI_active["Codice"].astype("string").str.lower().eq("z")]
if "Codice" in dfI_inactive.columns:
    dfI_inactive = dfI_inactive[~dfI_inactive["Codice"].astype("string").str.lower().eq("z")]

# Mantengo una sola riga per codice produttore (prima occorrenza)
dfI_active = dfI_active.drop_duplicates(subset="Codice-produttore", keep="first", ignore_index=True)
dfI_inactive = dfI_inactive.drop_duplicates(subset="Codice-produttore", keep="first", ignore_index=True)

# Rinomino colonne clean per allineare merge e output
dfC = dfC.rename(
    columns={
        "CODICE PRODUTTORE": "Codice-produttore",
        "EAN": "Codice-a-barre",
        "DESCRIZIONE": "Descrizione",
        "PREZZO GRANDI CLIENTI (IVA ESCL.)": "PREZZO-ACQUISTO",
        "PREZZO NEGOZIO (IVA ESCL.)": "PREZZO-VENDITA",
        "MSRP": "PUBBLICO",
    }
)

# Merge principale: match SOLO su articoli attivi usando Codice-produttore
dfM = dfC.merge(dfI_active, how="left", on="Codice-produttore", suffixes=("", "-I"))

# Pulizia nomi colonna eventuali
dfM.columns = [c.replace("\n", "_") for c in dfM.columns]
dfM.columns = [c.replace(" ", "-") for c in dfM.columns]

# Elimina colonne non utili se presenti
col_drop = [
    "Obsoleto",
    "MRP",
    "Vecchio-codice",
    "Rit_EscludiCalcolo",
    "StampaForfait_Flg",
    "Lst-scaglioni-VEN",
    "Lst-scaglioni-ACQ",
    "Peso-netto",
    "Colli",
    "Lunghezza",
    "Larghezza",
    "Altezza",
    "PezziConfezione",
    "PrevSpe_CalcoloTp",
    "ExportTp",
    "OmaggioTp",
    "Gest.-distinta-fantasma",
    "GG_Scadenza",
    "Attivita_Flg",
    "Rapp_FatturazioneTp",
    "IdStato_OrigineMerce",
    "ValoreUnit_Siae",
    "Data-ultima-modifica",
    "Fine-utilizzo",
    "Descrizione-breve",
]
col_drop_present = [c for c in col_drop if c in dfM.columns]
dfM = dfM.drop(columns=col_drop_present)

# --- TO_ADD ---
# Codici senza match sugli ATTIVI
# (Codice viene dall'export articoli: se è NaN significa non trovato negli attivi)
df_to_add = dfM[dfM["Codice"].isna()].copy()

# Verifico se il codice produttore è presente nei DISATTIVATI
inactive_info = dfI_inactive[["Codice-produttore", "Codice"]].rename(
    columns={"Codice": "Codice-disattivato-associato"}
)

df_to_add = df_to_add.merge(inactive_info, how="left", on="Codice-produttore")
df_to_add["Associato-a-codice-disattivato"] = df_to_add[
    "Codice-disattivato-associato"
].notna()

# --- OUTPUT PRINCIPALE ---
# Mantengo solo i codici matchati sugli attivi
dfM = dfM.dropna(subset=["Codice"], inplace=False)

# Rende maiuscole alcune colonne se presenti
for col in ["Descrizione", "UM", "Codice-merceologico"]:
    if col in dfM.columns:
        dfM[col] = dfM[col].astype("string").str.upper()

# Normalizzo famiglia
if "Famiglia" in dfM.columns:
    dfM.loc[dfM["Famiglia"] == "NF", "Famiglia"] = pd.NA
    dfM.loc[dfM["Famiglia"] == "", "Famiglia"] = pd.NA

# Genero dataframe famiglia mancante
dfFN = pd.DataFrame()
if "Famiglia" in dfM.columns:
    dfFN = dfM[dfM["Famiglia"].isna()].copy()
    dfFN = dfFN.dropna(subset=["Codice"], inplace=False)

# output
dfM.drop_duplicates(subset="Codice", keep="first", inplace=True, ignore_index=True)
dfM.to_excel("file/file_intermedi/merged_imio.xlsx", index=False)

if not df_to_add.empty:
    df_to_add.drop_duplicates(subset="Codice-produttore", keep="first", inplace=True, ignore_index=True)
    df_to_add.to_excel("file/file_intermedi/To_add.xlsx", index=False)

if not dfFN.empty:
    dfFN.drop_duplicates(subset="Codice", keep="first", inplace=True, ignore_index=True)
    dfFN.to_excel("file/file_intermedi/To_no_famiglia.xlsx", index=False)

# Estrai i valori unici dalla colonna "FAMIGLIA"
famiglia_unique = pd.Series(dtype="string")
if "Famiglia" in dfM.columns:
    famiglia_unique = dfM["Famiglia"].drop_duplicates().dropna()

# leggi file sconti
dfS = pd.read_excel("input/sconti.xlsx")

# Verifica quali valori non sono presenti in famiglia_unique
valori_da_aggiungere = famiglia_unique[~famiglia_unique.isin(dfS["FAMIGLIA"])]
print(valori_da_aggiungere)

# Aggiungi i valori mancanti a dfS
if not valori_da_aggiungere.empty:
    nuove_righe = pd.DataFrame({"FAMIGLIA": valori_da_aggiungere})
    dfS = pd.concat([dfS, nuove_righe], ignore_index=True)
    print(dfS)
    dfS.to_excel("input/sconti.xlsx", index=False)
