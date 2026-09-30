"""
Testi del server in italiano e in inglese.

Due usi diversi:
  - risposte immediate (errori e conferme): la lingua arriva dall'intestazione
    Accept-Language della richiesta, cioè dalla lingua del sito o dell'app che
    sta chiamando;
  - email: la lingua è quella salvata nell'account (colonna `language` della
    tabella users, vedi language_schema.sql), perché l'email parte anche molto
    dopo la richiesta, o per iniziativa dello staff.

Le email allo staff restano in italiano: le legge il team, non gli utenti.

Per aggiungere un testo: una voce in MESSAGES con entrambe le lingue. I
segnaposto {cosi} vengono riempiti con t("chiave", lang, cosi="valore").
"""

DEFAULT_LANG = "it"
SUPPORTED = ("it", "en")


def normalize(lang):
    """Riporta qualsiasi valore a una lingua supportata ("it" se non riconosciuta)."""
    if not lang:
        return DEFAULT_LANG
    short = str(lang).strip().lower().replace("_", "-").split("-")[0]
    return short if short in SUPPORTED else DEFAULT_LANG


def from_accept_language(header):
    """
    Lingua preferita dall'intestazione Accept-Language, es. "en-GB,en;q=0.9,it;q=0.8".
    Si prende la prima lingua supportata in ordine di preferenza; se non ce n'è
    nessuna, l'italiano.
    """
    if not header:
        return DEFAULT_LANG
    entries = []
    #Un'intestazione con centinaia di voci non aiuta nessuno: ne bastano poche.
    for part in str(header).split(",")[:20]:
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        quality = 1.0
        if "q=" in params:
            try:
                quality = float(params.split("q=", 1)[1])
            except ValueError:
                quality = 0.0
            #float() accetta anche "nan" e "inf": riportiamo il valore nell'intervallo
            #previsto (0-1), altrimenti l'ordinamento diventa imprevedibile.
            if not 0.0 <= quality <= 1.0:
                quality = 0.0
        entries.append((quality, tag.strip().lower()))
    for _, tag in sorted(entries, key=lambda e: e[0], reverse=True):
        short = tag.replace("_", "-").split("-")[0]
        if short in SUPPORTED:
            return short
    return DEFAULT_LANG


def t(key, lang=DEFAULT_LANG, **values):
    """Testo tradotto. Con **values riempie i segnaposto {nome}."""
    text = MESSAGES[key][normalize(lang)]
    return text.format(**values) if values else text


#Nome leggibile dei campi, usato nei messaggi di dati non validi
FIELD_LABELS = {
    "username": {"it": "Username", "en": "Username"},
    "password": {"it": "Password", "en": "Password"},
    "new_password": {"it": "Password", "en": "Password"},
    "current_password": {"it": "Password attuale", "en": "Current password"},
    "email": {"it": "Email", "en": "Email"},
    "code": {"it": "Codice", "en": "Code"},
    "birth_date": {"it": "Data di nascita", "en": "Date of birth"},
    "subject": {"it": "Oggetto", "en": "Subject"},
    "description": {"it": "Descrizione", "en": "Description"},
    "extra": {"it": "Informazioni aggiuntive", "en": "Additional information"},
    "body": {"it": "Messaggio", "en": "Message"},
    "title": {"it": "Titolo", "en": "Title"},
    "deal_id": {"it": "Offerta", "en": "Deal"},
    "attachments": {"it": "Allegati", "en": "Attachments"},
}


def field_label(name, lang=DEFAULT_LANG):
    entry = FIELD_LABELS.get(name)
    if entry:
        return entry[normalize(lang)]
    return "Un campo" if normalize(lang) == "it" else "A field"


MESSAGES = {
    # --- Account: errori ---------------------------------------------------
    "user_not_found": {
        "it": "Utente non trovato",
        "en": "User not found",
    },
    "username_taken": {
        "it": "Username già in uso",
        "en": "Username already taken",
    },
    "bad_credentials": {
        "it": "Username o password errati",
        "en": "Wrong username or password",
    },
    "email_not_verified": {
        "it": "Email non ancora verificata. Usa /resend-code per riceverne uno nuovo.",
        "en": "Email not verified yet. Use /resend-code to get a new code.",
    },
    "wrong_current_password": {
        "it": "Password attuale errata",
        "en": "Wrong current password",
    },
    "site_login_required": {
        "it": "Per sicurezza accedi di nuovo dal sito: ti mandiamo un codice via email.",
        "en": "For your security, please sign in again on the site: we will email you a code.",
    },
    "site_code_wrong": {
        "it": "Codice non corretto. Tentativi rimasti: {left}.",
        "en": "Incorrect code. Attempts left: {left}.",
    },
    "site_code_too_many": {
        "it": "Troppi codici sbagliati: accedi di nuovo con la password.",
        "en": "Too many wrong codes: please sign in again with your password.",
    },
    "site_code_expired": {
        "it": "Il codice è scaduto: accedi di nuovo con la password.",
        "en": "The code has expired: please sign in again with your password.",
    },
    "mail_site_code_subject": {
        "it": "Discount Searcher - Codice di accesso al sito",
        "en": "Discount Searcher - Site sign-in code",
    },
    "mail_site_code_body": {
        "it": "Gentile utente,\n\n"
              "qualcuno ha inserito la password giusta del tuo account per accedere al sito "
              "di Discount Searcher. Per entrare, inserisci questo codice nella pagina di accesso:\n\n"
              "    {code}\n\n"
              "Il codice è valido per {minutes} minuti.\n\n"
              "Se non sei stato tu, non inserire il codice e cambia subito la password "
              "dal Profilo dell'app: chi ha provato ad accedere conosce la tua password attuale.\n\n"
              "Cordiali saluti,\nIl team di Discount Searcher",
        "en": "Hello,\n\n"
              "someone entered the correct password of your account to sign in to the "
              "Discount Searcher website. To sign in, enter this code on the sign-in page:\n\n"
              "    {code}\n\n"
              "The code is valid for {minutes} minutes.\n\n"
              "If this was not you, do not enter the code and change your password right away "
              "from the app's Profile: whoever tried to sign in knows your current password.\n\n"
              "Kind regards,\nThe Discount Searcher team",
    },
    "session_lost": {
        "it": "La sessione è scaduta o non è più valida: accedi di nuovo.",
        "en": "Your session has expired or is no longer valid: please sign in again.",
    },
    #Modalità manutenzione (maintenance.py): mostrato da sito e app
    "maintenance": {
        "it": "Il team sta aggiornando Discount Searcher. L'aggiornamento può richiedere "
              "qualche ora o qualche giorno: tutto riprenderà a funzionare appena sarà "
              "finito. Grazie per la pazienza.",
        "en": "The team is updating Discount Searcher. The update may take a few hours or a "
              "few days: everything will work again as soon as it is finished. Thank you for "
              "your patience.",
    },
    "session_not_found": {
        "it": "Sessione non trovata",
        "en": "Session not found",
    },
    "no_pending_code": {
        "it": "Non c'è nessun codice in attesa di verifica per questo account",
        "en": "There is no verification code pending for this account",
    },
    "code_expired": {
        "it": "Il codice è scaduto, richiedine uno nuovo",
        "en": "The code has expired, request a new one",
    },
    "code_wrong": {
        "it": "Codice errato",
        "en": "Wrong code",
    },
    "reset_code_invalid": {
        "it": "Codice non valido o scaduto",
        "en": "Invalid or expired code",
    },
    "already_verified": {
        "it": "L'account è già verificato: puoi accedere.",
        "en": "This account is already verified: you can sign in.",
    },
    "too_many_attempts": {
        "it": "Troppi tentativi falliti. Riprova tra circa {minutes} minuti.",
        "en": "Too many failed attempts. Try again in about {minutes} minutes.",
    },
    "too_many_codes": {
        "it": "Troppi codici sbagliati. Riprova tra circa {minutes} minuti.",
        "en": "Too many wrong codes. Try again in about {minutes} minutes.",
    },
    "too_many_emails": {
        "it": "Hai già richiesto un codice da poco: riprova tra circa {minutes} {minute_word}. "
              "Controlla anche lo spam.",
        "en": "You requested a code a moment ago: try again in about {minutes} {minute_word}. "
              "Check your spam folder too.",
    },
    "minute_singular": {"it": "minuto", "en": "minute"},
    "minute_plural": {"it": "minuti", "en": "minutes"},
    "email_daily_limit": {
        "it": "Il servizio ha raggiunto il numero massimo di email per oggi. Riprova più tardi.",
        "en": "The service has reached today's maximum number of emails. Please try again later.",
    },
    "request_too_large": {
        "it": "La richiesta è troppo grande: gli allegati possono pesare al massimo 10 MB in tutto.",
        "en": "The request is too large: attachments can weigh at most 10 MB in total.",
    },

    # --- Account: conferme -------------------------------------------------
    "registered": {
        "it": "Registrazione completata. Controlla la tua email per il codice di verifica.",
        "en": "Registration complete. Check your email for the verification code.",
    },
    "email_verified": {
        "it": "Email verificata con successo. Ora puoi accedere.",
        "en": "Email verified. You can sign in now.",
    },
    "new_code_sent": {
        "it": "Nuovo codice generato.",
        "en": "New code generated.",
    },
    "logged_out": {
        "it": "Disconnesso con successo",
        "en": "Signed out",
    },
    "session_revoked": {
        "it": "Sessione revocata",
        "en": "Session revoked",
    },
    "email_change_sent": {
        "it": "Per cambiare l'email ti abbiamo mandato due codici: uno all'indirizzo attuale e uno a quello nuovo.",
        "en": "To change your email we sent you two codes: one to your current address and one to the new one.",
    },
    "email_change_wrong": {
        "it": "Uno dei due codici non è corretto. Tentativi rimasti: {left}.",
        "en": "One of the two codes is incorrect. Attempts left: {left}.",
    },
    "email_change_too_many": {
        "it": "Troppi codici sbagliati: il cambio email è annullato. Riprova dal Profilo.",
        "en": "Too many wrong codes: the email change was cancelled. Try again from your Profile.",
    },
    "email_change_expired": {
        "it": "I codici sono scaduti o il cambio email è stato annullato. Riprova dal Profilo.",
        "en": "The codes have expired or the email change was cancelled. Try again from your Profile.",
    },
    "email_changed": {
        "it": "Email cambiata con successo.",
        "en": "Email changed successfully.",
    },
    "mail_email_change_subject": {
        "it": "Discount Searcher - Cambio dell'email",
        "en": "Discount Searcher - Email change",
    },
    "mail_email_change_old_body": {
        "it": "Gentile utente,\n\n"
              "è stato chiesto di cambiare l'email del tuo account Discount Searcher con questo "
              "indirizzo: {new_email}\n\n"
              "Se sei stato tu, inserisci nell'app questo codice (valido {minutes} minuti), insieme a "
              "quello che arriva al nuovo indirizzo:\n\n"
              "    {code}\n\n"
              "Se NON sei stato tu, non comunicare il codice a nessuno e cambia subito la password "
              "dal Profilo dell'app: chi ha fatto la richiesta conosce la tua password attuale. "
              "Senza questo codice l'email non può essere cambiata.\n\n"
              "Cordiali saluti,\nIl team di Discount Searcher",
        "en": "Hello,\n\n"
              "someone asked to change the email of your Discount Searcher account to this "
              "address: {new_email}\n\n"
              "If it was you, enter this code in the app (valid for {minutes} minutes), together with "
              "the one sent to the new address:\n\n"
              "    {code}\n\n"
              "If it was NOT you, do not share this code with anyone and change your password right away "
              "from the app's Profile: whoever made the request knows your current password. "
              "Without this code the email cannot be changed.\n\n"
              "Kind regards,\nThe Discount Searcher team",
    },
    "mail_email_change_new_body": {
        "it": "Gentile utente,\n\n"
              "per usare questo indirizzo come nuova email del tuo account Discount Searcher, "
              "inserisci nell'app questo codice (valido {minutes} minuti), insieme a quello che arriva "
              "al tuo indirizzo attuale:\n\n"
              "    {code}\n\n"
              "Se non hai chiesto tu questo cambio, ignora questa email.\n\n"
              "Cordiali saluti,\nIl team di Discount Searcher",
        "en": "Hello,\n\n"
              "to use this address as the new email of your Discount Searcher account, enter this "
              "code in the app (valid for {minutes} minutes), together with the one sent to your "
              "current address:\n\n"
              "    {code}\n\n"
              "If you did not ask for this change, ignore this email.\n\n"
              "Kind regards,\nThe Discount Searcher team",
    },
    "no_changes": {
        "it": "Nessuna modifica da salvare",
        "en": "No changes to save",
    },
    "profile_updated": {
        "it": "Profilo aggiornato con successo",
        "en": "Profile updated",
    },
    "history_added": {
        "it": "Aggiunto alla cronologia",
        "en": "Added to your history",
    },
    "forgot_generic": {
        "it": "Se l'account esiste, riceverai un'email con le istruzioni per reimpostare la password.",
        "en": "If the account exists, you will receive an email with instructions to reset your password.",
    },
    "password_reset_done": {
        "it": "Password reimpostata con successo. Effettua di nuovo il login.",
        "en": "Password reset. Please sign in again.",
    },

    # --- Dati non validi ---------------------------------------------------
    "invalid_too_long": {
        "it": "{field}: al massimo {limit} caratteri",
        "en": "{field}: at most {limit} characters",
    },
    "invalid_too_short": {
        "it": "{field}: almeno {limit} caratteri",
        "en": "{field}: at least {limit} characters",
    },
    "invalid_missing": {
        "it": "{field}: campo obbligatorio",
        "en": "{field}: required",
    },
    "invalid_generic": {
        "it": "{field}: valore non valido",
        "en": "{field}: invalid value",
    },
    "invalid_password_short": {
        "it": "La password deve avere almeno {limit} caratteri",
        "en": "The password must be at least {limit} characters long",
    },
    "invalid_gmail": {
        "it": "L'email deve essere un indirizzo @gmail.com valido",
        "en": "The email must be a valid @gmail.com address",
    },
    "invalid_username_empty": {
        "it": "Username non può essere vuoto",
        "en": "Username cannot be empty",
    },
    "invalid_subject_multiline": {
        "it": "L'oggetto deve stare su una sola riga",
        "en": "The subject must be a single line",
    },

    # --- Ticket ------------------------------------------------------------
    "ticket_not_found": {
        "it": "Ticket non trovato",
        "en": "Ticket not found",
    },
    "ticket_closed": {
        "it": "Il ticket è chiuso e non accetta nuove risposte",
        "en": "This ticket is closed and does not accept new replies",
    },
    "too_many_tickets": {
        "it": "Hai aperto troppi ticket nelle ultime 24 ore. Rispondi a un ticket esistente "
              "oppure riprova domani.",
        "en": "You have opened too many tickets in the last 24 hours. Reply to an existing ticket "
              "or try again tomorrow.",
    },
    "too_many_replies": {
        "it": "Hai inviato molti messaggi nell'ultima ora. Aspetta un po' prima di scriverne "
              "un altro: il team li legge tutti.",
        "en": "You have sent many messages in the last hour. Please wait a little before writing "
              "another one: the team reads them all.",
    },
    "attachments_not_sent": {
        "it": "Non è stato possibile inviare gli allegati al team, quindi la richiesta non è stata "
              "registrata. Riprova tra qualche minuto, oppure inviala senza allegati.",
        "en": "The attachments could not be sent to the team, so your request was not saved. "
              "Try again in a few minutes, or send it without attachments.",
    },

    # --- Allegati ----------------------------------------------------------
    "attachment_too_many": {
        "it": "Puoi allegare al massimo {limit} file.",
        "en": "You can attach at most {limit} files.",
    },
    "attachment_broken": {
        "it": "Il file \"{name}\" non è arrivato integro: riprova ad allegarlo.",
        "en": "The file \"{name}\" did not arrive intact: try attaching it again.",
    },
    "attachment_empty": {
        "it": "Il file \"{name}\" è vuoto.",
        "en": "The file \"{name}\" is empty.",
    },
    "attachment_too_big": {
        "it": "Il file \"{name}\" supera {limit}.",
        "en": "The file \"{name}\" is larger than {limit}.",
    },
    "attachment_bad_type": {
        "it": "Il file \"{name}\" non è un PDF o un'immagine valida: sono accettati solo "
              "PDF, PNG, JPG, GIF e WEBP.",
        "en": "The file \"{name}\" is not a valid PDF or image: only PDF, PNG, JPG, GIF and WEBP "
              "are accepted.",
    },
    "attachment_total_too_big": {
        "it": "Gli allegati insieme superano {limit}.",
        "en": "The attachments together are larger than {limit}.",
    },
    "attachment_summary": {
        "it": "Allegati inviati al team: {files}",
        "en": "Attachments sent to the team: {files}",
    },

    # --- Stati del ticket, come li vede l'utente ---------------------------
    "status_open": {"it": "Aperto", "en": "Open"},
    "status_progress": {"it": "In lavorazione", "en": "In progress"},
    "status_waiting": {"it": "In attesa di risposta", "en": "Waiting for your reply"},
    "status_resolved": {"it": "Risolto", "en": "Resolved"},
    "status_closed": {"it": "Chiuso", "en": "Closed"},

    # --- Email: verifica dell'indirizzo ------------------------------------
    "mail_verify_subject": {
        "it": "Discount Searcher - Codice di verifica",
        "en": "Discount Searcher - Verification code",
    },
    "mail_verify_body": {
        "it": "Gentile utente,\n\n"
              "grazie per esserti registrato su Discount Searcher.\n\n"
              "Per completare la registrazione e attivare il tuo account, inserisci il seguente "
              "codice di verifica nell'app:\n\n"
              "    {code}\n\n"
              "Il codice è valido per 15 minuti.\n\n"
              "Se non hai richiesto tu questa registrazione, puoi ignorare questa email in tutta sicurezza.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "thank you for signing up to Discount Searcher.\n\n"
              "To complete your registration and activate your account, enter this verification "
              "code in the app:\n\n"
              "    {code}\n\n"
              "The code is valid for 15 minutes.\n\n"
              "If you did not sign up, you can safely ignore this email.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },

    # --- Email: modifiche al profilo ---------------------------------------
    "mail_profile_subject": {
        "it": "Discount Searcher - Il tuo account è stato modificato",
        "en": "Discount Searcher - Your account was changed",
    },
    "mail_profile_body": {
        "it": "Gentile utente,\n\n"
              "ti scriviamo per informarti che il {changed_at} sono state modificate le seguenti "
              "informazioni del tuo account Discount Searcher: {changes}.{extra}\n\n"
              "Se sei stato tu a effettuare questa modifica, non devi fare nulla.\n\n"
              "Se invece non riconosci questa attività, contattaci immediatamente.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "we are writing to let you know that on {changed_at} the following details of your "
              "Discount Searcher account were changed: {changes}.{extra}\n\n"
              "If it was you, there is nothing to do.\n\n"
              "If you do not recognise this activity, contact us immediately.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },
    "mail_profile_extra_password": {
        "it": "\n\nPer sicurezza, abbiamo disconnesso automaticamente tutti gli altri "
              "dispositivi collegati al tuo account.",
        "en": "\n\nFor your safety, we automatically signed out every other device connected to "
              "your account.",
    },
    "field_username": {"it": "username", "en": "username"},
    "field_email": {"it": "email", "en": "email"},
    "field_password": {"it": "password", "en": "password"},

    # --- Email: recupero password ------------------------------------------
    "mail_reset_subject": {
        "it": "Discount Searcher - Reimposta la tua password",
        "en": "Discount Searcher - Reset your password",
    },
    "mail_reset_body": {
        "it": "Gentile utente,\n\n"
              "abbiamo ricevuto una richiesta per reimpostare la password del tuo account Discount Searcher.\n\n"
              "Il codice per procedere è:\n\n"
              "    {code}\n\n"
              "Il codice è valido per 15 minuti.\n\n"
              "Se non hai richiesto tu questa operazione, ignora questa email: la tua password non verrà modificata.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "we received a request to reset the password of your Discount Searcher account.\n\n"
              "Your code is:\n\n"
              "    {code}\n\n"
              "The code is valid for 15 minutes.\n\n"
              "If you did not ask for this, ignore this email: your password will not be changed.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },
    "mail_reset_done_subject": {
        "it": "Discount Searcher - La tua password è stata reimpostata",
        "en": "Discount Searcher - Your password was reset",
    },
    "mail_reset_done_body": {
        "it": "Gentile utente,\n\n"
              "la password del tuo account Discount Searcher è stata appena reimpostata tramite la "
              "procedura \"Password dimenticata\". Per sicurezza, tutti i dispositivi collegati sono "
              "stati disconnessi.\n\n"
              "Se sei stato tu, non devi fare nulla.\n\n"
              "Se invece non riconosci questa attività, contattaci immediatamente.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "the password of your Discount Searcher account has just been reset through the "
              "\"Forgot password\" procedure. For your safety, every connected device was signed out.\n\n"
              "If it was you, there is nothing to do.\n\n"
              "If you do not recognise this activity, contact us immediately.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },

    # --- Email: ticket -----------------------------------------------------
    "mail_ticket_received_subject": {
        "it": "Discount Searcher - Ticket {ticket_id} ricevuto",
        "en": "Discount Searcher - Ticket {ticket_id} received",
    },
    "mail_ticket_received_body": {
        "it": "Gentile utente,\n\n"
              "abbiamo ricevuto {what} \"{subject}\" (ticket {ticket_id}).\n\n"
              "Ti avviseremo via email quando il team risponderà. Puoi seguire il ticket e "
              "rispondere da qui:\n{url}\n\n"
              "Per favore non rispondere a questa email: usa la pagina del ticket.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "we have received {what} \"{subject}\" (ticket {ticket_id}).\n\n"
              "We will email you when the team replies. You can follow the ticket and answer here:\n"
              "{url}\n\n"
              "Please do not reply to this email: use the ticket page.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },
    "what_support_request": {
        "it": "la tua richiesta di assistenza",
        "en": "your support request",
    },
    "what_application": {
        "it": "la tua candidatura",
        "en": "your application",
    },
    "mail_ticket_update_subject": {
        "it": "Discount Searcher - Aggiornamento sul ticket {ticket_id}",
        "en": "Discount Searcher - Update on ticket {ticket_id}",
    },
    "mail_ticket_update_body": {
        "it": "Gentile utente,\n\n"
              "c'è un aggiornamento sul tuo ticket {ticket_id} \"{subject}\".\n\n"
              "{reply}"
              "Stato attuale: {status}\n\n"
              "Per rispondere, apri il ticket:\n{url}\n\n"
              "Per favore non rispondere a questa email: la risposta non arriverebbe al team.\n\n"
              "Cordiali saluti,\n"
              "Il team di Discount Searcher",
        "en": "Hello,\n\n"
              "there is an update on your ticket {ticket_id} \"{subject}\".\n\n"
              "{reply}"
              "Current status: {status}\n\n"
              "To answer, open the ticket:\n{url}\n\n"
              "Please do not reply to this email: your answer would not reach the team.\n\n"
              "Best regards,\n"
              "The Discount Searcher team",
    },
    "mail_ticket_update_reply": {
        "it": "{staff_name} ha scritto:\n\n{message}\n\n",
        "en": "{staff_name} wrote:\n\n{message}\n\n",
    },
}
