import subprocess
import sys

import genera_esportazione_articoli as genex
from colorama import Fore, init

init(autoreset=True)

# Assicura un'anagrafica articoli abbastanza fresca prima di lanciare la pipeline: rigenera da
# GestCont solo se l'ultimo snapshot è più vecchio di ORE_VALIDITA (o se non esiste ancora).
# Per forzare un aggiornamento subito, indipendentemente dall'età, lancia a mano
# genera_esportazione_articoli.py invece di main.py.
avviso_anagrafica = None
snapshot = genex.snapshot_piu_recente()
if not snapshot or genex.eta_ore(snapshot) > genex.ORE_VALIDITA:
    try:
        genex.genera_snapshot()
    except Exception as e:
        disponibile = genex.file_anagrafica_disponibile()
        if disponibile:
            avviso_anagrafica = (
                f"impossibile aggiornare l'anagrafica da GestCont ({e}). "
                f"Proseguo con quella disponibile: {disponibile}."
            )
            print(Fore.RED + f"ATTENZIONE: {avviso_anagrafica}")
        else:
            print(Fore.RED + f"ATTENZIONE: impossibile generare l'anagrafica da GestCont e "
                              f"nessun file di riserva disponibile: {e}")
            sys.exit(1)

# Lista dei file .py da eseguire in sequenza
files_to_execute = ["0Clear_file.py", "1ImportF.py", "2ImportIMIO.py",
                    "3ordina e aggiungi colonne.py", "4creazione prezzi e file.py"]

# Percorso della cartella contenente i file .py (modifica questo percorso con il tuo)
scripts_folder = ""

# Itera attraverso i file e eseguili in sequenza
for script in files_to_execute:
    script_path = scripts_folder + script
    try:
        print(f"Lancio {script} . . .")
        subprocess.run([sys.executable, script_path], check=True)
        print(f"Script {script} eseguito con successo.")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di {script}: {e}")
        break  # Interrompi l'esecuzione in caso di errore

if avviso_anagrafica:
    print(Fore.RED + f"ATTENZIONE: {avviso_anagrafica}")

print("!!!!!!Esecuzione completata!!!!!!")
