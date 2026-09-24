import os
import pandas as pd
from colorama import Fore, init
import genera_esportazione_articoli as genex

init(autoreset=True)

# import foglio uno
cp_f = "file/file_intermedi/clean.xlsx"

if not os.path.exists(cp_f):
    raise FileNotFoundError(
        f"Non trovo '{cp_f}': lancia prima 1ImportF.py (genera il file pulito dal listino fornitore)."
    )

# anagrafica articoli: usa l'ultimo snapshot generato da GestCont (o il vecchio export manuale
# se non ne esiste ancora uno). Il controllo "è abbastanza fresco?" e l'eventuale rigenerazione
# li fa main.py prima di arrivare qui — questo script si limita a leggere quello che trova.
# NB: la query di questo progetto include anche "Fine-utilizzo" (UtilFineDt), usata sotto per
# lo split attivi/disattivati — vedi ATTIVI_DISATTIVATI.md.
imio_f = genex.file_anagrafica_disponibile()
if imio_f is None:
    raise FileNotFoundError(
        "Nessuna anagrafica articoli disponibile: lancia genera_esportazione_articoli.py "
        "(o main.py, che lo fa in automatico) prima di continuare."
    )


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

# Colonne indispensabili più avanti nello script: se mancano (es. l'export del gestionale ha
# cambiato un nome colonna, o si è tornati al file legacy senza Fine-utilizzo) meglio fermarsi
# qui con un elenco chiaro
colonne_richieste = ['Codice', 'Codice-produttore', 'Fine-utilizzo', 'Descrizione', 'UM',
                      'Codice-merceologico', 'Famiglia']
colonne_mancanti = [c for c in colonne_richieste if c not in dfI.columns]
if colonne_mancanti:
    raise ValueError(
        f"Nell'anagrafica articoli '{imio_f}' mancano le colonne richieste: {colonne_mancanti}. "
        f"Colonne trovate: {dfI.columns.tolist()}"
    )

# Normalizzo il codice produttore in entrambi i dataset
dfC["CODICE PRODUTTORE"] = normalize_text_col(dfC["CODICE PRODUTTORE"])
dfI["Codice-produttore"] = normalize_text_col(dfI["Codice-produttore"])

# Rinomino colonne clean per allineare merge e output (anticipato qui,
# serve gia' sotto per il rilevamento degli ambigui)
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

# Mantengo SOLO gli articoli gestiti da questa pipeline Beltrami: in
# anagrafica lo stesso "Codice-produttore" puo' comparire su piu'
# articoli con prefissi diversi di "Codice" (es. "CB-21573" e
# "CL-21573": stesso EAN/descrizione ma gestito da un altro canale/
# fornitore). Solo i prefissi CB-/CM-/CK- sono di competenza di questa
# pipeline, quindi vanno filtrati QUI, prima dello split
# attivi/disattivati, di drop_duplicates e del merge.
PREFISSI_PIPELINE = ("CB-", "CM-", "CK-")
dfI = dfI[dfI["Codice"].astype("string").str.strip().str.startswith(PREFISSI_PIPELINE, na=False)].copy()

# Separo export articoli in ATTIVI vs DISATTIVATI
# Attivo = Fine-utilizzo vuota
# Inattivo = Fine-utilizzo valorizzata O Codice-produttore vuoto
dfI["Fine-utilizzo"] = normalize_text_col(dfI["Fine-utilizzo"])
inactive_mask = dfI["Fine-utilizzo"].notna() | dfI["Codice-produttore"].isna()
dfI_active = dfI[~inactive_mask].copy()
dfI_inactive = dfI[inactive_mask].copy()

# Escludo codici di sistema (es. "z") che non rappresentano articoli reali
if "Codice" in dfI_active.columns:
    dfI_active = dfI_active[~dfI_active["Codice"].astype("string").str.lower().eq("z")]
if "Codice" in dfI_inactive.columns:
    dfI_inactive = dfI_inactive[~dfI_inactive["Codice"].astype("string").str.lower().eq("z")]

# --- AMBIGUI ---
# Anche tra i soli prefissi CB-/CM-/CK-, un Codice-produttore del
# listino in lavorazione puo' avere piu' di un candidato in anagrafica
# (es. due categorie Beltrami diverse con lo stesso codice produttore).
# Il drop_duplicates(keep="first") qui sotto ne terrebbe silenziosamente
# solo uno: esporto tutte le righe ambigue per revisione manuale, PRIMA
# della dedup, scope limitato ai codici presenti in questo listino.
codici_ambigui = dfI_active["Codice-produttore"][
    dfI_active["Codice-produttore"].duplicated(keep=False)
]
candidati_ambigui = dfI_active[dfI_active["Codice-produttore"].isin(codici_ambigui)]
dfAmbigui = dfC.merge(candidati_ambigui, how="inner", on="Codice-produttore", suffixes=("", "-I"))
# stessa pulizia nomi colonna applicata a dfM piu' sotto, necessaria per
# essere processato allo stesso modo da "3ordina e aggiungi colonne.py"
dfAmbigui.columns = [c.replace("\n", "_") for c in dfAmbigui.columns]
dfAmbigui.columns = [c.replace(" ", "-") for c in dfAmbigui.columns]

# Mantengo una sola riga per codice produttore (prima occorrenza)
dfI_active = dfI_active.drop_duplicates(subset="Codice-produttore", keep="first", ignore_index=True)
dfI_inactive = dfI_inactive.drop_duplicates(subset="Codice-produttore", keep="first", ignore_index=True)

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

if not dfAmbigui.empty:
    dfAmbigui.to_excel("file/file_intermedi/To_ambigui.xlsx", index=False)

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

# contatori errori
num_righen = dfFN.shape[0]
print((Fore.GREEN if num_righen == 0 else Fore.RED) + f"Famiglia mancante: {num_righen}")

num_righenm = df_to_add.shape[0]
print((Fore.GREEN if num_righenm == 0 else Fore.RED) + f"Codice mancante: {num_righenm}")

num_ambigui = dfAmbigui.shape[0]
print((Fore.GREEN if num_ambigui == 0 else Fore.RED) + f"Codici ambigui (revisione manuale): {num_ambigui}")

print(f"Anagrafica articoli usata: {imio_f}")
