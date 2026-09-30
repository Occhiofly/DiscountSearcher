"""
Pulizia automatica delle sessioni che non servono più.

Una sessione scade dopo 30 giorni senza utilizzo (vedi auth.session_expiry e il
rinnovo in deps.py), oppure viene revocata con "Esci" o cambiando la password.
Da quel momento non apre più niente, ma la sua riga (con il nome del dispositivo)
resterebbe nel database per sempre. Qui la si cancella quando sono passati
RETENTION_DAYS dall'ultimo utilizzo: è quanto dichiara l'informativa privacy
(web/privacy.html), quindi i due valori vanno cambiati insieme.

Le sessioni ancora valide non vengono mai toccate: la condizione richiede che
la sessione sia revocata o già scaduta.
"""
import asyncio
import logging

import database

log = logging.getLogger("uvicorn.error")

RETENTION_DAYS = 30
_INTERVAL_SECONDS = 12 * 3600 #due volte al giorno; e a ogni avvio del server


async def delete_old_sessions():
    """Cancella le sessioni revocate o scadute, inutilizzate da più di RETENTION_DAYS giorni."""
    pool = database.get_pool()
    async with pool.acquire() as conn:
        status = await conn.execute(
            """
            DELETE FROM sessions
            WHERE (revoked OR expires_at < now())
              AND last_used_at < now() - make_interval(days => $1)
            """,
            RETENTION_DAYS,
        )
    deleted = int(status.split()[-1]) #asyncpg restituisce "DELETE <numero>"
    if deleted:
        log.info("Sessioni vecchie cancellate: %d", deleted)
    #Richieste di accesso al sito mai completate (il codice scade dopo 10 minuti,
    #vedi site_login.py). A parte: se la tabella mancasse, le sessioni sono già pulite.
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM login_challenges WHERE created_at < now() - interval '1 day'")
    except Exception:
        log.exception("Pulizia delle richieste di accesso al sito non riuscita")
    #Cambi email mai confermati (i codici scadono dopo 15 minuti, vedi email_change.py)
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM email_changes WHERE created_at < now() - interval '1 day'")
    except Exception:
        log.exception("Pulizia dei cambi email non confermati non riuscita")
    return deleted


async def cleanup_loop():
    """Pulizia periodica, avviata insieme al server (vedi lifespan in main.py)."""
    while True:
        try:
            await delete_old_sessions()
        except Exception:
            #Un errore qui (database momentaneamente irraggiungibile) non deve
            #fermare il ciclo: si riprova al giro successivo
            log.exception("Pulizia delle sessioni non riuscita")
        await asyncio.sleep(_INTERVAL_SECONDS)
