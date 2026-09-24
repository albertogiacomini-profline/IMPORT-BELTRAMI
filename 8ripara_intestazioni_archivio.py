import pandas as pd
import shutil
from datetime import datetime

# Ripara l'archivio gestionale dopo che 7migra_codici_punti.py ha
# erroneamente salvato il file con le intestazioni normalizzate
# internamente (spazio->trattino) invece dei nomi colonna originali.
# Questo ha causato coppie di colonne duplicate (es. "Codice produttore"
# e "Codice-produttore") quando altri script (5aggiungi add.py) hanno poi
# scritto sullo stesso file usando i nomi colonna originali con lo spazio.
# Fonde le coppie duplicate e ripristina i nomi colonna originali.
# Script una tantum, indipendente dalla pipeline principale.

archivio_f = "input/Esportazione_Articoli - Vista Grid.xlsx"

# (nome-con-trattino introdotto per errore, nome originale con spazio)
COPPIE_DA_FONDERE = [
    ("Codice-merceologico", "Codice merceologico"),
    ("Codice-produttore", "Codice produttore"),
    ("Peso-lordo", "Peso lordo"),
]
SOLO_RINOMINARE = [
    ("Data-ultima-modifica", "Data ultima modifica"),
    ("Fine-utilizzo", "Fine utilizzo"),
    ("Descrizione-breve", "Descrizione breve"),
    ("Ricerca-facilitata", "Ricerca facilitata"),
    ("Vecchio-codice", "Vecchio codice"),
    ("Lst-scaglioni-VEN", "Lst scaglioni VEN"),
    ("Lst-scaglioni-ACQ", "Lst scaglioni ACQ"),
    ("Peso-netto", "Peso netto"),
    ("Gest.-distinta-fantasma", "Gest. distinta fantasma"),
]

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_f = f"input/_backup_preripara_{timestamp}.xlsx"
shutil.copy(archivio_f, backup_f)
print(f"Backup salvato in: {backup_f}")

df = pd.read_excel(archivio_f)

for trattino, spazio in COPPIE_DA_FONDERE:
    entrambi_pieni = df[trattino].notna() & df[spazio].notna()
    conflitti = entrambi_pieni & (df[trattino].astype(str) != df[spazio].astype(str))
    if conflitti.any():
        raise SystemExit(
            f"Conflitto di valori tra '{trattino}' e '{spazio}' su {conflitti.sum()} righe: "
            f"controllo manuale necessario, nessuna modifica salvata."
        )
    df[spazio] = df[spazio].where(df[spazio].notna(), df[trattino])
    df = df.drop(columns=[trattino])

for trattino, spazio in SOLO_RINOMINARE:
    if spazio in df.columns:
        raise SystemExit(
            f"'{spazio}' esiste gia' inaspettatamente: controllo manuale necessario."
        )
    df = df.rename(columns={trattino: spazio})

df.to_excel(archivio_f, index=False)

print(f"Colonne finali: {len(df.columns)}")
print(f"Righe finali: {len(df)}")
print("Riparazione completata.")
