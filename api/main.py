"""
Server API di Discount Searcher (FastAPI).

Per avviarlo in locale (dalla cartella api/):
    uvicorn main:app --reload

Poi apri nel browser: http://127.0.0.1:8000/health
Se tutto funziona, vedrai: {"status":"ok","database":"connected"}
"""
import asyncio
import os
import uuid
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncpg
import database
import auth
import email_change
from body_limit import BodySizeLimitMiddleware
import maintenance
import email_utils
import i18n
import rate_limit
import release
import session_cleanup
import site_login
import staff
import ticket_mail
import tickets
from deps import get_current_user
from models import (
    RegisterRequest, RegisterResponse, VerifyEmailRequest, MessageResponse,
    ResendCodeRequest, ResendCodeResponse, LoginRequest, LoginResponse, MeResponse,
    SessionInfo, SessionListResponse, UpdateProfileRequest,
    AddHistoryRequest, HistoryEntry, HistoryListResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ProfileUpdateResponse,
)

load_dotenv() #Carica le variabili da .env (DATABASE_URL, credenziali email, ecc.) prima di tutto il resto

_CODE_VALIDITY_MINUTES = 15


def request_lang(request: Request):
    """
    Lingua da usare nella risposta: quella chiesta dal sito o dall'app con
    l'intestazione Accept-Language. Usata come dipendenza negli endpoint.
    """
    return i18n.from_accept_language(request.headers.get("accept-language"))
_MAX_HISTORY = 100 #voci di cronologia conservate per ogni utente (vedi add_history)

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Eseguito UNA VOLTA all'avvio del server, prima di accettare qualsiasi richiesta
    await database.init_pool()
    #Lettura periodica delle risposte dello staff ai ticket, arrivate via email
    mail_task = asyncio.create_task(ticket_mail.background_loop())
    #Cancellazione delle sessioni scadute o revocate da più di 30 giorni
    cleanup_task = asyncio.create_task(session_cleanup.cleanup_loop())
    yield
    #Eseguito UNA VOLTA alla chiusura del server (Ctrl+C)
    for task in (mail_task, cleanup_task):
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    await database.close_pool()

#Documentazione interattiva (/docs, /redoc, /openapi.json): spenta di base, perché
#elencherebbe a chiunque tutti gli indirizzi del server. In locale si accende con
#ENABLE_API_DOCS=1 nel .env; su Render va lasciata spenta.
_docs_on = os.getenv("ENABLE_API_DOCS", "").strip().lower() in ("1", "true", "yes", "on")
app = FastAPI(
    title="Discount Searcher API", lifespan=lifespan,
    docs_url="/docs" if _docs_on else None,
    redoc_url="/redoc" if _docs_on else None,
    openapi_url="/openapi.json" if _docs_on else None,
)
app.include_router(tickets.router) #Endpoint /tickets (vedi tickets.py)
app.include_router(email_change.router) #Conferma del cambio email con due codici (email_change.py)
app.include_router(site_login.router) #Accesso al sito con codice via email (site_login.py)
app.include_router(staff.router) #Endpoint /staff: il team vede e gestisce i ticket dal sito (staff.py)

#Dimensione massima di una richiesta. La più grande legittima è una candidatura con
#allegati (al massimo 10 MB di file, che in base64 diventano ~13,4 MB). Il corpo
#viene letto contando i byte, anche se inviato "a pezzi" senza dichiarare la
#dimensione (vedi body_limit.py). Aggiunto PRIMA del CORS di proposito: così il CORS
#lo avvolge, anche la risposta 413 porta le sue intestazioni e il sito può leggerne
#il messaggio.
_MAX_BODY_BYTES = 15 * 1024 * 1024
app.add_middleware(BodySizeLimitMiddleware, max_bytes=_MAX_BODY_BYTES)

#Modalità manutenzione (MAINTENANCE_MODE=1 su Render, vedi maintenance.py). Aggiunta
#dopo il limite sulle richieste e prima del CORS: risponde 503 senza leggere il corpo
#della richiesta, e il CORS la avvolge, così il sito può leggere il messaggio.
app.add_middleware(maintenance.MaintenanceMiddleware)

#CORS: permette al sito web (una pagina aperta nel browser, su un dominio diverso
#da quello dell'API) di leggere le risposte del server. Senza, il browser blocca
#la risposta anche se il server ha risposto correttamente. Non riguarda l'app
#desktop: requests non è un browser e non applica queste regole.
#
#Le origini autorizzate si leggono da CORS_ORIGINS nel .env (o nelle variabili
#d'ambiente di Render), separate da virgola, es.:
#    CORS_ORIGINS=https://sito-di-esempio.com,https://www.sito-di-esempio.com
#Se non è impostata valgono solo gli indirizzi del sito in locale. Mai "*": la
#lista esplicita impedisce a un sito qualsiasi di usare l'API dal browser di
#un utente.
_DEFAULT_CORS_ORIGINS = "http://127.0.0.1:5510,http://localhost:5510"
_cors_origins = [
    origin.strip().rstrip("/") #"https://sito.it/" e "https://sito.it" devono valere uguale
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    #Il token di sessione viaggia nell'intestazione Authorization, non in un
    #cookie: non servono le "credenziali" CORS (che riguardano i cookie).
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    #Senza questa riga il sito non potrebbe leggere dopo quanti secondi riprovare
    #quando il login risponde 429 (troppi tentativi).
    expose_headers=["Retry-After"],
)

@app.exception_handler(RequestValidationError)
async def readable_validation_error(request: Request, exc: RequestValidationError):
    """
    Dati non validi (422) con un messaggio in italiano, come stringa.

    Di base FastAPI risponde con un elenco tecnico in inglese: l'app desktop lo
    mostrerebbe così com'è all'utente (per esempio registrandosi con una password
    troppo corta). Qui si prende il primo problema e lo si rende leggibile.
    """
    lang = request_lang(request)
    first = exc.errors()[0] if exc.errors() else {}
    field = next((str(p) for p in reversed(first.get("loc", ())) if isinstance(p, str)), "")
    label = i18n.field_label(field, lang)
    ctx = first.get("ctx") or {}
    kind = first.get("type", "")
    if kind == "value_error":
        #I validatori in models.py sollevano una chiave di i18n.py (es. "invalid_gmail")
        key = str(ctx.get("error", "")) or "invalid_generic"
        if key in i18n.MESSAGES:
            message = i18n.t(key, lang, field=label, limit=models_min_password())
        else:
            message = i18n.t("invalid_generic", lang, field=label)
    elif kind == "string_too_long":
        message = i18n.t("invalid_too_long", lang, field=label, limit=ctx.get("max_length"))
    elif kind == "string_too_short":
        message = i18n.t("invalid_too_short", lang, field=label, limit=ctx.get("min_length"))
    elif kind == "missing":
        message = i18n.t("invalid_missing", lang, field=label)
    else:
        message = i18n.t("invalid_generic", lang, field=label)
    return JSONResponse(status_code=422, content={"detail": message})


def models_min_password():
    """Lunghezza minima della password, per il messaggio "almeno N caratteri"."""
    from models import _MIN_PASSWORD_LENGTH
    return _MIN_PASSWORD_LENGTH


def _too_many_emails(wait_seconds, lang):
    minutes = max(1, -(-wait_seconds // 60)) #arrotondato per eccesso: 60 secondi = "1 minuto"
    word = i18n.t("minute_singular" if minutes == 1 else "minute_plural", lang)
    return HTTPException(
        status_code=429,
        detail=i18n.t("too_many_emails", lang, minutes=minutes, minute_word=word),
        headers={"Retry-After": str(wait_seconds)},
    )


def _daily_limit_error(lang):
    return HTTPException(status_code=429, detail=i18n.t("email_daily_limit", lang))


def _check_email_allowed(key, lang):
    """Solleva 429 se per questa chiave (o in totale) sono partite troppe email con codice."""
    wait = rate_limit.email_wait_seconds(key)
    if wait:
        raise _too_many_emails(wait, lang)
    if rate_limit.daily_email_limit_reached():
        raise _daily_limit_error(lang)


@app.get("/status")
async def service_status(lang: str = Depends(request_lang)):
    """
    Stato del servizio per sito e app, letto all'avvio: con la manutenzione accesa
    mostrano la schermata "aggiornamento in corso" invece di andare avanti.
    Non tocca il database, così risponde anche se il database è fermo.

    Nella risposta c'è anche l'ultima versione pubblicata dell'app con le sue novità
    (release.py): l'app la confronta con la propria e avvisa da sola quando ne è uscita
    una nuova, senza bisogno di mandare email a nessuno.
    """
    attiva = maintenance.is_on()
    return {"maintenance": attiva, "message": maintenance.message(lang) if attiva else None,
            "app": release.info(lang)}


@app.get("/health")
async def health_check():
    """
    Endpoint di controllo: verifica non solo che il server sia acceso,
    ma che riesca DAVVERO a parlare col database (esegue una query reale).
    """
    pool = database.get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected" if result == 1 else "errore"}

@app.post("/register", response_model=RegisterResponse, status_code=201)
async def register(payload: RegisterRequest, lang: str = Depends(request_lang)):
    """
    Crea un nuovo account (non ancora verificato) e invia il codice di verifica
    via email. Stessa logica della register_user() del vecchio database.py
    dell'app desktop, spostata qui.
    """
    pool = database.get_pool()

    #Un indirizzo, un account. Questo controllo viene PRIMA del limite agli invii: chi
    #riprova con un indirizzo già usato deve sentirsi dire che è già collegato a un
    #account, non "hai già chiesto un codice da poco" (che è vero ma non spiega niente).
    #Qui non si spedisce nulla, quindi non consuma il budget delle email.
    async with pool.acquire() as conn:
        if await conn.fetchval("SELECT 1 FROM users WHERE lower(email) = lower($1)", payload.email):
            raise HTTPException(status_code=409, detail=i18n.t("email_taken", lang))

    #Limite agli invii verso lo stesso indirizzo: senza, la registrazione servirebbe a
    #tempestare di email chiunque abbia un indirizzo Gmail
    email_key = f"register:{payload.email.lower()}"
    _check_email_allowed(email_key, lang)

    password_hash = auth.hash_password(payload.password)
    code = auth.generate_verification_code()

    try:
        async with pool.acquire() as conn:
            #La garanzia vera è il vincolo users_email_unico nel database
            #(api/email_unique_schema.sql): due registrazioni nello stesso istante
            #supererebbero entrambe il controllo qui sopra.
            await conn.execute(
                """
                INSERT INTO users (username, password_hash, email, birth_date, verification_code,
                                   code_created_at, language)
                VALUES ($1, $2, $3, $4, $5, now(), $6)
                """,
                payload.username, password_hash, payload.email, payload.birth_date, code, lang,
            )
    except asyncpg.UniqueViolationError as e:
        #Quale dei due vincoli è scattato? Il nome lo dice, e il messaggio cambia di conseguenza.
        chiave = "email_taken" if e.constraint_name == "users_email_unico" else "username_taken"
        raise HTTPException(status_code=409, detail=i18n.t(chiave, lang))

    #L'invio email usa smtplib, che è BLOCCANTE: eseguirlo direttamente qui fermerebbe
    #l'intero server per tutti gli altri, non solo per questa richiesta (stesso identico
    #problema della ricerca che bloccava la finestra dell'app desktop, ma qui più grave:
    #bloccherebbe TUTTI gli utenti collegati in quel momento). asyncio.to_thread lo sposta
    #su un thread separato, lasciando il server libero di rispondere ad altre richieste.
    rate_limit.record_email(email_key)
    email_sent = True
    try:
        await asyncio.to_thread(email_utils.send_verification_email, payload.email, code, lang)
    except email_utils.EmailSendError:
        #L'account è comunque stato creato: l'utente potrà richiedere un nuovo invio
        email_sent = False

    return RegisterResponse(message=i18n.t("registered", lang), email_sent=email_sent)

@app.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest, lang: str = Depends(request_lang)):
    """
    Verifica il codice inserito. Se corretto e non scaduto, attiva l'account.
    Stessa logica di verify_email_code() del vecchio database.py.

    Con un limite ai tentativi sbagliati, come il recupero password: senza, un
    codice a 6 cifre si indovina provando in automatico, e si potrebbe "verificare"
    un indirizzo email che non è il proprio.
    """
    attempts_key = f"verify-code:{payload.username}"
    if rate_limit.is_locked_out(attempts_key):
        wait_seconds = rate_limit.seconds_until_unlock(attempts_key)
        raise HTTPException(
            status_code=429,
            detail=i18n.t("too_many_codes", lang, minutes=wait_seconds // 60 + 1),
            headers={"Retry-After": str(wait_seconds)},
        )

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, verification_code, code_created_at FROM users WHERE username = $1",
            payload.username,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=i18n.t("user_not_found", lang))

        if not row["verification_code"]:
            raise HTTPException(status_code=400, detail=i18n.t("no_pending_code", lang))

        if datetime.now(timezone.utc) - row["code_created_at"] > timedelta(minutes=_CODE_VALIDITY_MINUTES):
            raise HTTPException(status_code=400, detail=i18n.t("code_expired", lang))

        if not auth.codes_match(payload.code.strip(), row["verification_code"]):
            rate_limit.record_failed_attempt(attempts_key)
            raise HTTPException(status_code=400, detail=i18n.t("code_wrong", lang))

        rate_limit.reset_attempts(attempts_key)
        await conn.execute(
            "UPDATE users SET email_verified = true, verification_code = NULL, code_created_at = NULL WHERE id = $1",
            row["id"],
        )

    return MessageResponse(message=i18n.t("email_verified", lang))

@app.post("/resend-code", response_model=ResendCodeResponse)
async def resend_code(payload: ResendCodeRequest, lang: str = Depends(request_lang)):
    """Genera un nuovo codice di verifica e lo invia via email (con un limite agli invii)."""
    email_key = f"verify:{payload.username}"
    _check_email_allowed(email_key, lang)

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, email, email_verified FROM users WHERE username = $1", payload.username)
        if row is None:
            raise HTTPException(status_code=404, detail=i18n.t("user_not_found", lang))
        #Un account già verificato non ha bisogno di codici: niente email inutili
        if row["email_verified"]:
            raise HTTPException(status_code=400, detail=i18n.t("already_verified", lang))

        code = auth.generate_verification_code()
        await conn.execute(
            "UPDATE users SET verification_code = $1, code_created_at = now() WHERE id = $2",
            code, row["id"],
        )

    rate_limit.record_email(email_key)
    email_sent = True
    try:
        await asyncio.to_thread(email_utils.send_verification_email, row["email"], code, lang)
    except email_utils.EmailSendError:
        email_sent = False

    return ResendCodeResponse(message=i18n.t("new_code_sent", lang), email_sent=email_sent)

@app.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, lang: str = Depends(request_lang)):
    """
    Verifica le credenziali e, se corrette, crea una nuova sessione (una riga
    in sessions) e restituisce il token da usare nelle richieste successive.
    """
    #Stessi controlli dell'accesso al sito (site_login.py): limite tentativi PRIMA di
    #toccare il database, messaggio generico per utente o password sbagliati, email
    #da verificare, lingua dell'account aggiornata.
    site_login.raise_if_locked_out(payload.username, lang)

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await site_login.check_credentials(conn, payload.username, payload.password, lang)
        token, _ = await site_login.create_session(conn, row["id"], payload.device_info)

    return LoginResponse(access_token=token, username=row["username"])

@app.get("/me", response_model=MeResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Endpoint protetto di prova: restituisce i dati dell'utente collegato al
    token presentato. Ogni futuro endpoint che richiede login userà la stessa
    identica dipendenza get_current_user.
    """
    return MeResponse(id=current_user["id"], username=current_user["username"], email=current_user["email"])

@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """Elenca i dispositivi/accessi attivi dell'utente loggato."""
    pool = database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, device_info, created_at, last_used_at, expires_at
            FROM sessions
            WHERE user_id = $1 AND revoked = false AND expires_at > now()
            ORDER BY last_used_at DESC
            """,
            current_user["id"],
        )

    sessions = [
        SessionInfo(
            id=row["id"],
            device_info=row["device_info"],
            created_at=row["created_at"],
            last_used_at=row["last_used_at"],
            expires_at=row["expires_at"],
            is_current=(row["id"] == current_user["session_id"]),
        )
        for row in rows
    ]
    return SessionListResponse(sessions=sessions)

@app.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """Revoca SOLO la sessione usata per fare questa richiesta (il dispositivo corrente)."""
    pool = database.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE sessions SET revoked = true WHERE id = $1",
            current_user["session_id"],
        )
    return MessageResponse(message=i18n.t("logged_out", current_user["lang"]))

@app.post("/sessions/{session_id}/revoke", response_model=MessageResponse)
async def revoke_session(session_id: uuid.UUID, current_user: dict = Depends(get_current_user)):
    """
    Revoca una sessione specifica (anche un dispositivo diverso da quello usato
    ora) — questo è il "disconnetti quel dispositivo da remoto".
    """
    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM sessions WHERE id = $1", session_id)

        #Stesso 404 generico sia se la sessione non esiste, sia se esiste ma appartiene
        #a un altro utente: non vogliamo confermare a nessuno l'esistenza di id altrui.
        if row is None or row["user_id"] != current_user["id"]:
            raise HTTPException(status_code=404, detail=i18n.t("session_not_found", current_user["lang"]))

        await conn.execute("UPDATE sessions SET revoked = true WHERE id = $1", session_id)

    return MessageResponse(message=i18n.t("session_revoked", current_user["lang"]))

@app.patch("/me", response_model=ProfileUpdateResponse)
async def update_profile(payload: UpdateProfileRequest, current_user: dict = Depends(get_current_user),
                         lang: str = Depends(request_lang)):
    """
    Aggiorna username/email/password dell'utente loggato. Richiede la password
    attuale come conferma (stessa logica del pannello Profilo dell'app desktop),
    e invia una notifica di sicurezza alla vecchia email dopo ogni modifica.

    L'email NON cambia qui: con la sola password chiunque la conoscesse potrebbe
    mettere il proprio indirizzo e prendersi l'account. Si prepara il cambio e
    partono due codici, all'indirizzo attuale e al nuovo (email_change.py); la
    risposta lo dice con email_pending=true. Username e password invece sì.
    """
    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT username, email, password_hash FROM users WHERE id = $1",
            current_user["id"],
        )
        if row is None:
            raise HTTPException(status_code=404, detail=i18n.t("user_not_found", lang))

        if not auth.verify_password(payload.current_password, row["password_hash"]):
            raise HTTPException(status_code=401, detail=i18n.t("wrong_current_password", lang))

        #Segniamo COSA sta cambiando PRIMA di applicare la modifica, usando i valori
        #attuali letti sopra (non quelli nuovi arrivati nella richiesta).
        changed_fields = []
        if payload.username != row["username"]:
            changed_fields.append("username")
        if payload.email != row["email"]:
            changed_fields.append("email")
        if payload.password is not None:
            changed_fields.append("password")

        if not changed_fields:
            return ProfileUpdateResponse(message=i18n.t("no_changes", lang))

        old_email = row["email"] #L'email a cui notificare il cambiamento è quella di PRIMA
        email_requested = "email" in changed_fields
        if email_requested:
            #Inutile spedire due codici per un indirizzo che non si potrà usare: se è già
            #di un altro account, il cambio fallirebbe alla conferma (vincolo users_email_unico).
            if await conn.fetchval(
                    "SELECT 1 FROM users WHERE lower(email) = lower($1) AND id <> $2",
                    payload.email, current_user["id"]):
                raise HTTPException(status_code=409, detail=i18n.t("email_taken", lang))
            #Il controllo dei limiti viene prima di qualsiasi modifica: se scatta, non cambia niente
            email_change.check_email_allowed(current_user["id"], lang)
            changed_fields.remove("email") #cambierà solo con i due codici

        try:
            async with conn.transaction():
                if payload.password is not None:
                    new_password_hash = auth.hash_password(payload.password)
                    await conn.execute(
                        "UPDATE users SET username = $1, password_hash = $2 WHERE id = $3",
                        payload.username, new_password_hash, current_user["id"],
                    )
                else:
                    await conn.execute(
                        "UPDATE users SET username = $1 WHERE id = $2",
                        payload.username, current_user["id"],
                    )
                codes = (await email_change.start(conn, current_user["id"], old_email, payload.email, lang)
                         if email_requested else None)
        except asyncpg.UniqueViolationError as e:
            chiave = "email_taken" if e.constraint_name == "users_email_unico" else "username_taken"
            raise HTTPException(status_code=409, detail=i18n.t(chiave, lang))

        #Se la password è cambiata, disconnettiamo tutte le ALTRE sessioni (non quella
        #corrente, che ha appena dimostrato di essere legittima inserendo la password
        #attuale) — utile se si sta cambiando la password per un sospetto accesso non autorizzato.
        if payload.password is not None:
            await conn.execute(
                "UPDATE sessions SET revoked = true WHERE user_id = $1 AND id != $2",
                current_user["id"], current_user["session_id"],
            )

    if changed_fields:
        changed_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        try:
            await asyncio.to_thread(email_utils.send_profile_update_notification, old_email,
                                    changed_fields, changed_at, current_user["language"])
        except email_utils.EmailSendError:
            pass #Il profilo è comunque già stato aggiornato correttamente

    if email_requested:
        sent = await email_change.send_codes(current_user["id"], old_email, payload.email, *codes,
                                             current_user["language"])
        return ProfileUpdateResponse(message=i18n.t("email_change_sent", lang),
                                     **email_change.pending_info(old_email, payload.email, sent))
    return ProfileUpdateResponse(message=i18n.t("profile_updated", lang))

@app.post("/history", response_model=MessageResponse, status_code=201)
async def add_history(payload: AddHistoryRequest, current_user: dict = Depends(get_current_user)):
    """
    Registra un gioco come visitato dall'utente loggato.
    Tiene solo le ultime _MAX_HISTORY voci per utente: l'app ne mostra 10 e la
    lettura ne restituisce al massimo 100. Senza un tetto, uno script potrebbe
    riempire il database aggiungendo voci all'infinito.
    """
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO history (user_id, title, deal_id) VALUES ($1, $2, $3)",
                current_user["id"], payload.title, payload.deal_id,
            )
            await conn.execute(
                """
                DELETE FROM history WHERE user_id = $1 AND id NOT IN (
                    SELECT id FROM history WHERE user_id = $1 ORDER BY id DESC LIMIT $2
                )
                """,
                current_user["id"], _MAX_HISTORY,
            )
    return MessageResponse(message=i18n.t("history_added", current_user["lang"]))

@app.get("/history", response_model=HistoryListResponse)
async def get_history(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Restituisce gli ultimi giochi visitati dall'utente loggato (i più recenti prima).
    'limit' è un parametro nell'URL (es. /history?limit=5), non nel corpo della richiesta:
    Query(..., ge=1, le=100) fa validare automaticamente a FastAPI che sia tra 1 e 100,
    restituendo un 422 chiaro se non lo è, senza bisogno di controllarlo a mano.
    """
    pool = database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, title, deal_id, viewed_at FROM history WHERE user_id = $1 ORDER BY id DESC LIMIT $2",
            current_user["id"], limit,
        )

    entries = [
        HistoryEntry(id=r["id"], title=r["title"], deal_id=r["deal_id"], viewed_at=r["viewed_at"])
        for r in rows
    ]
    return HistoryListResponse(history=entries)

@app.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest, lang: str = Depends(request_lang)):
    """
    Genera un codice per reimpostare la password e lo invia all'email registrata
    sull'account. Risponde SEMPRE con lo stesso messaggio generico, anche se lo
    username non esiste — altrimenti questo endpoint diventerebbe un modo per
    scoprire quali username sono registrati nel sistema, provandone tanti di seguito.
    """
    generic_message = i18n.t("forgot_generic", lang)

    #Troppe richieste per lo stesso username: stesso messaggio, ma nessuna email.
    #Un 429 qui rivelerebbe poco, ma il messaggio generico non rivela niente, e chi
    #ha chiesto il codice da poco lo trova già nella casella.
    email_key = f"reset:{payload.username}"
    if rate_limit.email_wait_seconds(email_key):
        return MessageResponse(message=generic_message)
    if rate_limit.daily_email_limit_reached():
        raise _daily_limit_error(lang)

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, email, language FROM users WHERE username = $1", payload.username)
        if row is None:
            return MessageResponse(message=generic_message)

        code = auth.generate_verification_code() #Stesso generatore a 6 cifre della verifica email
        await conn.execute(
            "UPDATE users SET reset_code = $1, reset_code_created_at = now() WHERE id = $2",
            code, row["id"],
        )

    rate_limit.record_email(email_key)
    try:
        await asyncio.to_thread(email_utils.send_password_reset_email, row["email"], code, row["language"])
    except email_utils.EmailSendError:
        pass #Non riveliamo il fallimento dell'invio: stesso messaggio generico in ogni caso

    return MessageResponse(message=generic_message)

@app.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, lang: str = Depends(request_lang)):
    """
    Verifica il codice di reset e, se corretto, imposta la nuova password.
    A differenza del cambio password dal Profilo, qui disconnettiamo TUTTE le
    sessioni (nessun dispositivo "già autenticato" da risparmiare: l'utente non
    era loggato da nessuna parte quando ha avviato questa procedura).
    """
    #Stesso limite tentativi del login: un codice a 6 cifre è indovinabile a
    #forza bruta entro i 15 minuti di validità, senza un freno ai tentativi.
    if rate_limit.is_locked_out(payload.username):
        wait_seconds = rate_limit.seconds_until_unlock(payload.username)
        wait_minutes = wait_seconds // 60 + 1
        raise HTTPException(
            status_code=429,
            detail=i18n.t("too_many_attempts", lang, minutes=wait_minutes),
            headers={"Retry-After": str(wait_seconds)},
        )

    pool = database.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, reset_code, reset_code_created_at, language FROM users WHERE username = $1",
            payload.username,
        )

        if row is None or not row["reset_code"]:
            rate_limit.record_failed_attempt(payload.username)
            raise HTTPException(status_code=400, detail=i18n.t("reset_code_invalid", lang))

        if datetime.now(timezone.utc) - row["reset_code_created_at"] > timedelta(minutes=_CODE_VALIDITY_MINUTES):
            rate_limit.record_failed_attempt(payload.username)
            raise HTTPException(status_code=400, detail=i18n.t("code_expired", lang))

        if not auth.codes_match(payload.code.strip(), row["reset_code"]):
            rate_limit.record_failed_attempt(payload.username)
            raise HTTPException(status_code=400, detail=i18n.t("code_wrong", lang))

        rate_limit.reset_attempts(payload.username)

        new_password_hash = auth.hash_password(payload.new_password)
        await conn.execute(
            "UPDATE users SET password_hash = $1, reset_code = NULL, reset_code_created_at = NULL WHERE id = $2",
            new_password_hash, row["id"],
        )
        await conn.execute("UPDATE sessions SET revoked = true WHERE user_id = $1", row["id"])

    try:
        await asyncio.to_thread(email_utils.send_password_reset_confirmation, row["email"], row["language"])
    except email_utils.EmailSendError:
        pass

    return MessageResponse(message=i18n.t("password_reset_done", lang))
