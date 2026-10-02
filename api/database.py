"""
Gestione della connessione al database PostgreSQL (Supabase), lato server.

A differenza del vecchio database.py dell'app desktop (una connessione sqlite3
aperta e chiusa ad ogni operazione), qui usiamo un "pool" di connessioni
asincrono (asyncpg): un piccolo gruppo di connessioni già aperte e pronte,
condivise tra tutte le richieste che arrivano al server. Va creato una sola
volta all'avvio del server, non ad ogni richiesta.
"""
import asyncpg
import os
import re
from urllib.parse import quote, unquote

_pool = None #Il pool vero e proprio, creato da init_pool() all'avvio del server

#postgresql://utente:password@host:porta/nome — la password è tutto quello che sta tra i
#primi due punti e l'ULTIMA chiocciola, perché può contenerne una lei stessa.
_INDIRIZZO = re.compile(r"^(?P<schema>[a-zA-Z0-9+]+://)(?P<utente>[^:/@]+):(?P<password>.*)@(?P<resto>[^@]+)$")


def normalizza_indirizzo(database_url):
    """
    Rende innocui i caratteri speciali della password dentro DATABASE_URL.

    Una password che contiene `? / # @ %` spezza l'indirizzo: `?` fa iniziare la
    stringa di ricerca, `/` il nome del database, e asyncpg si fermava con un
    messaggio incomprensibile ("bad query field") senza dire che il problema era la
    password. Qui la si ricodifica (`?` diventa `%3F` e così via) lasciando intatto
    tutto il resto. Una password già codificata viene riconosciuta e lasciata stare,
    altrimenti codificarla due volte la cambierebbe.

    Resta un caso che non si può distinguere: una password che contiene davvero la
    sequenza `%3F` viene presa per una password già codificata. È un prezzo
    accettabile, ma meglio scegliere password senza il carattere `%`.

    Se l'indirizzo non ha la forma attesa si restituisce com'è: lo valuterà asyncpg,
    che per gli altri errori (host sbagliato, porta chiusa) parla già chiaro.
    """
    if not isinstance(database_url, str):
        return database_url
    pezzi = _INDIRIZZO.match(database_url.strip())
    if not pezzi:
        return database_url.strip()
    password = pezzi.group("password")
    in_chiaro = unquote(password, errors="replace")
    #Già codificata? Lo è solo se decodificandola e ricodificandola si riottiene
    #esattamente il valore di partenza. Un `%` da solo (come in "ab%cd") non supera
    #questa prova, quindi viene trattato per quello che è: un carattere qualsiasi.
    if in_chiaro != password and quote(in_chiaro, safe="") == password:
        sicura = password
    else:
        sicura = quote(password, safe="")
    return f'{pezzi.group("schema")}{pezzi.group("utente")}:{sicura}@{pezzi.group("resto")}'


async def init_pool():
    """
    Crea il pool di connessioni al database, leggendo l'indirizzo da DATABASE_URL
    (definita nel file .env locale, mai nel codice). Va chiamata una sola volta,
    all'avvio del server (vedi il gestore lifespan in main.py).

    Se il collegamento non riesce, il server si ferma comunque (senza database non
    può servire niente), ma il log dice cosa controllare invece di una traccia di
    venti righe. La password non finisce mai nel messaggio.
    """
    global _pool
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL non impostata: controlla il file .env")
    try:
        _pool = await asyncpg.create_pool(normalizza_indirizzo(database_url), min_size=1, max_size=5)
    except asyncpg.InvalidPasswordError:
        raise RuntimeError(
            "Il database ha rifiutato la password: DATABASE_URL non corrisponde a quella di "
            "Supabase. Se l'hai cambiata di recente, aggiornala anche qui."
        ) from None
    except (ValueError, IndexError) as errore:
        raise RuntimeError(
            f"DATABASE_URL non è un indirizzo valido ({errore}). La forma attesa è "
            "postgresql://utente:password@host:porta/nome_database, come la dà il pannello "
            "Connect di Supabase."
        ) from None
    except OSError as errore:
        raise RuntimeError(
            f"Database non raggiungibile ({errore}). Controlla che il progetto Supabase sia "
            "attivo e che host e porta siano quelli del pannello Connect."
        ) from None

async def close_pool():
    """Chiude tutte le connessioni del pool. Va chiamata alla chiusura del server."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

def get_pool():
    """
    Restituisce il pool già creato da init_pool(). Solleva un errore chiaro
    (invece di un crash confuso) se qualcosa lo usa prima che il server sia
    completamente avviato.
    """
    if _pool is None:
        raise RuntimeError("Pool non inizializzato: init_pool() non è ancora stato chiamato.")
    return _pool
