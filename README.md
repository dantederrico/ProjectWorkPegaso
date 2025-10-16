# Simulatore Processo di Packing - Centro Amazon

## Descrizione
Questo progetto contiene un simulatore in Python che riproduce il processo di packing di ordini in un centro logistico Amazon.  
Il simulatore modella le diverse fasi di lavorazione (Picking, Controllo qualità, Imballaggio, Etichettatura, Smistamento) per vari tipi di prodotti (cuffie Bluetooth, tablet, stampanti) e consente di analizzare tempi, volumi e probabilità di rilavorazione.

## Funzionalità principali
- Simulazione multithread delle fasi produttive con code dedicate
- Parametri configurabili: numero ordini, tempi di lavorazione, rework, ecc.
- Calcolo di indicatori di performance (KPI) come lead time e tasso di rilavorazione
- Supporto opzionale per analisi dati con pandas e matplotlib (se installati)

## Requisiti
- Python 3.x
- Librerie opzionali (per funzionalità avanzate): pandas, matplotlib (installabili con `pip install pandas matplotlib`)

## Come eseguire il simulatore
1. Aprire un terminale nella cartella del progetto.
2. Eseguire il comando:3. Seguire le istruzioni a schermo per inserire i parametri di simulazione.
4. I risultati vengono mostrati in output e, se disponibile, viene generata un’analisi grafica.

## Note
- La simulazione è uno strumento didattico e sperimentale, non un modello completamente fedele alla realtà produttiva.
- È possibile estendere e personalizzare il codice per adattarlo a scenari specifici o integrare servizi cloud per gestione dati.

---

Per qualsiasi domanda o chiarimento, sono disponibile a fornire supporto.

---

Buona esplorazione del progetto!
