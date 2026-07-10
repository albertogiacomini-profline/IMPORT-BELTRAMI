import pandas as pd

# Verifica lo stato dei Codice-produttore nell'archivio gestionale (export)
# rispetto alla norma NN.NNNN.NNN.NNN (12 cifre), valida per il gruppo
# SRAM/ZIPP/TIME/TRUVATIV (confermato dai codici dello stesso gruppo gia'
# salvati come testo nel listino, es. "00.1918.290.000"). Altri brand
# (CeramicSpeed, Muc-Off, Sigma, Corima, Feedback, ...) usano codici numerici
# nativamente senza punti: non vanno segnalati come errore.
# Produce un resoconto Excel dei codici da correggere manualmente in archivio.
# Script indipendente dalla pipeline principale (main.py): va lanciato a mano.

archivio_f = "input/Esportazione_Articoli - Vista Grid.xlsx"
listino_f = "input/LISTINO GRANDI CLIENTI.xlsx"
report_f = "output/report_codici_produttore_da_correggere.xlsx"

GRUPPO_PUNTI = {"SRAM", "ZIPP", "TIME", "TRUVATIV"}


def schema_punti(cifre: str) -> str:
    return f"{cifre[0:2]}.{cifre[2:6]}.{cifre[6:9]}.{cifre[9:12]}"


def normalizza_ean(v):
    if pd.isna(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def analizza(valore):
    """Ritorna (categoria, codice_proposto) oppure (None, None) se il codice e' ok."""
    if pd.isna(valore):
        return None, None

    if isinstance(valore, (int, float)):
        cifre = str(int(valore)) if isinstance(valore, float) else str(valore)
    else:
        testo = str(valore).strip()
        if not testo.isdigit():
            return None, None
        cifre = testo

    if len(cifre) == 12:
        return "manca schema punti NN.NNNN.NNN.NNN (12 cifre)", schema_punti(cifre)
    return "lunghezza cifre anomala per il gruppo SRAM/ZIPP/TIME/TRUVATIV (verificare a mano)", cifre


# --- mappa EAN -> BRAND dal listino originale ---
dfL = pd.read_excel(listino_f)
dfL["ean_norm"] = dfL["EAN CODE"].apply(normalizza_ean)
mappa_brand = (
    dfL.dropna(subset=["ean_norm"])
    .drop_duplicates(subset="ean_norm", keep="first")
    .set_index("ean_norm")["BRAND"]
)

# --- archivio gestionale ---
dfI = pd.read_excel(archivio_f)
dfI.columns = [c.replace("\n", "_").replace(" ", "-") for c in dfI.columns]
dfI = dfI.loc[:, ~dfI.columns.duplicated()]

# Limita l'analisi ai soli articoli gestiti da questa pipeline Beltrami
# (prefissi CB-/CM-/CK- in "Codice"): lo stesso Codice-produttore/EAN
# puo' comparire anche su articoli di altri canali/fornitori, che non
# devono essere segnalati in questo report.
PREFISSI_PIPELINE = ("CB-", "CM-", "CK-")
dfI = dfI[dfI["Codice"].astype("string").str.strip().str.startswith(PREFISSI_PIPELINE, na=False)]

# escludi i codici gia' eliminati (Fine-utilizzo valorizzata)
righe_totali = len(dfI)
dfI["Fine-utilizzo"] = dfI["Fine-utilizzo"].astype("string").str.strip()
dfI = dfI[dfI["Fine-utilizzo"].isna() | dfI["Fine-utilizzo"].eq("")]
righe_escluse_fu = righe_totali - len(dfI)

dfI["ean_norm"] = dfI["Codice-a-barre"].apply(normalizza_ean)
dfI["BRAND"] = dfI["ean_norm"].map(mappa_brand)

righe = []
for _, row in dfI.iterrows():
    if row["BRAND"] not in GRUPPO_PUNTI:
        continue
    categoria, proposto = analizza(row.get("Codice-produttore"))
    if categoria is None:
        continue
    righe.append({
        "Codice": row.get("Codice"),
        "Brand": row["BRAND"],
        "Descrizione": row.get("Descrizione"),
        "Codice-produttore attuale": row.get("Codice-produttore"),
        "Codice-produttore corretto proposto": proposto,
        "Categoria": categoria,
    })

report = pd.DataFrame(righe)
report.to_excel(report_f, index=False, sheet_name="Codici da correggere")

print(f"Righe totali archivio: {righe_totali}")
print(f"Righe escluse perche' gia' eliminate (Fine-utilizzo valorizzata): {righe_escluse_fu}")
print(f"Righe attive analizzate: {len(dfI)}")
print(f"Righe del gruppo SRAM/ZIPP/TIME/TRUVATIV riconosciute (via EAN): {(dfI['BRAND'].isin(GRUPPO_PUNTI)).sum()}")
print(f"Codici da correggere: {len(report)}")
print(report["Categoria"].value_counts() if not report.empty else "Nessuna anomalia trovata.")
print(f"Report salvato in: {report_f}")
