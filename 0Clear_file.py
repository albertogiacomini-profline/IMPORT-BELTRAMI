import glob
import os

# Specifica una lista di cartelle contenenti i file Excel
cartelle = ["file/file_intermedi",
            "output"]

# Specifica il pattern dei file Excel da cancellare
pattern = "*.xlsx"

# Itera attraverso le cartelle
for cartella in cartelle:
    # Ottieni la lista dei file che corrispondono al pattern nella cartella corrente
    files_da_cancellare = glob.glob(os.path.join(cartella, pattern))

    # Itera attraverso la lista e cancella i file
    for percorso_file_excel in files_da_cancellare:
        if os.path.exists(percorso_file_excel):
            os.remove(percorso_file_excel)
            print(f"Il file {percorso_file_excel} è stato cancellato con successo.")
        else:
            print(f"Il file {percorso_file_excel} non esiste.")
