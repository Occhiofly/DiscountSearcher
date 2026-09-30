"""
Accesso al sito in due passaggi: password e poi un codice di 6 cifre inviato via email.

Come funziona:
1. POST /site-login con username e password: se sono giusti NON si entra ancora,
   il server manda un codice all'email dell'account e restituisce un
   identificativo della richiesta ("challenge").
2. POST /site-login/verify con quell'identificativo e il codice: solo ora nasce la
   sessione, e viene segnata come "verificata dal sito" (tabella site_sessions).
   POST /site-login/resend manda un codice nuovo per la stessa richiesta.

Perché serve il segno sulla sessione: se il codice lo chiedesse solo la pagina, chi
conosce la password potrebbe chiamare /login come fa l'app e usare quel token sul
sito. Invece ticket e area staff (tickets.py, staff.py) accettano soltanto le
sessioni nate da qui: con un token dell'app rispondono 401 e il sito chiede di
accedere di nuovo. L'app desktop non usa i ticket, quindi non cambia niente per lei.

Tabelle: api/site_login_schema.sql, da eseguire su Supabase PRIMA di pubblicare
questo codice su Render. Se mancano, solo l'accesso al sito e i ticket danno
errore: l'app e /login non le usano.
"""
import asyncio
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request

import auth
import database
import email_utils
import i18n
import rate_limit
from deps import get_current_user
from models import (
    LoginRequest, LoginResponse, SiteLoginChallenge, SiteLoginResendRequest, SiteLoginResend,
    SiteLoginVerifyRequest,
)

router = APIRouter(prefix="/site-login", tags=["site-login"])

_CODE_MINUTES = 10  #validità del codice
_MAX_CODE_TRIES = 5 #errori sul codice prima di dover rimettere la password


def request_lang(request: Request):
    return i18n.from_accept_language(request.headers.get("accept-language"))


# ---------------------------------------------------------------------------
# Controlli in comune con /login (main.py)
# ---------------------------------------------------------------------------

def raise_if_locked_out(username, lang):
    """429 se lo username è bloccato per troppi tentativi, prima ancora di toccare il database."""
    if rate_limit.is_locked_out(username):
        wait_seconds = rate_limit.seconds_until_unlock(username)
        raise HTTPException(
            status_code=429,
            detail=i18n.t("too_many_attempts", lang, minutes=wait_seconds // 60 + 1),
            headers={"Retry-After": str(wait_seconds)},
        )


async def check_credentials(conn, username, password, lang):
    """
    La riga dell'utente se username e password sono giusti e l'email è verificata.
    Altrimenti lo stesso errore di sempre: 401 generico (non diciamo se è sbagliato
    lo username o la password) oppure 403 "email_not_verified".
    """
    row = await conn.fetchrow(
        "SELECT id, username, password_hash, email, email_verified, language FROM users WHERE username = $1",
        username,
    )
    if row is None or not auth.verify_password(password, row["password_hash"]):
        rate_limit.record_failed_attempt(username)
        raise HTTPException(status_code=401, detail=i18n.t("bad_credentials", lang))
    if not row["email_verified"]:
        #Credenziali corrette: non è un tentativo fallito, non lo contiamo contro il limite.
        raise HTTPException(
            status_code=403,
            detail={"error": "email_not_verified", "message": i18n.t("email_not_verified", lang),
                    "email": row["email"]},
        )
    rate_limit.reset_attempts(username)
    #La lingua dell'account segue quella con cui si accede (email nella lingua giusta)
    if row["language"] != lang:
        await conn.execute("UPDATE users SET language = $1 WHERE id = $2", lang, row["id"])
    return row


async def create_session(conn, user_id, device_info):
    """Nuova sessione; restituisce il token in chiaro (nel database resta solo l'hash)."""
    token = auth.generate_session_token()
    session_id = await conn.fetchval(
        "INSERT INTO sessions (user_id, token_hash, device_info, expires_at) VALUES ($1, $2, $3, $4) RETURNING id",
        user_id, auth.hash_token(token), device_info, auth.session_expiry(),
    )
    return token, session_id


# ---------------------------------------------------------------------------
# Sessioni del sito
# ---------------------------------------------------------------------------

def _site_login_required(lang):
    #401 come una sessione scaduta: il sito toglie il token e mostra "Accedi"
    return HTTPException(status_code=401, detail={"error": "site_login_required",
                                                  "message": i18n.t("site_login_required", lang)})


async def get_site_user(current_user: dict = Depends(get_current_user)):
    """Come get_current_user, ma solo per le sessioni aperte dal sito con il codice via email."""
    pool = database.get_pool()
    async with pool.acquire() as conn:
        verified = await conn.fetchval(
            "SELECT 1 FROM site_sessions WHERE session_id = $1", current_user["session_id"],
        )
    if not verified:
        raise _site_login_required(current_user["lang"])
    return current_user


# ---------------------------------------------------------------------------
# Codice via email
# ---------------------------------------------------------------------------

def _email_hint(address):
    """ "mario.rossi@gmail.com" -> "ma•••@gmail.com": abbastanza per riconoscerla, non per leggerla."""
    local, _, domain = address.partition("@")
    return f"{local[:2]}•••@{domain}"


def _email_key(user_id):
    return f"site-login:{user_id}"


def _check_email_allowed(user_id, lang):
    """429 se per questo account (o in totale) sono partite troppe email con codice."""
    wait = rate_limit.email_wait_seconds(_email_key(user_id))
    if wait:
        minutes = max(1, -(-wait // 60))
        word = i18n.t("minute_singular" if minutes == 1 else "minute_plural", lang)
        raise HTTPException(status_code=429, headers={"Retry-After": str(wait)},
                            detail=i18n.t("too_many_emails", lang, minutes=minutes, minute_word=word))
    if rate_limit.daily_email_limit_reached():
        raise HTTPException(status_code=429, detail=i18n.t("email_daily_limit", lang))


async def _send_code(user_id, email, lang, code):
    rate_limit.record_email(_email_key(user_id))
    try:
        await asyncio.to_thread(email_utils.send_site_login_code, email, code, _CODE_MINUTES, lang)
        return True
    except email_utils.EmailSendError:
        return False


@router.post("", response_model=SiteLoginChallenge)
async def site_login(payload: LoginRequest, lang: str = Depends(request_lang)):
    """Primo passaggio: password giusta → codice via email, ma ancora nessuna sessione."""
    raise_if_locked_out(payload.username, lang)
    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await check_credentials(conn, payload.username, payload.password, lang)
        _check_email_allowed(row["id"], lang)
        challenge = secrets.token_urlsafe(24)
        code = auth.generate_verification_code()
        async with conn.transaction():
            #Una sola richiesta aperta per account: la precedente non vale più
            await conn.execute("DELETE FROM login_challenges WHERE user_id = $1", row["id"])
            await conn.execute(
                """
                INSERT INTO login_challenges (id, user_id, code_hash, device_info)
                VALUES ($1, $2, $3, $4)
                """,
                challenge, row["id"], auth.hash_token(code), payload.device_info,
            )
    email_sent = await _send_code(row["id"], row["email"], lang, code)
    return SiteLoginChallenge(challenge=challenge, email_hint=_email_hint(row["email"]),
                              email_sent=email_sent, minutes=_CODE_MINUTES)


async def _open_challenge(conn, challenge, lang):
    """La richiesta ancora valida, con l'utente; altrimenti 410: si ricomincia dalla password."""
    row = await conn.fetchrow(
        """
        SELECT c.id, c.user_id, c.code_hash, c.attempts, c.device_info,
               u.username, u.email, u.language
        FROM login_challenges c JOIN users u ON u.id = c.user_id
        WHERE c.id = $1 AND c.created_at > now() - make_interval(mins => $2)
        FOR UPDATE OF c
        """,
        challenge, _CODE_MINUTES,
    )
    if row is None:
        raise HTTPException(status_code=410, detail={"error": "challenge_expired",
                                                     "message": i18n.t("site_code_expired", lang)})
    return row


@router.post("/verify", response_model=LoginResponse)
async def site_login_verify(payload: SiteLoginVerifyRequest, lang: str = Depends(request_lang)):
    """Secondo passaggio: codice giusto → sessione del sito."""
    #Attenzione: gli errori sul codice si lanciano DOPO la transazione. Lanciati dentro,
    #la annullerebbero, e con lei il conteggio dei tentativi: si potrebbero provare
    #codici all'infinito.
    error = None
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await _open_challenge(conn, payload.challenge, lang)
            if auth.codes_match(auth.hash_token(payload.code), row["code_hash"]):
                await conn.execute("DELETE FROM login_challenges WHERE id = $1", row["id"])
                token, session_id = await create_session(conn, row["user_id"], row["device_info"])
                await conn.execute("INSERT INTO site_sessions (session_id) VALUES ($1)", session_id)
            else:
                tries = row["attempts"] + 1
                if tries >= _MAX_CODE_TRIES:
                    #Troppi errori: la richiesta si butta, serve di nuovo la password
                    await conn.execute("DELETE FROM login_challenges WHERE id = $1", row["id"])
                    rate_limit.record_failed_attempt(row["username"])
                    error = HTTPException(status_code=410, detail={"error": "challenge_expired",
                                                                   "message": i18n.t("site_code_too_many", lang)})
                else:
                    await conn.execute("UPDATE login_challenges SET attempts = $1 WHERE id = $2", tries, row["id"])
                    error = HTTPException(status_code=400, detail=i18n.t("site_code_wrong", lang,
                                                                         left=_MAX_CODE_TRIES - tries))
    if error:
        raise error
    return LoginResponse(access_token=token, username=row["username"])


@router.post("/resend", response_model=SiteLoginResend)
async def site_login_resend(payload: SiteLoginResendRequest, lang: str = Depends(request_lang)):
    """Codice nuovo per la stessa richiesta (quello vecchio non vale più). Limitato come gli altri invii."""
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await _open_challenge(conn, payload.challenge, lang)
            _check_email_allowed(row["user_id"], lang)
            code = auth.generate_verification_code()
            #Il tempo riparte: il codice nuovo vale di nuovo _CODE_MINUTES minuti
            await conn.execute(
                "UPDATE login_challenges SET code_hash = $1, attempts = 0, created_at = now() WHERE id = $2",
                auth.hash_token(code), row["id"],
            )
    email_sent = await _send_code(row["user_id"], row["email"], row["language"], code)
    return SiteLoginResend(email_sent=email_sent)
