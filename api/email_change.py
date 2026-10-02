"""
Cambio dell'email dell'account, confermato con due codici.

Prima l'email cambiava subito dal profilo (PATCH /me), con la sola password. Chi
scopriva una password poteva quindi mettere il proprio indirizzo e da lì ricevere
i codici di accesso al sito e di recupero password: l'account era perso.

Ora PATCH /me non cambia l'email: prepara la richiesta e manda due codici.
- uno all'indirizzo ATTUALE: prova che a chiedere il cambio è il proprietario
  (chi ha solo la password non lo riceve);
- uno al NUOVO indirizzo: prova che esiste ed è scritto giusto (un errore di
  battitura farebbe perdere l'accesso ai codici).
POST /me/email/confirm con i due codici applica il cambio e avvisa il vecchio
indirizzo. Chi non ha più accesso alla vecchia email chiede al team con un ticket.

Tabella: api/email_change_schema.sql, da eseguire su Supabase PRIMA di pubblicare.
"""
import asyncio
import logging
from datetime import datetime, timezone

import asyncpg

from fastapi import APIRouter, Depends, HTTPException

import auth
import database
import email_utils
import i18n
import rate_limit
from deps import get_current_user
from models import EmailChangeConfirmRequest, MessageResponse

log = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/me/email", tags=["profile"])

_CODE_MINUTES = 15  #validità dei codici, come quello di verifica della registrazione
_MAX_TRIES = 5      #tentativi sbagliati prima di dover ripartire dal profilo


def _hint(address):
    """ "mario.rossi@gmail.com" -> "ma•••@gmail.com" """
    local, _, domain = address.partition("@")
    return f"{local[:2]}•••@{domain}"


def _email_key(user_id):
    return f"email-change:{user_id}"


def check_email_allowed(user_id, lang):
    """429 se per questo account (o in totale) sono partite troppe email con codice."""
    wait = rate_limit.email_wait_seconds(_email_key(user_id))
    if wait:
        minutes = max(1, -(-wait // 60))
        word = i18n.t("minute_singular" if minutes == 1 else "minute_plural", lang)
        raise HTTPException(status_code=429, headers={"Retry-After": str(wait)},
                            detail=i18n.t("too_many_emails", lang, minutes=minutes, minute_word=word))
    if rate_limit.daily_email_limit_reached():
        raise HTTPException(status_code=429, detail=i18n.t("email_daily_limit", lang))


async def start(conn, user_id, old_email, new_email, lang):
    """
    Prepara il cambio (una sola richiesta aperta per account) e restituisce i due
    codici da spedire. Il chiamante li spedisce con send_codes, fuori dalla transazione.
    """
    old_code = auth.generate_verification_code()
    new_code = auth.generate_verification_code()
    await conn.execute(
        """
        INSERT INTO email_changes (user_id, new_email, old_code_hash, new_code_hash)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_id) DO UPDATE
            SET new_email = EXCLUDED.new_email, old_code_hash = EXCLUDED.old_code_hash,
                new_code_hash = EXCLUDED.new_code_hash, attempts = 0, created_at = now()
        """,
        user_id, new_email, auth.hash_token(old_code), auth.hash_token(new_code),
    )
    return old_code, new_code


async def send_codes(user_id, old_email, new_email, old_code, new_code, lang):
    """Spedisce i due codici. True se sono partiti entrambi."""
    rate_limit.record_email(_email_key(user_id))
    try:
        await asyncio.to_thread(email_utils.send_email_change_code, old_email, old_code, new_email,
                                "old", _CODE_MINUTES, lang)
        await asyncio.to_thread(email_utils.send_email_change_code, new_email, new_code, new_email,
                                "new", _CODE_MINUTES, lang)
        return True
    except email_utils.EmailSendError as e:
        log.warning("Codici per il cambio email non inviati: %s", e)
        return False


def pending_info(old_email, new_email, email_sent):
    """Campi aggiunti alla risposta di PATCH /me quando il cambio email aspetta i codici."""
    return {"email_pending": True, "old_email_hint": _hint(old_email),
            "new_email_hint": _hint(new_email), "email_sent": email_sent}


@router.post("/confirm", response_model=MessageResponse)
async def confirm_email_change(payload: EmailChangeConfirmRequest,
                               current_user: dict = Depends(get_current_user)):
    """Applica il cambio email se entrambi i codici sono giusti."""
    lang = current_user["lang"]
    #Gli errori si lanciano DOPO la transazione: dentro, la annullerebbero insieme
    #al conteggio dei tentativi (si potrebbero provare codici all'infinito).
    error = None
    changed = None
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                SELECT c.new_email, c.old_code_hash, c.new_code_hash, c.attempts, u.email AS old_email
                FROM email_changes c JOIN users u ON u.id = c.user_id
                WHERE c.user_id = $1 AND c.created_at > now() - make_interval(mins => $2)
                FOR UPDATE OF c
                """,
                current_user["id"], _CODE_MINUTES,
            )
            if row is None:
                error = HTTPException(status_code=410, detail={"error": "email_change_expired",
                                                               "message": i18n.t("email_change_expired", lang)})
            else:
                old_ok = auth.codes_match(auth.hash_token(payload.old_code), row["old_code_hash"])
                new_ok = auth.codes_match(auth.hash_token(payload.new_code), row["new_code_hash"])
                if old_ok and new_ok:
                    #Tra la richiesta e la conferma qualcun altro può essersi registrato con
                    #quell'indirizzo: il vincolo users_email_unico lo impedisce, e qui si
                    #trasforma in un messaggio chiaro invece di un errore del server. Il
                    #blocco annidato è un savepoint: senza, l'errore annullerebbe tutta la
                    #transazione e non si potrebbe più cancellare la richiesta in sospeso.
                    preso = None
                    try:
                        async with conn.transaction():
                            await conn.execute("UPDATE users SET email = $1 WHERE id = $2",
                                               row["new_email"], current_user["id"])
                    except asyncpg.UniqueViolationError:
                        preso = True
                    await conn.execute("DELETE FROM email_changes WHERE user_id = $1", current_user["id"])
                    if preso:
                        error = HTTPException(status_code=409, detail=i18n.t("email_taken", lang))
                    else:
                        changed = (row["old_email"], row["new_email"])
                else:
                    tries = row["attempts"] + 1
                    if tries >= _MAX_TRIES:
                        await conn.execute("DELETE FROM email_changes WHERE user_id = $1", current_user["id"])
                        error = HTTPException(status_code=410, detail={"error": "email_change_expired",
                                                                       "message": i18n.t("email_change_too_many", lang)})
                    else:
                        await conn.execute("UPDATE email_changes SET attempts = $1 WHERE user_id = $2",
                                           tries, current_user["id"])
                        error = HTTPException(status_code=400, detail=i18n.t("email_change_wrong", lang,
                                                                             left=_MAX_TRIES - tries))
    if error:
        raise error

    old_email, _ = changed
    log.info("Email dell'account %s cambiata con i due codici", current_user["id"])
    try:
        await asyncio.to_thread(email_utils.send_profile_update_notification, old_email, ["email"],
                                datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S"), current_user["language"])
    except email_utils.EmailSendError:
        pass #Il cambio è comunque avvenuto
    return MessageResponse(message=i18n.t("email_changed", lang))
