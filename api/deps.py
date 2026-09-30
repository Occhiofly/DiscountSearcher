"""
Dipendenza di autenticazione: verifica il token Bearer presentato dal client
contro la tabella sessions, e restituisce l'utente collegato a quella sessione.

Va usata su OGNI endpoint che richiede un utente loggato (in FastAPI, con
Depends(get_current_user)) — è il punto unico dove vive questo controllo,
così non va riscritto endpoint per endpoint.
"""
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import auth
import database
import i18n

_security = HTTPBearer()

def _session_lost(lang):
    """
    Token assente dal database, revocato o scaduto: un solo errore, con un codice
    che il sito e l'app riconoscono ("session_lost") per riportare al login senza
    dover confrontare il testo del messaggio, che cambia con la lingua.
    """
    return HTTPException(status_code=401, detail={"error": "session_lost", "message": i18n.t("session_lost", lang)})


async def get_current_user(request: Request,
                           credentials: HTTPAuthorizationCredentials = Depends(_security)):
    lang = i18n.from_accept_language(request.headers.get("accept-language"))
    token = credentials.credentials
    token_hash = auth.hash_token(token)

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT sessions.id AS session_id, sessions.expires_at, sessions.revoked,
                   users.id AS user_id, users.username, users.email, users.language
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = $1
            """,
            token_hash,
        )

        if row is None or row["revoked"] or datetime.now(timezone.utc) > row["expires_at"]:
            raise _session_lost(lang)

        #Sessione valida e usata ora: la rinnoviamo ("sliding expiration"). Un utente
        #che usa l'app regolarmente non viene mai disconnesso; una sessione abbandonata
        #scade comunque dopo 30 giorni di inattività.
        new_expires_at = auth.session_expiry()
        await conn.execute(
            "UPDATE sessions SET last_used_at = now(), expires_at = $1 WHERE id = $2",
            new_expires_at, row["session_id"],
        )

    #`lang` = lingua della richiesta (per le risposte), `language` = lingua dell'account (per le email)
    return {"id": row["user_id"], "username": row["username"], "email": row["email"],
            "session_id": row["session_id"], "language": row["language"], "lang": lang}
