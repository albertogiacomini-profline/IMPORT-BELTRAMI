import pandas as pd
import shutil
from datetime import datetime

# I prodotti del gruppo SRAM/ZIPP/TIME/TRUVATIV finiti in "To_add" dopo
# l'introduzione dello schema a punti (NN.NNNN.NNN.NNN) non sono in realta'
# nuovi: esistono gia' in archivio con il vecchio Codice-produttore senza
# punti, ma il merge non li trova piu' perche' il codice e' cambiato.
# Questo script, per ognuno di questi, cerca (via EAN) la vecchia riga in
# archivio e ne crea una copia con Codice-produttore/Codice aggiornati al
# nuovo formato, lasciando la vecchia riga intatta.
# Script indipendente dalla pipeline principale (main.py): va lanciato a mano
# dopo aver eseguito main.py (che genera file/file_intermedi/To_add.xlsx).

to_add_f = "file/file_intermedi/To_add.xlsx"
archivio_f = "input/Esportazione_Articoli - Vista Grid.xlsx"

GRUPPO_PUNTI = {"SRAM", "ZIPP", "TIME", "TRUVATIV"}


def normalizza_ean(v):
    if pd.isna(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def codice_interno(codice_produttore: str) -> str:
    return f"CB-{codice_produttore}"


# --- backup di sicurezza prima di modificare l'archivio ---
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_f = f"input/_backup_Esportazione_Articoli_{timestamp}.xlsx"
shutil.copy(archivio_f, backup_f)
print(f"Backup archivio salvato in: {backup_f}")

# --- righe To_add del gruppo a punti ---
dfAdd = pd.read_excel(to_add_f)
dfAdd = dfAdd[dfAdd["BRAND"].isin(GRUPPO_PUNTI)].copy()
dfAdd["ean_norm"] = dfAdd["Codice-a-barre"].apply(normalizza_ean)

# --- archivio ---
# NB: si lavora sui nomi colonna ORIGINALI del gestionale (con lo spazio,
# es. "Codice a barre"/"Codice produttore") e li si salva invariati: NON
# rinominare le colonne prima di scrivere il file, altrimenti si creano
# doppioni quando altri script (es. 5aggiungi add.py) scrivono sullo stesso
# file usando i nomi originali.
dfI = pd.read_excel(archivio_f)
dfI["ean_norm"] = dfI["Codice a barre"].apply(normalizza_ean)

# La ricerca della "vecchia riga" via EAN deve restare confinata agli
# articoli gia' gestiti da QUESTA pipeline (prefissi CB-/CM-/CK- in
# "Codice"): lo stesso EAN puo' comparire anche su articoli di altri
# canali/fornitori. NB: si filtra SOLO qui; "dfI" (riusato piu' sotto
# per dfI_finale) resta l'archivio completo e non va toccato.
PREFISSI_PIPELINE = ("CB-", "CM-", "CK-")
dfI_pipeline = dfI[dfI["Codice"].astype("string").str.strip().str.startswith(PREFISSI_PIPELINE, na=False)]

# una vecchia riga per EAN (prima occorrenza, escludendo EAN mancanti)
vecchie_per_ean = (
    dfI_pipeline.dropna(subset=["ean_norm"])
    .drop_duplicates(subset="ean_norm", keep="first")
    .set_index("ean_norm")
)

nuove_righe = []
non_trovate = []

for _, riga_add in dfAdd.iterrows():
    ean = riga_add["ean_norm"]
    if ean is None or ean not in vecchie_per_ean.index:
        non_trovate.append(riga_add)
        continue

    vecchia = vecchie_per_ean.loc[ean].copy()
    nuovo_codice_prod = riga_add["Codice-produttore"]

    nuova = vecchia.copy()
    nuova["Codice produttore"] = nuovo_codice_prod
    nuova["Codice"] = codice_interno(nuovo_codice_prod)
    nuove_righe.append(nuova)

df_nuove = pd.DataFrame(nuove_righe).drop(columns=["ean_norm"], errors="ignore")
df_non_trovate = pd.DataFrame(non_trovate)

# evita di duplicare righe se lo script viene rilanciato: scarta i Codice
# che sono gia' presenti in archivio
codici_gia_presenti = set(dfI["Codice"].astype(str))
if not df_nuove.empty:
    df_nuove = df_nuove[~df_nuove["Codice"].astype(str).isin(codici_gia_presenti)]

dfI_finale = pd.concat(
    [dfI.drop(columns=["ean_norm"]), df_nuove], ignore_index=True
)
dfI_finale.to_excel(archivio_f, index=False)

print(f"Righe 'To_add' del gruppo a punti: {len(dfAdd)}")
print(f"Nuove righe create in archivio (vecchio codice trovato via EAN): {len(df_nuove)}")
print(f"Righe non trovate in archivio (prodotti probabilmente davvero nuovi): {len(df_non_trovate)}")
if not df_non_trovate.empty:
    report_non_trovate_f = "output/report_to_add_senza_vecchio_codice.xlsx"
    df_non_trovate.drop(columns=["ean_norm"], errors="ignore").to_excel(
        report_non_trovate_f, index=False
    )
    print(f"Elenco salvato in: {report_non_trovate_f}")
