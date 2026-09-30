"""
Limiti anti-abuso, tenuti in memoria (una variabile del processo), non nel database.

1. Tentativi falliti (login, reset password, codice di verifica): dopo troppi
   errori ravvicinati sulla stessa chiave, blocco temporaneo. Rallenta chi prova
   a indovinare una password o un codice a 6 cifre.

2. Invii di email con un codice (verifica, recupero password): al massimo pochi
   invii ravvicinati per lo stesso account o indirizzo, più un tetto complessivo
   giornaliero. Senza, chiunque potrebbe tempestare di email un indirizzo, oppure
   esaurire il limite di invio giornaliero di Gmail: da lì in poi non partirebbero
   più né i codici né le email dei ticket, per nessuno.

Scelta adatta alla scala di questa app — nessuna tabella nuova, nessun costo
aggiuntivo per richiesta. Il contro, da sapere: i conteggi si azzerano a ogni
riavvio del server, e non funzionerebbero se l'app girasse su più server in
parallelo (in quel caso servirebbe una tabella condivisa o un servizio come Redis).

Le chiavi sono stringhe libere: lo username per il login, "verify-code:<username>"
per il codice di verifica, "register:<email>" per gli invii, ecc. Così i
contatori di cose diverse non si mescolano.
"""
import math
import time

_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 15 * 60 #15 minuti

#Oltre questo numero di chiavi si fa pulizia di quelle scadute: senza, chi prova
#tanti username diversi farebbe crescere il dizionario all'infinito.
_MAX_KEYS = 5000

_failed_attempts = {} #chiave -> lista di timestamp dei tentativi falliti recenti


def _prune(key):
    """Toglie i tentativi più vecchi della finestra, così il dizionario non cresce all'infinito."""
    if key not in _failed_attempts:
        return []
    cutoff = time.time() - _WINDOW_SECONDS
    recent = [t for t in _failed_attempts[key] if t > cutoff]
    if recent:
        _failed_attempts[key] = recent
    else:
        _failed_attempts.pop(key, None)
    return recent


def _prune_all(store, window):
    """Pulizia completa, fatta solo quando le chiavi diventano troppe."""
    cutoff = time.time() - window
    for key in [k for k, times in store.items() if not times or max(times) <= cutoff]:
        store.pop(key, None)


def is_locked_out(key):
    """True se questa chiave ha già raggiunto il limite di tentativi falliti recenti."""
    return len(_prune(key)) >= _MAX_ATTEMPTS


def record_failed_attempt(key):
    """Registra un tentativo fallito per questa chiave."""
    if len(_failed_attempts) > _MAX_KEYS:
        _prune_all(_failed_attempts, _WINDOW_SECONDS)
    recent = _prune(key)
    recent.append(time.time())
    _failed_attempts[key] = recent


def reset_attempts(key):
    """Azzera lo storico dei tentativi falliti, da chiamare dopo un successo."""
    _failed_attempts.pop(key, None)


def seconds_until_unlock(key):
    """Quanti secondi mancano prima che il tentativo più vecchio esca dalla finestra."""
    recent = _prune(key)
    if not recent:
        return 0
    oldest = min(recent)
    return max(0, int(_WINDOW_SECONDS - (time.time() - oldest)))


# ---------------------------------------------------------------------------
# Invii di email con un codice
# ---------------------------------------------------------------------------

_EMAIL_MIN_GAP = 60            #secondi minimi fra due invii per la stessa chiave
_EMAIL_PER_KEY = 3             #invii massimi per la stessa chiave...
_EMAIL_KEY_WINDOW = 15 * 60    #...in 15 minuti
#Tetto complessivo di email con codice in 24 ore. Gmail permette circa 500 invii
#al giorno: questo ne lascia sempre una parte per le email dei ticket.
_EMAIL_DAILY_MAX = 200
_EMAIL_DAY = 24 * 3600

_emails_by_key = {} #chiave -> timestamp degli invii recenti
_emails_all = []    #timestamp di tutti gli invii delle ultime 24 ore


def email_wait_seconds(key):
    """
    0 se si può inviare ora un'email con codice per questa chiave, altrimenti i
    secondi da aspettare. Non registra niente: dopo l'invio va chiamata record_email.
    """
    now = time.time()
    recent = [t for t in _emails_by_key.get(key, []) if t > now - _EMAIL_KEY_WINDOW]
    if recent and now - recent[-1] < _EMAIL_MIN_GAP:
        return math.ceil(_EMAIL_MIN_GAP - (now - recent[-1]))
    if len(recent) >= _EMAIL_PER_KEY:
        return math.ceil(_EMAIL_KEY_WINDOW - (now - recent[0]))
    return 0


def daily_email_limit_reached():
    """True se nelle ultime 24 ore sono già partite _EMAIL_DAILY_MAX email con codice."""
    cutoff = time.time() - _EMAIL_DAY
    while _emails_all and _emails_all[0] <= cutoff:
        _emails_all.pop(0)
    return len(_emails_all) >= _EMAIL_DAILY_MAX


def record_email(key):
    """Registra un invio appena fatto (o tentato) per questa chiave."""
    now = time.time()
    if len(_emails_by_key) > _MAX_KEYS:
        _prune_all(_emails_by_key, _EMAIL_KEY_WINDOW)
    recent = [t for t in _emails_by_key.get(key, []) if t > now - _EMAIL_KEY_WINDOW]
    recent.append(now)
    _emails_by_key[key] = recent
    _emails_all.append(now)
