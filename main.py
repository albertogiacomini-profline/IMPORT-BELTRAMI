import subprocess

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
        subprocess.run(["python", script_path], check=True)
        print(f"Script {script} eseguito con successo.")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di {script}: {e}")
        break  # Interrompi l'esecuzione in caso di errore

print("!!!!!!Esecuzione completata!!!!!!")
