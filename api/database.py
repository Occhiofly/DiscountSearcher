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

_pool = None #Il pool vero e proprio, creato da init_pool() all'avvio del server

async def init_pool():
    """
    Crea il pool di connessioni al database, leggendo l'indirizzo da DATABASE_URL
    (definita nel file .env locale, mai nel codice). Va chiamata una sola volta,
    all'avvio del server (vedi il gestore lifespan in main.py).
    """
    global _pool
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL non impostata: controlla il file .env")
    _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)

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
