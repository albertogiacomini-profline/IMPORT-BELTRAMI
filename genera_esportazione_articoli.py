"""
Interroga GestCont e scrive uno snapshot timestampato dell'anagrafica articoli, con solo le
colonne che il resto della pipeline usa davvero (11 invece delle ~50 dell'export manuale
"Vista Grid").

Lanciato a mano genera SEMPRE un nuovo snapshot, senza controllare l'età di quello esistente:
è il modo per forzare un aggiornamento subito, es. quando sai che in gestionale sono appena
cambiati articoli/famiglie.

    ./venv/bin/python3 genera_esportazione_articoli.py

Il controllo automatico "serve rigenerare?" in base all'età del file più recente lo fa main.py
prima di lanciare la pipeline, non questo script.

NB: questa query ha una colonna in più rispetto agli altri progetti sorelli (IMPORT VITTORIA,
IMPORT MICHE, IMPORT SHIMANO): "Fine-utilizzo" (UtilFineDt), che 2ImportIMIO.py usa per separare
gli articoli attivi da quelli disattivati prima del merge. Vedi ATTIVI_DISATTIVATI.md per i
dettagli — se in futuro si porta questa logica anche sugli altri progetti, la query va allineata
allo stesso modo lì.
"""
import glob
import os
from datetime import datetime

import pandas as pd
from colorama import Fore, init

init(autoreset=True)

CARTELLA_SNAPSHOT = "input/esportazione_articoli"
PATTERN_SNAPSHOT = os.path.join(CARTELLA_SNAPSHOT, "esportazione_articoli_*.xlsx")
ORE_VALIDITA = 2  # sotto questa età lo snapshot esistente viene riusato senza reinterrogare il DB

# file legacy generato a mano dall'export "Vista Grid" del gestionale: usato come ultima
# spiaggia se non esiste ancora nessuno snapshot e il DB non è raggiungibile
FILE_LEGACY = "input/Esportazione_Articoli - Vista Grid.xlsx"

QUERY = """
SELECT
    IdArticolo             AS [Codice],
    Descriz                 AS [Descrizione],
    IdUm                      AS [UM],
    BarCode                   AS [Codice a barre],
    IdMerceologico             AS [Codice merceologico],
    IdArticolo_Produttore      AS [Codice produttore],
    BarCode_Produttore          AS [BarCode_Produttore],
    IdFamiglia                   AS [Famiglia],
    PesoLordo                     AS [Peso lordo],
    Volume                         AS [Volume],
    UtilFineDt                      AS [Fine-utilizzo]
FROM veArticoli
"""


def snapshot_piu_recente():
    """Percorso dell'ultimo snapshot generato, o None se non ne esiste ancora nessuno."""
    trovati = sorted(glob.glob(PATTERN_SNAPSHOT))
    return trovati[-1] if trovati else None


def eta_ore(percorso):
    """Da quante ore esiste il file (in base alla data di modifica)."""
    return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(percorso))).total_seconds() / 3600


def file_anagrafica_disponibile():
    """
    Il miglior file utilizzabile SUBITO, senza interrogare il DB: l'ultimo snapshot generato,
    o in mancanza il vecchio export manuale "Vista Grid". None se non c'è proprio nulla.
    """
    snap = snapshot_piu_recente()
    if snap:
        return snap
    if os.path.exists(FILE_LEGACY):
        return FILE_LEGACY
    return None


def _connetti():
    import pymssql
    try:
        from db_config import DB_CONFIG
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Manca 'db_config.py' con le credenziali del database: copia db_config.example.py "
            "in db_config.py e verifica i valori."
        ) from e
    return pymssql.connect(**DB_CONFIG)


def genera_snapshot():
    """Interroga GestCont e scrive un nuovo file timestampato. Solleva un'eccezione se il DB
    non è raggiungibile: chi chiama decide se usare uno snapshot vecchio come fallback."""
    os.makedirs(CARTELLA_SNAPSHOT, exist_ok=True)
    conn = _connetti()
    try:
        cur = conn.cursor(as_dict=True)
        cur.execute(QUERY)
        df = pd.DataFrame(cur.fetchall())
    finally:
        conn.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    percorso = os.path.join(CARTELLA_SNAPSHOT, f"esportazione_articoli_{timestamp}.xlsx")
    df.to_excel(percorso, index=False)
    print(Fore.GREEN + f"Anagrafica articoli aggiornata da GestCont: {percorso} ({len(df)} articoli)")
    return percorso


if __name__ == "__main__":
    genera_snapshot()
