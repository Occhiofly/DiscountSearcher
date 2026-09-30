"""
Invio email lato server, tramite SMTP di Gmail.

Stessa identica logica del vecchio email_utils.py dell'app desktop, con
un'unica differenza: le credenziali arrivano da variabili d'ambiente (.env)
invece che da un file email_config.py, perché qui non c'è nessun eseguibile
da distribuire — le credenziali vivono solo su questo server.
"""
import smtplib
import os

import i18n
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587

class EmailSendError(Exception):
    """Sollevata quando l'invio di un'email fallisce, per qualsiasi motivo."""
    pass

#Intestazione aggiunta alle notifiche dei ticket inviate allo staff. Serve a ticket_mail.py
#per riconoscerle quando lo staff è l'account del server stesso: in quel caso le notifiche
#finiscono nella sua "Posta inviata" insieme alle risposte, e non vanno scambiate per risposte.
NOTIFICATION_HEADER = "X-DS-Notification"

def _send_email(to_email, subject, body, reply_to=None, headers=None, attachments=None):
    """
    to_email può essere un indirizzo o una lista di indirizzi (es. tutto lo staff).
    reply_to: dove finisce la risposta se il destinatario preme "Rispondi".
    headers: intestazioni aggiuntive, es. {NOTIFICATION_HEADER: "ticket"}.
    attachments: file da allegare (attachments.Attachment), già controllati.
    """
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_app_password:
        raise EmailSendError("Credenziali email non configurate: controlla il file .env")

    recipients = [to_email] if isinstance(to_email, str) else list(to_email)
    if not recipients:
        raise EmailSendError("Nessun destinatario")

    message = MIMEMultipart()
    message["From"] = gmail_address
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    for name, value in (headers or {}).items():
        message[name] = value
    message.attach(MIMEText(body, "plain", "utf-8"))
    for item in attachments or []:
        part = MIMEApplication(item.data, _subtype=item.content_type.split("/", 1)[1])
        part.replace_header("Content-Type", item.content_type)
        #Forma (charset, lingua, nome): i nomi con lettere accentate restano leggibili
        part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", item.name))
        message.attach(part)

    #Il timeout vale per l'intero invio del messaggio: con qualche MB di allegati
    #10 secondi potrebbero non bastare.
    timeout = 60 if attachments else 10
    try:
        #Costruita prima di collegarsi: se il contenuto non è valido (per esempio
        #un'intestazione con un "a capo", che Python rifiuta) non serve aprire la connessione
        raw = message.as_string()
    except Exception as e:
        raise EmailSendError(f"Email non valida: {e}")
    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=timeout) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_password)
            server.sendmail(gmail_address, recipients, raw)
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError("Credenziali Gmail non valide: controlla il file .env")
    except (smtplib.SMTPException, OSError) as e:
        raise EmailSendError(f"Errore durante l'invio dell'email: {e}")

def send_verification_email(to_email, code, lang=i18n.DEFAULT_LANG):
    _send_email(to_email, i18n.t("mail_verify_subject", lang), i18n.t("mail_verify_body", lang, code=code))

def send_site_login_code(to_email, code, minutes, lang=i18n.DEFAULT_LANG):
    """Codice per entrare nel sito (site_login.py): il secondo passaggio dopo la password."""
    _send_email(to_email, i18n.t("mail_site_code_subject", lang),
                i18n.t("mail_site_code_body", lang, code=code, minutes=minutes))

def send_email_change_code(to_email, code, new_email, which, minutes, lang=i18n.DEFAULT_LANG):
    """
    Uno dei due codici per cambiare l'email (email_change.py). which="old": va
    all'indirizzo attuale e lo avvisa del cambio richiesto; which="new": va al nuovo.
    """
    body_key = "mail_email_change_old_body" if which == "old" else "mail_email_change_new_body"
    _send_email(to_email, i18n.t("mail_email_change_subject", lang),
                i18n.t(body_key, lang, code=code, new_email=new_email, minutes=minutes))

def send_profile_update_notification(to_email, changed_fields, changed_at, lang=i18n.DEFAULT_LANG):
    """
    Notifica di sicurezza quando Username, Email o Password vengono modificati
    dal Profilo. Va inviata all'email GIÀ registrata PRIMA della modifica
    (il chiamante deve passare quella vecchia, non quella nuova).
    """
    #I nomi dei campi cambiati ("username", "email", "password") vanno tradotti anche loro
    changes_text = ", ".join(i18n.t(f"field_{name}", lang) for name in changed_fields)
    extra_note = i18n.t("mail_profile_extra_password", lang) if "password" in changed_fields else ""
    _send_email(to_email, i18n.t("mail_profile_subject", lang),
                i18n.t("mail_profile_body", lang, changed_at=changed_at,
                       changes=changes_text, extra=extra_note))

def send_password_reset_email(to_email, code, lang=i18n.DEFAULT_LANG):
    """Codice per la procedura "Password dimenticata"."""
    _send_email(to_email, i18n.t("mail_reset_subject", lang), i18n.t("mail_reset_body", lang, code=code))

def send_password_reset_confirmation(to_email, lang=i18n.DEFAULT_LANG):
    """
    Notifica di sicurezza inviata DOPO che la password è stata reimpostata con
    successo tramite "Password dimenticata" — un evento più delicato di un
    normale cambio dal Profilo, perché l'utente non era autenticato quando è successo.
    """
    _send_email(to_email, i18n.t("mail_reset_done_subject", lang), i18n.t("mail_reset_done_body", lang))

#--- Ticket di assistenza ---------------------------------------------------
#Regola importante: SOLO le email destinate allo staff hanno il codice del ticket fra
#parentesi quadre nell'oggetto ("[DS-1001]"). È quel marcatore che ticket_mail.py cerca
#nella casella per riconoscere le risposte dello staff; le email per gli utenti usano
#"DS-1001" senza parentesi, così un'eventuale risposta di un utente non viene scambiata
#per una risposta del team.

_STAFF_INSTRUCTIONS = (
    "----------------------------------------------------------------\n"
    "COME RISPONDERE\n"
    "Rispondi a questa email scrivendo SOPRA il testo citato: la tua risposta\n"
    "comparirà nel ticket sul sito e l'utente riceverà un avviso via email.\n\n"
    "Per cambiare lo stato, scrivi come PRIMA riga della risposta uno di questi:\n"
    "  #inlavorazione   il team ci sta lavorando\n"
    "  #risolto         la richiesta è risolta (l'utente può ancora rispondere)\n"
    "  #chiuso          ticket chiuso, niente più risposte\n"
    "Senza parola chiave, il ticket passa a \"In attesa di risposta\" dell'utente.\n"
    "Una email con solo la parola chiave cambia lo stato senza aggiungere messaggi.\n"
    "----------------------------------------------------------------"
)

def _staff_site_line(ticket_id):
    """Link alla pagina del ticket nell'area staff del sito (staff.py), in alternativa all'email."""
    base = os.environ.get("SITE_URL", "https://discountsearcher.it").rstrip("/")
    return f"Puoi leggerlo e rispondere anche dal sito, nell'area staff:\n{base}/staff?id={ticket_id}\n\n"

def send_ticket_created_to_staff(staff_emails, reply_to, ticket_id, subject, category_label,
                                 username, user_email, description, extra, attachments=None):
    attachment_list = "".join(f"  - {a.name} ({a.size_label})\n" for a in attachments or [])
    body = (
        f"Nuovo ticket {ticket_id}\n\n"
        f"Oggetto:   {subject}\n"
        f"Categoria: {category_label}\n"
        f"Utente:    {username} <{user_email}>\n\n"
        f"Descrizione:\n{description}\n"
        + (f"\nInformazioni aggiuntive:\n{extra}\n" if extra else "")
        + (f"\nFile allegati a questa email (inviati dall'utente: aprili con prudenza):\n{attachment_list}"
           if attachments else "")
        + "\n" + _staff_site_line(ticket_id) + _STAFF_INSTRUCTIONS
    )
    _send_email(staff_emails, f"[{ticket_id}] {subject}", body, reply_to=reply_to,
                headers={NOTIFICATION_HEADER: "ticket"}, attachments=attachments)

def send_ticket_user_reply_to_staff(staff_emails, reply_to, ticket_id, subject, username, message):
    body = (
        f"{username} ha risposto al ticket {ticket_id}.\n\n"
        f"Messaggio:\n{message}\n\n"
        + _staff_site_line(ticket_id) + _STAFF_INSTRUCTIONS
    )
    _send_email(staff_emails, f"[{ticket_id}] Nuova risposta: {subject}", body, reply_to=reply_to,
                headers={NOTIFICATION_HEADER: "ticket"})

def send_ticket_received_to_user(to_email, ticket_id, subject, ticket_url,
                                 what_key="what_support_request", lang=i18n.DEFAULT_LANG):
    #`what_key` cambia come chiamiamo il ticket: dalla pagina "Lavora con noi" arriva
    #una candidatura, e chiamarla "richiesta di assistenza" sarebbe sbagliato.
    body = i18n.t("mail_ticket_received_body", lang, what=i18n.t(what_key, lang),
                  subject=subject, ticket_id=ticket_id, url=ticket_url)
    _send_email(to_email, i18n.t("mail_ticket_received_subject", lang, ticket_id=ticket_id), body)

def send_ticket_staff_reply_to_user(to_email, ticket_id, subject, staff_name, message,
                                    status_key, ticket_url, lang=i18n.DEFAULT_LANG):
    reply_text = i18n.t("mail_ticket_update_reply", lang, staff_name=staff_name, message=message) if message else ""
    body = i18n.t("mail_ticket_update_body", lang, ticket_id=ticket_id, subject=subject,
                  reply=reply_text, status=i18n.t(status_key, lang), url=ticket_url)
    _send_email(to_email, i18n.t("mail_ticket_update_subject", lang, ticket_id=ticket_id), body)
