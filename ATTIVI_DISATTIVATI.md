# Logica attivi/disattivati — riferimento per eventuale estensione agli altri progetti

Implementata solo su `IMPORT BELTRAMI` (24/09/2026), sul branch
`fix/matching-cross-fornitore-prefissi`. Gli altri progetti sorelli (`IMPORT VITTORIA`,
`IMPORT MICHE`, `IMPORT SHIMANO`) NON hanno questa logica: fanno match sul `Codice-produttore`
contro TUTTA l'anagrafica, senza distinguere articoli disattivati in gestionale. Questo file
descrive cosa fa Beltrami di diverso, per portarlo eventualmente sugli altri progetti in un
secondo momento — non farlo senza discuterne, perché cambia il comportamento del matching.

## Perché serve

In gestionale uno stesso `Codice-produttore` può comparire su più articoli (stesso EAN/
descrizione, canali/fornitori diversi) e un articolo può essere stato disattivato (sostituito,
fuori produzione, ecc.) senza essere cancellato dall'anagrafica. Un merge "ingenuo" sul solo
`Codice-produttore` rischia di:
- abbinare un codice del listino fornitore a un articolo ormai disattivato invece che a quello
  attivo che lo ha sostituito;
- abbinarlo a un articolo gestito da un canale/fornitore diverso (stesso codice produttore,
  prefisso `Codice` diverso).

## Colonna in più nella query GestCont

`genera_esportazione_articoli.py` di Beltrami aggiunge, rispetto alla query standard degli
altri progetti:
```sql
UtilFineDt AS [Fine-utilizzo]
```
(`UtilFineDt` è il campo data di `veArticoli` che, se valorizzato, indica la fine utilizzo
dell'articolo — vedi `references/schema_reference.md` della skill `imio-db`).

## Logica in `2ImportIMIO.py` (Beltrami)

1. **Filtro per pipeline**: tra tutti gli articoli con quel `Codice-produttore`, tiene solo
   quelli il cui `Codice` interno inizia per i prefissi di competenza di questa pipeline
   (`CB-`, `CM-`, `CK-` per Beltrami — **il prefisso è specifico per progetto**, andrebbe
   adattato per ciascuno).
2. **Split attivi/disattivati**: `Attivo = Fine-utilizzo vuota`, `Inattivo = Fine-utilizzo
   valorizzata OR Codice-produttore vuoto`.
3. **Merge principale SOLO sugli attivi**: un codice del listino fornitore si abbina solo a un
   articolo attivo. Se non trova nulla tra gli attivi, finisce in "To_add" (nuovo articolo da
   creare) — ma prima viene controllato se esiste un articolo *disattivato* con lo stesso
   codice produttore (colonna `Associato-a-codice-disattivato` nel file di revisione), utile per
   capire se è un "vecchio" articolo da riattivare/sostituire piuttosto che uno davvero nuovo.
4. **Rilevamento ambigui**: anche dopo il filtro prefissi, lo stesso `Codice-produttore` può
   avere più di un candidato attivo (es. due categorie Beltrami diverse). Prima del
   `drop_duplicates` (che altrimenti ne terrebbe silenziosamente solo uno), queste righe
   vengono esportate a parte (`To_ambigui.xlsx` / `output/ord-To_ambigui.xlsx`) per revisione
   manuale — vengono anche portate fino allo step 3 come quarto file processato.

## Cosa serve per estendere ad altri progetti

1. Aggiungere `UtilFineDt AS [Fine-utilizzo]` alla query di quel progetto in
   `genera_esportazione_articoli.py`.
2. Decidere i prefissi `Codice` di competenza di quella pipeline (se applicabile — non tutti i
   progetti hanno più canali/fornitori che condividono lo stesso `Codice-produttore`; verificare
   prima se il problema esiste davvero per quel fornitore, altrimenti la complessità in più non
   serve).
3. Portare la logica di split attivi/disattivati + ambigui in `2ImportIMIO.py` di quel progetto,
   adattando i nomi delle colonne al resto dello script (schema di base identico su tutti i
   progetti: `Codice`, `Descrizione`, `Codice-a-barre`, `UM`, `Codice-merceologico`, `Famiglia`,
   `Codice-produttore`, `Peso-lordo`, `Volume`).
4. Testare con un run reale e confrontare `Codice mancante`/`Codici ambigui` con un run
   precedente prima di committare — un cambiamento nel criterio di matching può spostare
   parecchi articoli tra "trovato"/"da aggiungere".
