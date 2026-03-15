# Raptor One – Leva 3

Sistema automatico per calcolo segnali e grafici su ETF a leva 3x (indici, commodities, single stock).

## Struttura

- `scripts/fetch_and_compute.py`  
  Scarica i dati, calcola indicatori, genera segnali e grafici.

- `data/`  
  Contiene i CSV aggiornati con prezzi e indicatori.

- `charts/`  
  Contiene i grafici PNG generati automaticamente.

- `dashboard/index.html`  
  Dashboard semplice che mostra i grafici.

- `.github/workflows/raptor-one.yml`  
  Workflow GitHub Actions che esegue tutto ogni 2 ore.

## Flusso

1. GitHub Actions parte ogni 2 ore.
2. Esegue `scripts/fetch_and_compute.py`.
3. Aggiorna i CSV in `data/`.
4. Genera grafici in `charts/`.
5. La dashboard in `dashboard/index.html` li mostra.
