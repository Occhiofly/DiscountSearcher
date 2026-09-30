"""
Area staff del sito: il team vede TUTTI i ticket, risponde e cambia lo stato
dal sito, in alternativa alle risposte via email (ticket_mail.py), che
continuano a funzionare come prima.

Chi fa parte dello staff si decide dalle variabili d'ambiente di Render:
    STAFF_ACCOUNTS=12:Marco, 15:Vittorio
cioè il NUMERO dell'account (colonna id della tabella users) e, dopo i due
punti, il nome con cui le risposte compaiono nel ticket. Il nome è facoltativo:
senza, si usa il nome utente dell'account.

Perché il numero e non l'email o il nome utente: dal profilo (PATCH /me) si
possono cambiare email e nome utente, e l'email nuova non viene verificata di
nuovo. Riconoscere lo staff dall'email permetterebbe a chiunque di scriversi
l'indirizzo del team e diventare staff. Il numero dell'account non cambia mai.

Per trovare il numero di un account, nel SQL Editor di Supabase:
    SELECT id, username FROM users WHERE username = 'nome_utente';

Per chi non è staff questi endpoint rispondono 404, come se non esistessero.
"""
import asyncio
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query

import database
import email_utils
import i18n
import ticket_mail
from site_login import get_site_user
from tickets import _parse_public_id
from models import (
    StaffMeResponse, StaffReplyRequest, StaffStatusRequest, StaffTicketDetail,
    StaffTicketListResponse, StaffTicketSummary, TicketMessageOut, TicketStatus,
)

log = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/staff", tags=["staff"])

#Quanti ticket al massimo in un elenco: abbastanza per anni di assistenza di un
#progetto piccolo, e un tetto evita risposte enormi.
_MAX_LIST = 500


def staff_accounts():
    """{numero account: nome mostrato o None} da STAFF_ACCOUNTS. Voci non valide ignorate."""
    accounts = {}
    for item in os.environ.get("STAFF_ACCOUNTS", "").split(","):
        number, _, name = item.strip().partition(":")
        if number.strip().isdigit():
            accounts[int(number)] = name.strip()[:60] or None
    return accounts


def _not_found():
    #Identica alla risposta di FastAPI per un indirizzo che non esiste
    return HTTPException(status_code=404, detail="Not Found")


async def get_staff_user(current_user: dict = Depends(get_site_user)):
    """Come get_site_user (sessione del sito con codice), ma solo per lo staff; agli altri 404."""
    accounts = staff_accounts()
    if current_user["id"] not in accounts:
        raise _not_found()
    return {**current_user, "staff_name": accounts[current_user["id"]] or current_user["username"]}


def _public_id(number):
    return f"DS-{number}"


def _summary(row):
    return StaffTicketSummary(
        id=_public_id(row["id"]), subject=row["subject"], category=row["category"],
        status=row["status"], created_at=row["created_at"], updated_at=row["updated_at"],
        username=row["username"], email=row["email"],
    )


def _parse_id(value, lang):
    #Stesso formato dei ticket dell'utente: "DS-1001"
    return _parse_public_id(value, lang)


async def _load(conn, number, lang):
    ticket = await conn.fetchrow(
        """
        SELECT t.id, t.subject, t.category, t.extra, t.status, t.created_at, t.updated_at,
               u.username, u.email, u.language
        FROM tickets t JOIN users u ON u.id = t.user_id
        WHERE t.id = $1
        """,
        number,
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail=i18n.t("ticket_not_found", lang))
    messages = await conn.fetch(
        """
        SELECT id, author_role, author_name, body, created_at
        FROM ticket_messages WHERE ticket_id = $1
        ORDER BY created_at, id
        """,
        number,
    )
    return ticket, StaffTicketDetail(
        **_summary(ticket).model_dump(),
        extra=ticket["extra"],
        messages=[TicketMessageOut(**dict(m)) for m in messages],
    )


async def _notify_user(ticket, staff_name, body, status):
    """Stessa email che parte quando il team risponde via email (ticket_mail.py)."""
    try:
        await asyncio.to_thread(
            email_utils.send_ticket_staff_reply_to_user,
            ticket["email"], _public_id(ticket["id"]), ticket["subject"], staff_name, body,
            ticket_mail.STATUS_KEYS[status],
            ticket_mail.site_ticket_url(ticket["id"], ticket["language"]), ticket["language"],
        )
    except email_utils.EmailSendError as e:
        #La risposta è comunque salvata e visibile sul sito
        log.warning("Avviso all'utente per DS-%s non inviato: %s", ticket["id"], e)


@router.get("/me", response_model=StaffMeResponse)
async def staff_me(staff: dict = Depends(get_staff_user)):
    """200 con il nome mostrato nelle risposte se l'account è staff, altrimenti 404."""
    return StaffMeResponse(name=staff["staff_name"])


@router.get("/tickets", response_model=StaffTicketListResponse)
async def staff_list(status: TicketStatus | None = Query(None), staff: dict = Depends(get_staff_user)):
    """Tutti i ticket (di tutti gli utenti), dal più recentemente aggiornato."""
    await ticket_mail.sync_if_due() #Porta dentro le risposte arrivate via email
    pool = database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT t.id, t.subject, t.category, t.status, t.created_at, t.updated_at,
                   u.username, u.email
            FROM tickets t JOIN users u ON u.id = t.user_id
            WHERE $1::text IS NULL OR t.status = $1
            ORDER BY t.updated_at DESC, t.id DESC
            LIMIT $2
            """,
            status, _MAX_LIST,
        )
    return StaffTicketListResponse(tickets=[_summary(r) for r in rows])


@router.get("/tickets/{ticket_id}", response_model=StaffTicketDetail)
async def staff_get(ticket_id: str, staff: dict = Depends(get_staff_user)):
    number = _parse_id(ticket_id, staff["lang"])
    await ticket_mail.sync_if_due()
    pool = database.get_pool()
    async with pool.acquire() as conn:
        _, detail = await _load(conn, number, staff["lang"])
    return detail


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201)
async def staff_reply(ticket_id: str, payload: StaffReplyRequest, staff: dict = Depends(get_staff_user)):
    """
    Risposta del team dal sito. Come via email: senza uno stato scelto il ticket
    passa a "In attesa di risposta" dell'utente, che riceve l'avviso via email.
    """
    number = _parse_id(ticket_id, staff["lang"])
    new_status = payload.status or "waiting"
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            ticket, _ = await _load(conn, number, staff["lang"])
            #Blocca il ticket fino alla fine: due risposte contemporanee non si pestano
            await conn.execute("SELECT 1 FROM tickets WHERE id = $1 FOR UPDATE", number)
            message = await conn.fetchrow(
                """
                INSERT INTO ticket_messages (ticket_id, author_role, author_name, body)
                VALUES ($1, 'staff', $2, $3)
                RETURNING id, author_role, author_name, body, created_at
                """,
                number, staff["staff_name"], payload.body,
            )
            await conn.execute(
                "UPDATE tickets SET status = $1, updated_at = now() WHERE id = $2", new_status, number,
            )
    log.info("DS-%s: risposta dal sito di %s (account %s)", number, staff["staff_name"], staff["id"])
    await _notify_user(ticket, staff["staff_name"], payload.body, new_status)
    return TicketMessageOut(**dict(message))


@router.patch("/tickets/{ticket_id}", response_model=StaffTicketSummary)
async def staff_set_status(ticket_id: str, payload: StaffStatusRequest,
                           staff: dict = Depends(get_staff_user)):
    """Cambia solo lo stato, come un'email con la sola parola chiave. L'utente riceve l'avviso."""
    number = _parse_id(ticket_id, staff["lang"])
    pool = database.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            ticket, _ = await _load(conn, number, staff["lang"])
            if ticket["status"] == payload.status:
                return _summary(ticket)
            await conn.execute(
                "UPDATE tickets SET status = $1, updated_at = now() WHERE id = $2", payload.status, number,
            )
        ticket, _ = await _load(conn, number, staff["lang"])
    log.info("DS-%s: stato %s dal sito, account %s", number, payload.status, staff["id"])
    await _notify_user(ticket, staff["staff_name"], "", payload.status)
    return _summary(ticket)
