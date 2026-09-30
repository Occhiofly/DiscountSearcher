"""
Modelli Pydantic: definiscono la forma esatta delle richieste che l'API
accetta e delle risposte che restituisce. FastAPI li usa per validare
automaticamente ogni richiesta PRIMA che arrivi al codice dell'endpoint —
se manca un campo, o l'email non è valida, il chiamante riceve subito un
errore 422 chiaro, senza che scriviamo noi quei controlli a mano.
"""
import re
from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, Field, StringConstraints, field_validator

import attachments as attachment_rules #alias: "attachments" è anche il nome di un campo

#--- Limiti comuni --------------------------------------------------------------
#Ogni testo ha una lunghezza massima. Senza, una richiesta potrebbe contenere
#stringhe di molti MB: finirebbero in memoria (il blocco dei tentativi di login
#ricorda gli username provati) o nel database (la cronologia), riempiendoli.
#I limiti sono larghi rispetto all'uso normale: nessun utente reale li sfiora.
_Username = Annotated[str, StringConstraints(max_length=64)]
_Password = Annotated[str, StringConstraints(max_length=256)]
_Email = Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
_Code = Annotated[str, StringConstraints(max_length=12)]

_MIN_PASSWORD_LENGTH = 8
#Un indirizzo Gmail completo, dall'inizio alla fine: "x@gmail.com.altro.it" non passa
_GMAIL_ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.IGNORECASE)

#I validatori sollevano una CHIAVE, non una frase: il messaggio vero, nella lingua
#della richiesta, lo compone il gestore degli errori in main.py (vedi i18n.py).
def _check_gmail(value):
    if not _GMAIL_ADDRESS.fullmatch(value):
        raise ValueError("invalid_gmail")
    return value

def _check_new_password(value):
    """Solo per le password NUOVE: chi ha già un account accede con quella che ha."""
    if len(value) < _MIN_PASSWORD_LENGTH:
        raise ValueError("invalid_password_short")
    return value

class RegisterRequest(BaseModel):
    username: _Username
    password: _Password
    email: _Email
    birth_date: date

    @field_validator("email")
    @classmethod
    def email_must_be_gmail(cls, v):
        return _check_gmail(v)

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("invalid_username_empty")
        return v

    @field_validator("password")
    @classmethod
    def password_long_enough(cls, v):
        return _check_new_password(v)

class RegisterResponse(BaseModel):
    message: str
    #False se l'account è stato creato ma l'email con il codice non è partita: chi si
    #registra dal sito lo vede scritto, invece di aspettare un'email che non arriverà.
    email_sent: bool = True

class VerifyEmailRequest(BaseModel):
    username: _Username
    code: _Code

class MessageResponse(BaseModel):
    message: str

class ResendCodeRequest(BaseModel):
    username: _Username

class ResendCodeResponse(BaseModel):
    message: str
    email_sent: bool

class LoginRequest(BaseModel):
    username: _Username
    password: _Password
    device_info: str | None = None #Facoltativo, es. "Windows - PC di casa"

    @field_validator("device_info")
    @classmethod
    def device_info_short(cls, v):
        #Tagliato invece che rifiutato: è solo un'etichetta, meglio non bloccare un login
        return v[:100] if v else v

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class MeResponse(BaseModel):
    id: int
    username: str
    email: str

class SessionInfo(BaseModel):
    id: UUID
    device_info: str | None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool

class SessionListResponse(BaseModel):
    sessions: list[SessionInfo]

class ForgotPasswordRequest(BaseModel):
    username: _Username

class ResetPasswordRequest(BaseModel):
    username: _Username
    code: _Code
    new_password: _Password

    @field_validator("new_password")
    @classmethod
    def password_long_enough(cls, v):
        return _check_new_password(v)

class UpdateProfileRequest(BaseModel):
    username: _Username
    email: _Email
    password: _Password | None = None #Nuova password, facoltativa
    current_password: _Password #Richiesta per confermare l'identità, come nell'app desktop

    @field_validator("email")
    @classmethod
    def email_must_be_gmail(cls, v):
        return _check_gmail(v)

    @field_validator("password")
    @classmethod
    def password_long_enough(cls, v):
        return v if v is None else _check_new_password(v)

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("invalid_username_empty")
        return v

class AddHistoryRequest(BaseModel):
    title: str
    deal_id: Annotated[str, StringConstraints(max_length=200)]

    @field_validator("title")
    @classmethod
    def title_short(cls, v):
        #Tagliato invece che rifiutato: un titolo lunghissimo non deve far perdere la voce
        return v[:300]

class HistoryEntry(BaseModel):
    id: int
    title: str
    deal_id: str
    viewed_at: datetime

class HistoryListResponse(BaseModel):
    history: list[HistoryEntry]

#--- Ticket di assistenza ---------------------------------------------------
#Le categorie sono le stesse del Centro assistenza del sito (web/assets/js/data/support.js):
#aggiungendone una lì, va aggiunta anche qui, altrimenti il server la rifiuta con un 422.
#"candidatura" non viene dall'assistenza: è il ticket aperto da "Lavora con noi"
#(web/assets/js/data/jobs.js), che usa lo stesso sistema con un modulo diverso.
TicketCategory = Literal[
    "account", "accesso", "recupero-password", "verifica-email", "applicazione",
    "offerte", "filtri", "cronologia", "bug", "altro", "candidatura",
]
#open = attende il team · progress = il team ci sta lavorando · waiting = il team ha
#risposto e attende l'utente · resolved = risolto · closed = chiuso, niente più risposte
TicketStatus = Literal["open", "progress", "waiting", "resolved", "closed"]

#strip_whitespace: gli spazi all'inizio e alla fine non contano per le lunghezze minime,
#così un oggetto fatto di soli spazi viene rifiutato. Stessi limiti del modulo sul sito.
_Subject = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=120)]
_Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=30, max_length=3000)]
_Extra = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]
_ReplyBody = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3000)]

#File allegato a un ticket (assistenza o candidatura), in base64 dentro il JSON (niente upload separato:
#stesso endpoint, stessa validazione). I controlli veri sul contenuto sono in
#attachments.py; qui solo i limiti di forma, così un file enorme viene respinto
#subito. Il tipo dichiarato viene comunque verificato sui primi byte del file.
class TicketAttachment(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content_type: Literal[tuple(attachment_rules.ALLOWED_TYPES)]
    data: Annotated[str, StringConstraints(max_length=attachment_rules.MAX_BASE64_CHARS)]

class TicketCreateRequest(BaseModel):
    subject: _Subject
    category: TicketCategory
    description: _Description
    extra: _Extra | None = None

    @field_validator("subject")
    @classmethod
    def subject_single_line(cls, v):
        #L'oggetto finisce nell'intestazione "Subject" dell'email allo staff: un "a capo"
        #lì dentro permetterebbe di aggiungere intestazioni (es. "Bcc: altro@indirizzo")
        #o farebbe fallire l'invio. Un oggetto è sempre una riga sola.
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in v):
            raise ValueError("invalid_subject_multiline")
        return v
    #Facoltativi: vedi create_ticket in tickets.py e attachments.py
    attachments: Annotated[list[TicketAttachment], Field(max_length=attachment_rules.MAX_FILES)] = []

class TicketReplyRequest(BaseModel):
    body: _ReplyBody

class TicketMessageOut(BaseModel):
    id: int
    author_role: Literal["user", "staff"]
    author_name: str
    body: str
    created_at: datetime

class TicketSummary(BaseModel):
    id: str #Identificativo pubblico, es. "DS-1001"
    subject: str
    category: TicketCategory
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

class TicketListResponse(BaseModel):
    tickets: list[TicketSummary]

class TicketDetail(TicketSummary):
    extra: str | None
    messages: list[TicketMessageOut]

#--- Cambio email con due codici (email_change.py) ------------------------------
class ProfileUpdateResponse(BaseModel):
    message: str
    #Se l'email è stata cambiata: il cambio aspetta i due codici (POST /me/email/confirm)
    email_pending: bool = False
    old_email_hint: str | None = None
    new_email_hint: str | None = None
    email_sent: bool | None = None

_Code6 = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{6}$")]

class EmailChangeConfirmRequest(BaseModel):
    old_code: _Code6 #arrivato all'indirizzo attuale
    new_code: _Code6 #arrivato al nuovo indirizzo

#--- Accesso al sito con codice via email (site_login.py) ----------------------------
class SiteLoginChallenge(BaseModel):
    challenge: str   #identificativo della richiesta, da rimandare con il codice
    email_hint: str  #indirizzo in parte nascosto, es. "ma•••@gmail.com"
    email_sent: bool
    minutes: int     #validità del codice

class SiteLoginVerifyRequest(BaseModel):
    challenge: Annotated[str, StringConstraints(min_length=10, max_length=64)]
    code: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{6}$")]

class SiteLoginResendRequest(BaseModel):
    challenge: Annotated[str, StringConstraints(min_length=10, max_length=64)]

class SiteLoginResend(BaseModel):
    email_sent: bool

#--- Area staff (staff.py) ----------------------------------------------------
#Le risposte del team possono essere più lunghe di quelle degli utenti: stesso tetto
#delle risposte via email (ticket_mail._MAX_BODY) e del database.
_StaffBody = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]

class StaffMeResponse(BaseModel):
    name: str #Come compaiono nel ticket le risposte di questo membro dello staff

class StaffTicketSummary(TicketSummary):
    username: str
    email: str

class StaffTicketListResponse(BaseModel):
    tickets: list[StaffTicketSummary]

class StaffTicketDetail(StaffTicketSummary):
    extra: str | None
    messages: list[TicketMessageOut]

class StaffReplyRequest(BaseModel):
    body: _StaffBody
    #Stato dopo la risposta; se manca, "waiting" (tocca all'utente), come via email
    status: TicketStatus | None = None

class StaffStatusRequest(BaseModel):
    status: TicketStatus
