"""
Numero di versione dell'applicazione, in un posto solo.

Lo usano:
- build_app.py, per scriverlo dentro l'eseguibile (proprietà del file su Windows);
- backend.py, nello User-Agent delle richieste a CheapShark;
- main.py, per confrontarlo con l'ultima versione pubblicata (api/release.json) e
  avvisare che ne è uscita una nuova.

Alzandolo qui va aggiornato anche api/release.json, altrimenti l'app appena compilata
si considera già aggiornata (giusto) ma nessuno viene avvisato della novità.
"""
APP_VERSION = "1.0.9"


def as_tuple(value):
    """
    "1.0.7" -> (1, 0, 7), per confrontare le versioni come numeri e non come testo
    ("1.0.10" viene DOPO "1.0.9", mentre alfabeticamente verrebbe prima).
    Le parti non numeriche vengono ignorate: una versione scritta male non fa crollare l'app.
    """
    parti = []
    for pezzo in str(value or "").split("."):
        pezzo = pezzo.strip()
        if not pezzo.isdigit():
            break
        parti.append(int(pezzo))
    return tuple(parti)


def is_newer(candidata, attuale=None):
    """
    True se `candidata` è più recente di `attuale` (senza indicarla, la versione di
    questa app). `attuale` si legge al momento del confronto e non all'importazione:
    così i collaudi possono far finta di avere una versione più vecchia.
    """
    nuova, mia = as_tuple(candidata), as_tuple(attuale or APP_VERSION)
    return bool(nuova) and bool(mia) and nuova > mia
