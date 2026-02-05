import pandas as pd
import os


# Verifica se il file esiste nella cartella specificata
def file_esiste(nome_file, cartella):
    percorso_file = os.path.join(cartella, nome_file)
    return os.path.exists(percorso_file)


# Cartella di output
cartella_output = "output"
cartella_input = "input"

# Nome dei file
file1 = "ord-To_add.xlsx"
file2 = "ord-To_fix.xlsx"
fileg = "Esportazione_Articoli - Vista Grid.xlsx"

# Percorso completo dei file
percorso_file1 = os.path.join(cartella_output, file1)
percorso_file2 = os.path.join(cartella_output, file2)
percorso_fileg = os.path.join(cartella_input, fileg)


# Controlla se il primo file esiste nella cartella di output
if file_esiste(file1, cartella_output):

    # Importa il primo file Excel come DataFrame e assegnalo a df1
    df1 = pd.read_excel(percorso_file1)

    # Rimuovi le righe che non hanno i campi specificati tutti popolati
    df1 = df1.dropna(subset=['CODICE INTERNO', 'UM', 'MERCEOLOGICO', 'FAMIGLIA'], how='any')

    # Rinomina le colonne di df1
    df1 = df1.rename(columns={'CODICE INTERNO': 'Codice',
                              'DESCRIZIONE INTERNA':'Descrizione',
                              'UM': 'UM',
                              'CODICE PRODUTTORE': 'Codice produttore',
                              'MERCEOLOGICO': 'Codice merceologico',
                              'FAMIGLIA': 'Famiglia'})
    print(df1)
    # Importa il file generale Excel come DataFrame e assegnalo a dfg
    dfg = pd.read_excel(percorso_fileg)
    print(dfg)
    # Aggiungi le righe di df1 a dfg
    #dfg = dfg.append(df1, ignore_index=True)
    dfg = pd.concat([dfg, df1], ignore_index=True)
    dfg.to_excel('input/Esportazione_Articoli - Vista Grid.xlsx', index=False)

else:
    print("Il file ",file1," non esiste nella cartella di output.")
    # Ferma lo script o esegui altre operazioni

print("OPERAZIONE TERMINATA")