"""
Risposte dello staff ai ticket, lette dalla casella Gmail del server (IMAP).

Come funziona:
1. Quando un utente apre un ticket, lo staff riceve un'email con oggetto
   "[DS-1001] ..." e Reply-To uguale all'indirizzo del server (GMAIL_ADDRESS).
2. Chi risponde dal proprio client email manda quindi la risposta a quella casella.
3. sync_if_due() / background_loop() leggono le email con "[DS-<numero>]"
   nell'oggetto, verificano che arrivino davvero da un membro dello staff,
   tolgono il testo citato e aggiungono la risposta al ticket; poi avvisano
   l'utente via email.

Quando gira:
- in background ogni 2 minuti, finché il server è acceso;
- e subito prima di mostrare i ticket a un utente (al massimo una volta al
  minuto): se il server era in pausa (es. piano gratuito di Render), le
  risposte arrivate nel frattempo compaiono comunque appena qualcuno apre la
  pagina.

Configurazione (variabili d'ambiente):
- GMAIL_ADDRESS / GMAIL_APP_PASSWORD: le stesse usate per inviare le email.
  La "password per le app" di Google vale anche per leggere la casella.
- SUPPORT_STAFF: chi riceve i ticket e può rispondere, es. "Supporto <searcherdiscuont@gmail.com>".
  Se manca, la lettura delle risposte è disattivata.

Due modi di rispondere, anche insieme:

A) Dall'account del server stesso (SUPPORT_STAFF contiene GMAIL_ADDRESS).
   Lo staff accede a quella casella e risponde alla notifica. La risposta è
   un'email che l'account manda a sé stesso: Gmail non le applica i controlli
   anti-falsificazione, quindi la leggiamo dalla cartella "Posta inviata", dove
   può scrivere solo chi ha accesso all'account. Nella stessa cartella finiscono
   anche le notifiche inviate dal server: le escludiamo grazie all'intestazione
   X-DS-Notification e perché non sono risposte (manca In-Reply-To).

B) Da indirizzi diversi (es. personali). La risposta arriva nella Posta in
   arrivo del server e la accettiamo solo se Gmail certifica il mittente
   (DMARC/DKIM): senza, chiunque potrebbe fingersi lo staff.
"""
import asyncio
import email
import hashlib
import imaplib
import logging
import os
import re
import time
from datetime import datetime, timedelta, timezone

import i18n
from email import policy
from email.utils import getaddresses, parseaddr
from html import unescape

import database
import email_utils

log = logging.getLogger("uvicorn.error") #Stesso logger di uvicorn: i messaggi compaiono nei log di Render

_IMAP_HOST = "imap.gmail.com"
_TAG = re.compile(r"\[DS-(\d{1,12})\]")
_SYNC_MIN_INTERVAL = 60      #secondi fra due letture della casella
_BACKGROUND_INTERVAL = 120   #secondi fra due letture automatiche
_LOOKBACK_DAYS = 14          #quanto indietro guardare nella casella
_MAX_BODY = 20000

STATUS_KEYWORDS = {"#inlavorazione": "progress", "#risolto": "resolved", "#chiuso": "closed"}
#Etichette per lo staff (italiano) e chiavi per i testi tradotti dell'utente (i18n.py)
STATUS_LABELS = {
    "open": "Aperto", "progress": "In lavorazione", "waiting": "In attesa di risposta",
    "resolved": "Risolto", "closed": "Chiuso",
}
STATUS_KEYS = {status: f"status_{status}" for status in STATUS_LABELS}

#Nomi dei mesi in inglese per il formato data di IMAP ("16-Sep-2026"): strftime("%b")
#dipende dalla lingua del sistema e su un server in italiano scriverebbe "set".
_IMAP_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def site_ticket_url(ticket_number, lang=i18n.DEFAULT_LANG):
    """
    Link alla pagina del ticket, nella lingua dell'utente: il sito inglese sta in
    /en/ e le sue pagine hanno nomi diversi (vedi web/README.md).
    """
    base = os.environ.get("SITE_URL", "https://discountsearcher.it").rstrip("/")
    if i18n.normalize(lang) == "en":
        return f"{base}/en/ticket-detail?id=DS-{ticket_number}"
    return f"{base}/ticket-dettaglio?id=DS-{ticket_number}"


def staff_directory():
    """{indirizzo in minuscolo: nome} dai membri elencati in SUPPORT_STAFF."""
    staff = {}
    for name, address in getaddresses([os.environ.get("SUPPORT_STAFF", "")]):
        address = address.strip().lower()
        if "@" in address:
            staff[address] = name.strip() or address.split("@")[0]
    return staff


# ---------------------------------------------------------------------------
# Analisi di un'email (funzioni pure: nessuna rete, nessun database)
# ---------------------------------------------------------------------------

def is_authentic(msg, sender):
    """
    Il mittente (From) di un'email si falsifica facilmente: chiunque potrebbe
    scrivere al server fingendosi Vittorio. Per questo guardiamo l'esito dei
    controlli anti-falsificazione che Gmail scrive in Authentication-Results.

    Usiamo solo la PRIMA di quelle intestazioni: è quella aggiunta da Gmail
    alla ricezione. Eventuali altre più in basso potrebbero essere state
    inserite apposta da chi ha inviato il messaggio.

    Accettiamo il messaggio se:
    - DMARC è superato per il dominio del mittente, oppure
    - DKIM è superato con una firma dello stesso dominio del mittente.
    """
    results = msg.get_all("Authentication-Results") or []
    if not results:
        return False
    header = " ".join(str(results[0]).split()).lower()
    if not header.startswith("mx.google.com"):
        return False

    domain = sender.rsplit("@", 1)[-1]
    dmarc = re.search(r"\bdmarc=pass\b[^;]*\bheader\.from=([\w.-]+)", header)
    if dmarc and dmarc.group(1) == domain:
        return True
    for dkim in re.finditer(r"\bdkim=pass\b[^;]*\bheader\.i=@?([\w.-]+)", header):
        if dkim.group(1) == domain:
            return True
    return False


def _html_to_text(html):
    #Tutto ciò che Gmail/Outlook citano sta in un blocco dedicato: lo togliamo per primo
    cut = re.search(r'<div[^>]+class="[^"]*gmail_quote|<blockquote|<div[^>]+id="divRplyFwdMsg"', html, re.I)
    if cut:
        html = html[:cut.start()]
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
    html = re.sub(r"<br\s*/?>|</(p|div|li|tr|h\d)>", "\n", html, flags=re.I)
    return unescape(re.sub(r"<[^>]+>", "", html))


def extract_text(msg):
    """Testo leggibile del messaggio: la parte text/plain, o quella HTML ripulita."""
    part = msg
    if msg.is_multipart():
        plain = html = None
        for candidate in msg.walk():
            if candidate.is_multipart() or candidate.get_content_disposition() == "attachment":
                continue
            ctype = candidate.get_content_type()
            if ctype == "text/plain" and plain is None:
                plain = candidate
            elif ctype == "text/html" and html is None:
                html = candidate
        part = plain or html
        if part is None:
            return ""
    try:
        text = part.get_content()
    except (LookupError, KeyError):
        #Charset sconosciuto: meglio un testo con qualche carattere sbagliato che niente
        text = part.get_payload(decode=True).decode("utf-8", errors="replace")
    if part.get_content_type() == "text/html":
        text = _html_to_text(text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


#Righe che introducono il messaggio citato, nei formati più comuni in italiano e inglese
_QUOTE_INTRO = re.compile(r"^\s*(il giorno\b|on\b|il\s.+\bha scritto:|.*\bwrote:\s*$|.*\bha scritto:\s*$)", re.I)
#Fine dell'intestazione della citazione. \s+ fra "ha" e "scritto": Gmail va a capo a circa
#78 caratteri e può spezzare la riga proprio lì ("... <indirizzo> ha" / "scritto:").
_QUOTE_INTRO_END = re.compile(r"\b(ha\s+scritto|wrote)\s*:\s*$", re.I)
_SEPARATORS = re.compile(
    r"^\s*(-{2,}\s*(messaggio originale|original message|messaggio inoltrato|forwarded message)\s*-{2,}"
    r"|_{10,}"
    r"|(da|from):\s.+@.+)\s*$",
    re.I,
)
_SIGNATURE_NOISE = re.compile(r"^\s*(inviato da|sent from)\s.{0,40}$", re.I)


def strip_quoted(text):
    """
    Tiene solo il testo scritto sopra la citazione del messaggio precedente.
    Riconosce: "Il giorno ... ha scritto:" (anche spezzato su più righe, come
    fa Gmail con i nomi lunghi), "On ... wrote:", le righe che iniziano con ">",
    i separatori di Outlook e il delimitatore di firma "-- ".
    """
    lines = text.split("\n")
    end = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">") or stripped == "--" or line.rstrip("\n") == "-- " or _SEPARATORS.match(line):
            end = i
            break
        if _QUOTE_INTRO.match(line):
            #L'intestazione della citazione può proseguire su un paio di righe: la
            #ricomponiamo, così "ha" a fine riga e "scritto:" sulla successiva combaciano
            if any(_QUOTE_INTRO_END.search(" ".join(lines[i:j + 1])) for j in range(i, min(i + 3, len(lines)))):
                end = i
                break

    #Rete di sicurezza: se la citazione inizia con righe ">", l'intestazione che la
    #introduce sta nel blocco di testo subito sopra, comunque sia stata spezzata.
    block_end = end
    while block_end > 0 and not lines[block_end - 1].strip():
        block_end -= 1
    block_start = block_end
    while block_start > 0 and lines[block_start - 1].strip() and block_end - block_start < 4:
        block_start -= 1
    if block_start < block_end and _QUOTE_INTRO_END.search(" ".join(l.strip() for l in lines[block_start:block_end])):
        end = block_start

    kept = lines[:end]
    while kept and (not kept[-1].strip() or _SIGNATURE_NOISE.match(kept[-1])):
        kept.pop()
    return "\n".join(kept).strip()


def split_status_keyword(text):
    """Se la prima riga è una parola chiave di stato la toglie e la restituisce."""
    lines = text.strip().split("\n")
    first = lines[0].strip().lower() if lines else ""
    if first in STATUS_KEYWORDS:
        return STATUS_KEYWORDS[first], "\n".join(lines[1:]).strip()
    return None, text.strip()


def parse_staff_email(raw, staff, *, self_address=None, from_sent_folder=False):
    """
    Analizza un'email grezza. Restituisce un dizionario con l'esito:
    {"message_id", "ticket_number", "accepted", "reason", "staff_name", "status", "body"}

    self_address: l'indirizzo dell'account del server (GMAIL_ADDRESS).
    from_sent_folder: True se l'email viene dalla "Posta inviata" di quell'account
    (modo A nella documentazione in cima al file), False se dalla Posta in arrivo.
    """
    msg = email.message_from_bytes(raw, policy=policy.default)
    message_id = (str(msg.get("Message-ID") or "").strip()
                  or "sha256:" + hashlib.sha256(raw).hexdigest())
    tag = _TAG.search(str(msg.get("Subject") or ""))
    result = {"message_id": message_id, "ticket_number": int(tag.group(1)) if tag else None,
              "accepted": False, "reason": None, "staff_name": None, "status": None, "body": ""}

    if not tag:
        result["reason"] = "oggetto senza codice ticket"
        return result
    sender = parseaddr(str(msg.get("From") or ""))[1].strip().lower()
    if sender not in staff:
        result["reason"] = f"mittente non autorizzato ({sender or 'sconosciuto'})"
        return result

    if from_sent_folder:
        #Posta inviata: autentica per costruzione, ma contiene anche le notifiche del server
        if sender != self_address:
            result["reason"] = f"nella posta inviata con un mittente diverso dall'account ({sender})"
            return result
        if msg.get(email_utils.NOTIFICATION_HEADER):
            result["reason"] = "notifica inviata dal server, non una risposta"
            return result
        if not msg.get("In-Reply-To"):
            result["reason"] = "non è una risposta a una notifica (manca In-Reply-To)"
            return result
    else:
        #Posta in arrivo: un messaggio che dice di venire dall'account del server stesso
        #non va mai accettato da qui (le risposte vere si leggono dalla posta inviata)
        if self_address and sender == self_address:
            result["reason"] = "mittente uguale all'account del server nella posta in arrivo"
            return result
        if not is_authentic(msg, sender):
            result["reason"] = f"verifica DMARC/DKIM non superata per {sender}"
            return result

    status, body = split_status_keyword(strip_quoted(extract_text(msg)))
    if not status and not body:
        result["reason"] = "risposta vuota"
        return result
    result.update(accepted=True, staff_name=staff[sender], status=status, body=body[:_MAX_BODY])
    return result


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

async def _already_processed(pool, message_ids):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT message_id FROM ticket_inbound_emails WHERE message_id = ANY($1::text[])",
            message_ids,
        )
    return {r["message_id"] for r in rows}


async def apply_parsed_email(pool, parsed):
    """
    Registra l'email e, se accettata, aggiorna il ticket. Tutto in una transazione:
    se qualcosa fallisce, l'email non risulta elaborata e verrà ritentata.
    Restituisce l'esito: "reply", "status", "ignored" o "duplicate".
    """
    notify = None
    async with pool.acquire() as conn:
        async with conn.transaction():
            ticket = None
            if parsed["ticket_number"] is not None:
                ticket = await conn.fetchrow(
                    """
                    SELECT tickets.id, tickets.subject, users.email AS user_email,
                           users.language AS user_language
                    FROM tickets JOIN users ON users.id = tickets.user_id
                    WHERE tickets.id = $1
                    FOR UPDATE OF tickets
                    """,
                    parsed["ticket_number"],
                )
            accepted = parsed["accepted"] and ticket is not None
            if parsed["accepted"] and ticket is None:
                parsed["reason"] = f"ticket DS-{parsed['ticket_number']} inesistente"
            outcome = ("reply" if parsed["body"] else "status") if accepted else "ignored"

            #ON CONFLICT: se l'email è già stata elaborata (anche da una lettura
            #contemporanea), ci fermiamo qui senza toccare niente.
            registered = await conn.fetchval(
                """
                INSERT INTO ticket_inbound_emails (message_id, ticket_id, outcome)
                VALUES ($1, $2, $3)
                ON CONFLICT (message_id) DO NOTHING
                RETURNING message_id
                """,
                parsed["message_id"], ticket["id"] if ticket else None, outcome,
            )
            if registered is None:
                return "duplicate"
            if not accepted:
                log.warning("Email ticket ignorata: %s", parsed["reason"])
                return "ignored"

            if parsed["body"]:
                await conn.execute(
                    """
                    INSERT INTO ticket_messages (ticket_id, author_role, author_name, body, email_message_id)
                    VALUES ($1, 'staff', $2, $3, $4)
                    """,
                    ticket["id"], parsed["staff_name"], parsed["body"], parsed["message_id"],
                )
            #Senza parola chiave, una risposta del team significa "tocca all'utente"
            new_status = parsed["status"] or "waiting"
            await conn.execute(
                "UPDATE tickets SET status = $1, updated_at = now() WHERE id = $2",
                new_status, ticket["id"],
            )
            notify = (ticket, new_status)

    ticket, new_status = notify
    try:
        await asyncio.to_thread(
            email_utils.send_ticket_staff_reply_to_user,
            ticket["user_email"], f"DS-{ticket['id']}", ticket["subject"], parsed["staff_name"],
            parsed["body"], STATUS_KEYS[new_status],
            site_ticket_url(ticket["id"], ticket["user_language"]), ticket["user_language"],
        )
    except email_utils.EmailSendError as e:
        #La risposta è comunque salvata e visibile sul sito
        log.warning("Avviso all'utente per DS-%s non inviato: %s", ticket["id"], e)
    return outcome


# ---------------------------------------------------------------------------
# Lettura della casella
# ---------------------------------------------------------------------------

def _imap_date(dt):
    return f"{dt.day:02d}-{_IMAP_MONTHS[dt.month - 1]}-{dt.year}"


def _fetch_parts(imap, uids, spec):
    """FETCH per più UID in un colpo solo: {uid: bytes}."""
    typ, data = imap.uid("FETCH", b",".join(uids), f"({spec})")
    found = {}
    if typ != "OK":
        return found
    for item in data:
        if isinstance(item, tuple):
            uid = re.search(rb"UID (\d+)", item[0])
            if uid:
                found[uid.group(1)] = item[1]
    return found


def _find_sent_folder(imap):
    """
    Nome IMAP della cartella "Posta inviata". Il nome cambia con la lingua
    dell'account ("[Gmail]/Posta inviata", "[Gmail]/Sent Mail", ...), quindi la
    riconosciamo dall'attributo standard \\Sent che Gmail le assegna.
    """
    typ, data = imap.list()
    if typ != "OK":
        return None
    for item in data or []:
        line = item.decode("utf-8", "replace") if isinstance(item, bytes) else str(item)
        flags = line[line.find("(") + 1:line.find(")")].split() if "(" in line else []
        if "\\Sent" in flags:
            name = re.search(r'"((?:[^"\\]|\\.)*)"\s*$', line)
            return name.group(1) if name else line.rsplit(" ", 1)[-1]
    return None


def _process_folder(imap, folder, *, sent, staff, self_address, run, pool, since, stats):
    """Legge una cartella (Posta in arrivo o Posta inviata) ed elabora le email dei ticket."""
    typ, _ = imap.select("INBOX" if folder == "INBOX" else f'"{folder}"', readonly=sent)
    if typ != "OK":
        log.warning("Cartella IMAP non apribile: %s", folder)
        return
    typ, data = imap.uid("SEARCH", None, "SINCE", since)
    uids = data[0].split() if typ == "OK" and data and data[0] else []
    if not uids:
        return

    #Prima solo le intestazioni: scarichiamo il corpo solo delle email che interessano
    fields = f"SUBJECT MESSAGE-ID FROM IN-REPLY-TO {email_utils.NOTIFICATION_HEADER.upper()}"
    headers = _fetch_parts(imap, uids, f"BODY.PEEK[HEADER.FIELDS ({fields})]")
    candidates = []
    for uid, raw_header in headers.items():
        h = email.message_from_bytes(raw_header, policy=policy.default)
        if not _TAG.search(str(h.get("Subject") or "")):
            continue
        sender = parseaddr(str(h.get("From") or ""))[1].strip().lower()
        if sent:
            #Nella posta inviata interessano solo le risposte scritte dall'account:
            #le notifiche del server non vengono nemmeno registrate.
            if sender != self_address or h.get(email_utils.NOTIFICATION_HEADER) or not h.get("In-Reply-To"):
                continue
        elif self_address and sender == self_address:
            #Copia in arrivo di un messaggio scritto dall'account stesso (notifica o
            #risposta): la gestisce la lettura della posta inviata. Registrarla qui come
            #"ignorata" bloccherebbe quella lettura, che userebbe lo stesso Message-ID.
            continue
        candidates.append((uid, str(h.get("Message-ID") or "").strip()))
    if not candidates:
        return

    done = run(_already_processed(pool, [mid for _, mid in candidates if mid]))
    pending = [uid for uid, mid in candidates if not mid or mid not in done]
    stats["checked"] += len(pending)
    if not pending:
        return

    handled = []
    for uid, raw in _fetch_parts(imap, pending, "BODY.PEEK[]").items():
        parsed = parse_staff_email(raw, staff, self_address=self_address, from_sent_folder=sent)
        try:
            outcome = run(apply_parsed_email(pool, parsed))
        except Exception:
            log.exception("Elaborazione dell'email %s non riuscita: verrà ritentata", parsed["message_id"])
            continue
        stats[outcome] += 1
        handled.append(uid)

    #Posta in arrivo: segna come lette le email elaborate (comodo per chi guarda la
    #casella; il registro nel database resta l'unica fonte di verità). La posta
    #inviata è aperta in sola lettura e non va toccata.
    if handled and not sent:
        imap.uid("STORE", b",".join(handled), "+FLAGS", "(\\Seen)")


def _sync_blocking(loop, pool):
    """
    Lavoro bloccante (rete IMAP) eseguito in un thread separato. Le operazioni
    sul database, che sono asincrone, vengono affidate al ciclo principale.
    """
    address = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    staff = staff_directory()
    if not address or not password or not staff:
        return {"enabled": False}
    self_address = address.strip().lower()

    def run(coro):
        return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=60)

    stats = {"enabled": True, "checked": 0, "reply": 0, "status": 0, "ignored": 0, "duplicate": 0}
    since = _imap_date(datetime.now(timezone.utc) - timedelta(days=_LOOKBACK_DAYS))
    common = {"staff": staff, "self_address": self_address, "run": run, "pool": pool, "since": since, "stats": stats}

    with imaplib.IMAP4_SSL(_IMAP_HOST, timeout=20) as imap:
        imap.login(address, password)

        #Modo B: staff con indirizzi diversi dall'account del server
        if any(addr != self_address for addr in staff):
            _process_folder(imap, "INBOX", sent=False, **common)

        #Modo A: lo staff risponde accedendo all'account del server
        if self_address in staff:
            sent_folder = _find_sent_folder(imap)
            if sent_folder:
                _process_folder(imap, sent_folder, sent=True, **common)
            else:
                log.warning("Cartella 'Posta inviata' non trovata: le risposte scritte dall'account "
                            "del server non possono essere lette")
    return stats


_lock = asyncio.Lock()
_last_sync = 0.0
_running_tasks = set() #Riferimenti ai task in corso: senza, potrebbero essere eliminati a metà


async def _locked_sync():
    global _last_sync
    async with _lock:
        if time.monotonic() - _last_sync < _SYNC_MIN_INTERVAL:
            return
        #Aggiornato PRIMA di leggere: se Gmail non risponde non riproviamo a ogni richiesta
        _last_sync = time.monotonic()
        try:
            stats = await asyncio.to_thread(_sync_blocking, asyncio.get_running_loop(), database.get_pool())
            if stats.get("checked"):
                log.info("Risposte ai ticket lette dalla casella: %s", stats)
        except Exception:
            log.exception("Lettura delle risposte ai ticket non riuscita")


async def sync_if_due(wait_seconds=6):
    """
    Legge la casella se non lo si è fatto nell'ultimo minuto. Aspetta al massimo
    wait_seconds: se Gmail è lento, la lettura continua in background e la
    pagina viene servita subito con i dati già presenti.
    """
    if time.monotonic() - _last_sync < _SYNC_MIN_INTERVAL or _lock.locked():
        return
    task = asyncio.create_task(_locked_sync())
    _running_tasks.add(task)
    task.add_done_callback(_running_tasks.discard)
    try:
        await asyncio.wait_for(asyncio.shield(task), wait_seconds)
    except asyncio.TimeoutError:
        pass


async def background_loop():
    """Lettura periodica finché il server è acceso (avviata nel lifespan di main.py)."""
    if not staff_directory():
        log.warning("SUPPORT_STAFF non impostata: le risposte via email ai ticket non verranno lette")
    await asyncio.sleep(5) #Lascia completare l'avvio del server
    while True:
        await _locked_sync()
        await asyncio.sleep(_BACKGROUND_INTERVAL)
