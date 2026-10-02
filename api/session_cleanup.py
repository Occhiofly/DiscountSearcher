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

Lo stesso giro cancella anche quello che non serve più: richieste di accesso al sito
e cambi email mai completati (i loro codici scadono in minuti), e gli account mai
confermati dopo UNVERIFIED_RETENTION_DAYS giorni.
"""
import asyncio
import logging

import database

log = logging.getLogger("uvicorn.error")

RETENTION_DAYS = 30
UNVERIFIED_RETENTION_DAYS = 7 #account registrati e mai confermati: vedi delete_unverified_accounts
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
    await delete_unverified_accounts()
    return deleted


async def delete_unverified_accounts():
    """
    Cancella gli account mai confermati dopo UNVERIFIED_RETENTION_DAYS giorni.

    Chi si registra e non inserisce il codice lascia nel database un indirizzo email
    di cui non abbiamo nemmeno la prova che sia suo, e senza questa pulizia resterebbe
    lì per sempre. Il codice vale 15 minuti e se ne può chiedere un altro quando si
    vuole, quindi dopo una settimana quell'account non serve più a nessuno: chi si
    ripresenta si registra di nuovo con lo stesso indirizzo.

    La cancellazione porta via anche sessioni, cronologia e ticket di quell'account
    (ON DELETE CASCADE, vedi schema.sql). Gli account confermati non si toccano.
    Il valore è dichiarato nell'informativa privacy (web/privacy.html e
    web/en/privacy.html): i due vanno cambiati insieme.
    """
    try:
        pool = database.get_pool()
        async with pool.acquire() as conn:
            status = await conn.execute(
                """
                DELETE FROM users
                WHERE NOT email_verified
                  AND created_at < now() - make_interval(days => $1)
                """,
                UNVERIFIED_RETENTION_DAYS,
            )
        cancellati = int(status.split()[-1])
        if cancellati:
            log.info("Account mai confermati cancellati: %d", cancellati)
        return cancellati
    except Exception:
        log.exception("Pulizia degli account mai confermati non riuscita")
        return 0


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
