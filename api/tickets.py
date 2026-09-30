"""
Ticket di assistenza: endpoint usati dal Centro assistenza del sito.

Tutti richiedono il login (stesso token di sessione dell'app desktop) e ogni
utente vede e modifica SOLO i propri ticket. Un ticket di qualcun altro
risponde 404, esattamente come uno inesistente: non confermiamo a nessuno
quali numeri di ticket esistono.

Le risposte dello staff non passano da qui: arrivano via email e le legge
ticket_mail.py.
"""
import asyncio
import logging
import os
import re

from fastapi import APIRouter, Depends, HTTPException

import attachments as attachment_rules
import database
import email_utils
import i18n
import ticket_mail
from site_login import get_site_user as get_current_user #solo sessioni del sito con codice
from models import (
    TicketCreateRequest, TicketReplyRequest, TicketDetail, TicketListResponse,
    TicketMessageOut, TicketSummary,
)

log = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/tickets", tags=["tickets"])

#Limite anti-abuso: un utente normale non apre 5 ticket in un giorno, e senza un
#tetto un account compromesso potrebbe riempire di email la casella dello staff.
_MAX_TICKETS_PER_DAY = 5

#Ogni risposta dell'utente manda un'email allo staff: senza un tetto, un solo account
#potrebbe riempire la casella ed esaurire il limite giornaliero di invio di Gmail
#(da lì non partirebbero più codici e notifiche per nessuno). Una conversazione
#normale non si avvicina a questo numero.
_MAX_REPLIES_PER_HOUR = 20

#Nomi leggibili delle categorie, per le email allo staff (stessi del sito)
CATEGORY_LABELS = {
    "account": "Account", "accesso": "Accesso", "recupero-password": "Recupero password",
    "verifica-email": "Verifica email", "applicazione": "Applicazione", "offerte": "Offerte e ricerca",
    "filtri": "Filtri", "cronologia": "Cronologia", "bug": "Segnalare un bug", "altro": "Altro",
    #Non è una categoria dell'assistenza: è la candidatura inviata da "Lavora con noi"
    "candidatura": "Candidatura",
}

#Come l'email di conferma chiama il ticket appena aperto. Una candidatura non è
#una richiesta di assistenza: il testo predefinito non andrebbe bene.
_RECEIVED_WHAT = {"candidatura": "what_application"}


def _public_id(number):
    return f"DS-{number}"


def _parse_public_id(value, lang=i18n.DEFAULT_LANG):
    """ "DS-1001" -> 1001. Qualsiasi altro formato è un ticket inesistente."""
    match = re.fullmatch(r"DS-(\d{1,12})", value.strip(), flags=re.I)
    if not match:
        raise _ticket_not_found(lang)
    return int(match.group(1))


def _summary(row):
    return TicketSummary(
        id=_public_id(row["id"]), subject=row["subject"], category=row["category"],
        status=row["status"], created_at=row["created_at"], updated_at=row["updated_at"],
    )


async def _send_quietly(func, *args, **kwargs):
    """Invia un'email senza mai far fallire la richiesta: il ticket è già salvato."""
    try:
        await asyncio.to_thread(func, *args, **kwargs)
    except email_utils.EmailSendError as e:
        log.warning("Email del ticket non inviata: %s", e)


def _staff_recipients():
    return list(ticket_mail.staff_directory().keys())


def _ticket_not_found(lang):
    return HTTPException(status_code=404, detail=i18n.t("ticket_not_found", lang))


async def _load_detail(conn, number, user_id, lang=i18n.DEFAULT_LANG):
    ticket = await conn.fetchrow(
        """
        SELECT id, subject, category, extra, status, created_at, updated_at
        FROM tickets WHERE id = $1 AND user_id = $2
        """,
        number, user_id,
    )
    if ticket is None:
        raise _ticket_not_found(lang)
    messages = await conn.fetch(
        """
        SELECT id, author_role, author_name, body, created_at
        FROM ticket_messages WHERE ticket_id = $1
        ORDER BY created_at, id
        """,
        number,
    )
    return TicketDetail(
        **_summary(ticket).model_dump(),
        extra=ticket["extra"],
        messages=[TicketMessageOut(**dict(m)) for m in messages],
    )


@router.post("", response_model=TicketDetail, status_code=201)
async def create_ticket(payload: TicketCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Apre un ticket: la descrizione diventa il primo messaggio della conversazione.

    Allegati (facoltativi, su qualsiasi ticket): non vengono salvati, viaggiano solo nell'email
    allo staff. Se quell'email non parte, il ticket appena creato viene eliminato
    e l'utente riceve un errore: altrimenti resterebbe un ticket che dice
    "allegati inviati" mentre i file sono andati persi.

    L'email NON parte a transazione aperta né tenendo occupata una connessione
    al database: con gli allegati può richiedere decine di secondi, e le
    connessioni sono poche (vedi database.py). Qualche invio lento in
    contemporanea bloccherebbe login e ticket di tutti gli altri utenti.
    """
    lang = current_user["lang"]
    try:
        files = attachment_rules.decode_all(payload.attachments)
    except attachment_rules.AttachmentError as e:
        raise HTTPException(status_code=400, detail=e.message(lang))
    staff = _staff_recipients()
    if files and not staff:
        log.warning("SUPPORT_STAFF non impostata: ticket con allegati rifiutato")
        raise HTTPException(status_code=503, detail=i18n.t("attachments_not_sent", lang))

    pool = database.get_pool()
    async with pool.acquire() as conn:
        recent = await conn.fetchval(
            "SELECT count(*) FROM tickets WHERE user_id = $1 AND created_at > now() - interval '24 hours'",
            current_user["id"],
        )
        if recent >= _MAX_TICKETS_PER_DAY:
            raise HTTPException(
                status_code=429,
                detail=i18n.t("too_many_tickets", lang),
            )

        async with conn.transaction():
            number = await conn.fetchval(
                """
                INSERT INTO tickets (user_id, subject, category, extra)
                VALUES ($1, $2, $3, $4) RETURNING id
                """,
                current_user["id"], payload.subject, payload.category, payload.extra or None,
            )
            #Nel ticket restano nomi e dimensioni dei file, non i file
            first_message = payload.description
            if files:
                first_message += "\n\n" + attachment_rules.summary_line(files, lang)
            await conn.execute(
                """
                INSERT INTO ticket_messages (ticket_id, author_role, author_name, body)
                VALUES ($1, 'user', $2, $3)
                """,
                number, current_user["username"], first_message,
            )
        detail = await _load_detail(conn, number, current_user["id"], lang)
    #Da qui in poi nessuna connessione al database è occupata

    ticket_id = _public_id(number)
    if files:
        try:
            await asyncio.to_thread(
                email_utils.send_ticket_created_to_staff,
                staff, os.environ.get("GMAIL_ADDRESS"), ticket_id, payload.subject,
                CATEGORY_LABELS[payload.category], current_user["username"], current_user["email"],
                payload.description, payload.extra, attachments=files,
            )
        except Exception as e: #qualunque errore: i file non sono arrivati, il ticket non deve restare
            log.warning("Ticket %s con allegati non inviato allo staff: %r", ticket_id, e)
            #I messaggi del ticket se ne vanno con lui (ON DELETE CASCADE)
            async with pool.acquire() as conn:
                await conn.execute("DELETE FROM tickets WHERE id = $1", number)
            raise HTTPException(status_code=503, detail=i18n.t("attachments_not_sent", lang))
    elif staff:
        await _send_quietly(
            email_utils.send_ticket_created_to_staff,
            staff, os.environ.get("GMAIL_ADDRESS"), ticket_id, payload.subject,
            CATEGORY_LABELS[payload.category], current_user["username"], current_user["email"],
            payload.description, payload.extra,
        )
    else:
        log.warning("SUPPORT_STAFF non impostata: nessuna notifica per il nuovo ticket %s", ticket_id)
    await _send_quietly(
        email_utils.send_ticket_received_to_user,
        current_user["email"], ticket_id, payload.subject,
        ticket_mail.site_ticket_url(number, current_user["language"]),
        _RECEIVED_WHAT.get(payload.category, "what_support_request"), current_user["language"],
    )
    return detail


@router.get("", response_model=TicketListResponse)
async def list_tickets(current_user: dict = Depends(get_current_user)):
    """I ticket dell'utente, dal più recentemente aggiornato."""
    await ticket_mail.sync_if_due() #Porta dentro eventuali risposte appena arrivate via email
    pool = database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, subject, category, status, created_at, updated_at
            FROM tickets WHERE user_id = $1
            ORDER BY updated_at DESC, id DESC
            """,
            current_user["id"],
        )
    return TicketListResponse(tickets=[_summary(r) for r in rows])


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: str, current_user: dict = Depends(get_current_user)):
    number = _parse_public_id(ticket_id, current_user["lang"])
    await ticket_mail.sync_if_due()
    pool = database.get_pool()
    async with pool.acquire() as conn:
        return await _load_detail(conn, number, current_user["id"], current_user["lang"])


@router.post("/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201)
async def reply_to_ticket(ticket_id: str, payload: TicketReplyRequest,
                          current_user: dict = Depends(get_current_user)):
    """Risposta dell'utente. Riapre il ticket se era in attesa o risolto."""
    lang = current_user["lang"]
    number = _parse_public_id(ticket_id, lang)
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            ticket = await conn.fetchrow(
                "SELECT id, subject, status FROM tickets WHERE id = $1 AND user_id = $2 FOR UPDATE",
                number, current_user["id"],
            )
            if ticket is None:
                raise _ticket_not_found(lang)
            if ticket["status"] == "closed":
                raise HTTPException(status_code=409, detail=i18n.t("ticket_closed", lang))
            #Contate nel database e non in memoria: il limite vale anche dopo un riavvio
            recent_replies = await conn.fetchval(
                """
                SELECT count(*) FROM ticket_messages m JOIN tickets t ON t.id = m.ticket_id
                WHERE t.user_id = $1 AND m.author_role = 'user'
                  AND m.created_at > now() - interval '1 hour'
                """,
                current_user["id"],
            )
            if recent_replies >= _MAX_REPLIES_PER_HOUR:
                raise HTTPException(
                    status_code=429,
                    detail=i18n.t("too_many_replies", lang),
                )

            message = await conn.fetchrow(
                """
                INSERT INTO ticket_messages (ticket_id, author_role, author_name, body)
                VALUES ($1, 'user', $2, $3)
                RETURNING id, author_role, author_name, body, created_at
                """,
                number, current_user["username"], payload.body,
            )
            #"In lavorazione" resta tale: il team ci sta già lavorando. Negli altri casi
            #la palla torna al team.
            new_status = "progress" if ticket["status"] == "progress" else "open"
            await conn.execute(
                "UPDATE tickets SET status = $1, updated_at = now() WHERE id = $2", new_status, number,
            )

    staff = _staff_recipients()
    if staff:
        await _send_quietly(
            email_utils.send_ticket_user_reply_to_staff,
            staff, os.environ.get("GMAIL_ADDRESS"), _public_id(number), ticket["subject"],
            current_user["username"], payload.body,
        )
    return TicketMessageOut(**dict(message))
