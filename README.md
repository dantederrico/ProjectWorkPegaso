# Simulatore Processo di Packing – Settore Elettronico

## Descrizione

Questo progetto contiene un **simulatore in Python** che riproduce il processo di **packing** di prodotti elettronici in un’azienda manifatturiera del **settore secondario**.

Il modello considera tre tipologie di prodotto:

- Cuffie Bluetooth  
- Tablet  
- Stampante  

e cinque fasi operative in serie:

1. Picking  
2. Controllo qualità  
3. Imballaggio  
4. Etichettatura  
5. Smistamento  

La simulazione è pensata come **simulazione a eventi discreti semplificata**: ogni ordine attraversa tutte le fasi in sequenza e i **tempi di lavorazione** sono gestiti tramite un **orologio simulato interno**, distinto dal tempo reale di esecuzione del programma. Questo permette di calcolare KPI come **lead time** e **makespan** sul solo tempo del modello, in coerenza con l’impostazione teorica del project work.

---

## Caratteristiche principali

- ✔️ Simulazione del processo di packing con tre tipologie di prodotto e cinque fasi in serie  
- ✔️ Parametri configurabili da riga di comando:
  - numero di ordini per tipologia (min/max),
  - range dei tempi di lavorazione (secondi simulati),
  - probabilità di rework,
  - fattore di velocità (*time scale*) per la visualizzazione  
- ✔️ Modellazione della variabilità:
  - tempi estratti in modo stocastico,
  - rework probabilistico con ritardo extra
- ✔️ Gestione del flusso con **code FIFO** e worker (thread) per fase×tipologia
- ✔️ Calcolo dei principali **KPI operativi** sul **tempo simulato**:
  - lead time per ordine,
  - lead time medio/mediano complessivo,
  - lead time medio per tipologia,
  - makespan simulato del lotto
- ✔️ **Export locale opzionale** in:
  - JSON (per analisi con pandas / Excel),
  - TXT (report sintetico leggibile)
- ✔️ Supporto opzionale per analisi e grafici con **pandas** e **matplotlib** (se installati)

---

## Requisiti

- Python 3.x
- Librerie standard (già incluse in Python):  
  `threading`, `queue`, `time`, `random`, `json`, `os`, `datetime`, `statistics`
- Librerie opzionali (per analisi e grafici):
  - `pandas`
  - `matplotlib`

Installabili, se desiderato, con:

```bash
pip install pandas matplotlib

