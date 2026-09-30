"""
Testi dell'app in italiano e in inglese, e scelta della lingua.

Al primo avvio l'app chiede la lingua all'utente (main.py, _create_language_panel):
la lingua di Windows è solo il suggerimento evidenziato, non una decisione presa al
posto suo. La scelta resta salvata in %APPDATA%\\DiscountSearcher\\settings.json e si
cambia quando si vuole dal pulsante "Italiano | English".

La stessa lingua viene mandata al server (intestazione Accept-Language), così
anche i suoi messaggi e le sue email arrivano nella lingua giusta.

Per aggiungere un testo: una voce in TEXTS con entrambe le lingue, poi t("chiave")
dove serve. I segnaposto {cosi} si riempiono con t("chiave", cosi="valore").
"""
import ctypes
import json
import locale
import os

SUPPORTED = ("it", "en")
DEFAULT = "it"

_current = DEFAULT
_settings_path = None
_chosen = False #True se la lingua è stata scelta dall'utente, non dedotta da Windows


def system_language():
    """Lingua di Windows (o del sistema), riportata a una di quelle supportate."""
    name = ""
    try:
        #Lingua dell'interfaccia di Windows: più affidabile del formato di data/ora
        language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        buffer = ctypes.create_unicode_buffer(85)
        ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, 85)
        name = buffer.value or str(language_id)
    except Exception:
        pass
    if not name:
        try:
            name = locale.getlocale()[0] or ""
        except Exception:
            name = ""
    short = name.replace("_", "-").split("-")[0].lower()
    return short if short in SUPPORTED else DEFAULT


def init(settings_path):
    """
    Imposta la lingua all'avvio: quella scelta in precedenza, altrimenti quella
    del sistema. `settings_path` è il file dove salvare la scelta.
    """
    global _current, _settings_path, _chosen
    _settings_path = settings_path
    saved = None
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            saved = json.load(f).get("language")
    except (OSError, ValueError, AttributeError):
        saved = None #File assente o rovinato: si riparte dalla lingua del sistema
    _chosen = saved in SUPPORTED
    _current = saved if _chosen else system_language()
    return _current


def chosen():
    """
    True se la lingua l'ha scelta l'utente in un avvio precedente. False al primo
    avvio, quando l'app la chiede invece di indovinarla dalle impostazioni di
    Windows: la lingua del sistema resta solo il suggerimento iniziale.
    """
    return _chosen


def current():
    return _current


def other():
    """L'altra lingua, quella su cui il pulsante fa passare."""
    return "en" if _current == "it" else "it"


def read_setting(key, default=None):
    """Una preferenza salvata in settings.json (es. "maximized"), o `default`."""
    try:
        with open(_settings_path, "r", encoding="utf-8") as f:
            return json.load(f).get(key, default)
    except (OSError, ValueError, AttributeError, TypeError):
        return default #File assente o rovinato: vale il valore predefinito


def write_setting(key, value):
    """
    Salva una preferenza senza perdere le altre: il file viene riletto, aggiornato
    e riscritto prima su un file temporaneo, così un'interruzione non lo rovina.
    """
    if not _settings_path:
        return False
    data = {}
    try:
        with open(_settings_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
            if isinstance(saved, dict):
                data = saved
    except (OSError, ValueError):
        data = {} #Riscritto da zero
    data[key] = value
    try:
        os.makedirs(os.path.dirname(_settings_path), exist_ok=True)
        temp_path = _settings_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(temp_path, _settings_path)
        return True
    except OSError:
        return False


def set_language(lang):
    """Cambia lingua e la ricorda. Restituisce True se il salvataggio è riuscito."""
    global _current, _chosen
    if lang not in SUPPORTED:
        return False
    _current = lang
    _chosen = True
    try:
        return write_setting("language", lang)
    except OSError:
        return False #La lingua vale per questa sessione, ma non verrà ricordata


def t(key, **values):
    text = TEXTS[key][_current]
    return text.format(**values) if values else text


TEXTS = {
    # --- Accesso e registrazione ------------------------------------------
    "login_title": {"it": "Accedi", "en": "Sign in"},
    "login_button": {"it": "Accedi", "en": "Sign in"},
    "username": {"it": "Username", "en": "Username"},
    "password": {"it": "Password", "en": "Password"},
    "login_footer": {"it": "Non hai un account? Registrati alla tua destra!",
                     "en": "No account yet? Sign up on the right!"},
    "forgot_link": {"it": "Password dimenticata?", "en": "Forgot your password?"},
    "login_in_progress": {"it": "Accesso in corso...", "en": "Signing in..."},
    "auto_login": {"it": "Accesso automatico in corso...", "en": "Signing you in..."},
    "login_done": {"it": "Login effettuato!", "en": "Signed in!"},
    "login_failed": {"it": "Username o password errati!", "en": "Wrong username or password!"},
    "saved_session_invalid": {"it": "La sessione salvata non è più valida: accedi di nuovo.",
                              "en": "Your saved session is no longer valid: please sign in again."},
    "server_problem": {"it": "Il server ha avuto un problema. Accedi di nuovo, oppure riprova più tardi.",
                       "en": "The server had a problem. Sign in again, or try later."},
    "session_lost": {"it": "La sessione è scaduta o è stata chiusa da un altro dispositivo: accedi di nuovo.",
                     "en": "Your session expired or was closed from another device: please sign in again."},
    "session_not_saved": {
        "it": "Accesso riuscito, ma non è stato possibile salvare la sessione su questo computer: "
              "al prossimo avvio dovrai accedere di nuovo.",
        "en": "Signed in, but the session could not be saved on this computer: you will have to "
              "sign in again next time.",
    },
    "register_title": {"it": "Registrati", "en": "Sign up"},
    "register_button": {"it": "Registrati", "en": "Sign up"},
    "email": {"it": "Email", "en": "Email"},
    "birth_date": {"it": "Data di nascita", "en": "Date of birth"},
    "day": {"it": "Giorno", "en": "Day"},
    "month": {"it": "Mese", "en": "Month"},
    "year": {"it": "Anno", "en": "Year"},
    "fill_all_fields": {"it": "Compila tutti i campi!", "en": "Please fill in every field!"},
    "gmail_required": {"it": "Devi usare un indirizzo email @gmail.com valido!",
                       "en": "You must use a valid @gmail.com address!"},
    "username_taken": {"it": "Username già in uso!", "en": "Username already taken!"},
    "connection_error": {
        "it": "Impossibile contattare il server. Controlla la connessione a internet; se il server "
              "non veniva usato da un po' può servire fino a un minuto per avviarsi, quindi riprova.",
        "en": "Could not reach the server. Check your internet connection; if the server has been "
              "idle for a while it can take up to a minute to start, so try again.",
    },

    # --- Verifica email ----------------------------------------------------
    "verify_title": {"it": "Verifica la tua email", "en": "Verify your email"},
    "verify_desc": {
        "it": "Abbiamo inviato un codice di verifica a {email}. Inseriscilo qui sotto (valido per "
              "15 minuti). Se non lo trovi, controlla anche nella cartella Spam di Gmail.",
        "en": "We sent a verification code to {email}. Enter it below (valid for 15 minutes). "
              "If you cannot find it, check your Gmail spam folder too.",
    },
    "verify_code_label": {"it": "Codice di verifica", "en": "Verification code"},
    "verify_button": {"it": "Verifica", "en": "Verify"},
    "resend_button": {"it": "Invia di nuovo il codice", "en": "Send the code again"},
    "back_to_login": {"it": "← Torna al login", "en": "← Back to sign in"},
    "enter_code": {"it": "Inserisci il codice ricevuto via email!",
                   "en": "Enter the code you received by email!"},
    "verify_done": {"it": "Email verificata! Accedi con le tue credenziali.",
                    "en": "Email verified! Sign in with your credentials."},
    "code_sent": {"it": "Nuovo codice inviato!", "en": "New code sent!"},
    "code_not_sent": {"it": "Codice generato, ma l'invio dell'email non è riuscito.",
                      "en": "Code generated, but the email could not be sent."},
    "send_failed": {"it": "Invio email non riuscito: {reason}", "en": "Email not sent: {reason}"},

    # --- Password dimenticata ----------------------------------------------
    "forgot_title": {"it": "Password dimenticata", "en": "Forgot password"},
    "forgot_desc": {
        "it": "Inserisci il tuo username per ricevere un codice via email, poi inseriscilo insieme "
              "alla nuova password.",
        "en": "Enter your username to receive a code by email, then type it together with your new "
              "password.",
    },
    "forgot_send": {"it": "Invia codice", "en": "Send code"},
    "enter_username": {"it": "Inserisci il tuo username!", "en": "Enter your username!"},
    "code_received": {"it": "Codice ricevuto", "en": "Code received"},
    "new_password": {"it": "Nuova password", "en": "New password"},
    "reset_button": {"it": "Reimposta password", "en": "Reset password"},
    "fill_reset_fields": {"it": "Compila username, codice e nuova password!",
                          "en": "Fill in username, code and new password!"},
    "reset_done": {"it": "Password reimpostata! Accedi con la nuova password.",
                   "en": "Password reset! Sign in with your new password."},
    "forgot_generic": {"it": "Se l'account esiste, riceverai un'email.",
                       "en": "If the account exists, you will receive an email."},

    # --- Ricerca ------------------------------------------------------------
    "search_placeholder": {"it": "Cerca un gioco...", "en": "Search for a game..."},
    "search_button": {"it": "Cerca", "en": "Search"},
    "store": {"it": "Store", "en": "Store"},
    "genre": {"it": "Genere", "en": "Genre"},
    "discount": {"it": "Sconto", "en": "Discount"},
    "all": {"it": "Tutti", "en": "All"},
    "searching": {"it": "Ricerca in corso...", "en": "Searching..."},
    "no_results": {"it": "Nessun risultato trovato con questi filtri",
                   "en": "No results with these filters"},
    "search_connection_error": {
        "it": "Errore di connessione: controlla la connessione a internet e riprova.",
        "en": "Connection error: check your internet connection and try again.",
    },
    "search_unexpected_error": {
        "it": "Si è verificato un errore imprevisto durante la ricerca. Riprova.",
        "en": "Something went wrong during the search. Please try again.",
    },
    "wait_for_search": {"it": "Attendi la fine della ricerca prima di uscire.",
                        "en": "Wait for the search to finish before signing out."},
    "history": {"it": "Cronologia", "en": "History"},
    "link": {"it": "Link 🔗", "en": "Open 🔗"},
    "credits": {"it": "Dati sulle offerte forniti da CheapShark",
                "en": "Deal data provided by CheapShark"},

    # --- Profilo -------------------------------------------------------------
    "profile": {"it": "Profilo", "en": "Profile"},
    "logout": {"it": "Esci dal profilo", "en": "Sign out"},
    "profile_desc": {
        "it": "Qui puoi modificare username, email o password. Lascia il campo password vuoto se "
              "non vuoi cambiarla.",
        "en": "Here you can change your username, email or password. Leave the password field "
              "empty to keep the current one.",
    },
    "password_placeholder": {"it": "Lascia vuoto per non cambiare", "en": "Leave empty to keep it"},
    "save": {"it": "Salva", "en": "Save"},
    "back_to_search": {"it": "← Torna alla ricerca", "en": "← Back to search"},
    "no_changes": {"it": "Nessuna modifica da salvare.", "en": "No changes to save."},
    "confirm_title": {"it": "Conferma modifiche", "en": "Confirm changes"},
    "confirm_desc": {
        "it": "Per modificare i campi Username, Email o Password devi inserire la tua password attuale.",
        "en": "To change your username, email or password you must enter your current password.",
    },
    "current_password": {"it": "Password attuale", "en": "Current password"},
    "enter_current_password": {"it": "Inserisci la password attuale!", "en": "Enter your current password!"},
    "wrong_current_password": {"it": "Password attuale errata!", "en": "Wrong current password!"},
    "cancel": {"it": "← Annulla", "en": "← Cancel"},
    "profile_updated": {"it": "Profilo aggiornato!", "en": "Profile updated!"},
    # --- Dimensione della finestra -------------------------------------------
    "maximize": {"it": "⛶ Ingrandisci finestra", "en": "⛶ Maximise window"},
    "restore_window": {"it": "⛶ Riduci finestra", "en": "⛶ Restore window"},
    # --- Cambio email con due codici (il server non la cambia con la sola password) ---
    "email_change_title": {"it": "Conferma la nuova email", "en": "Confirm your new email"},
    "email_change_desc": {
        "it": "Per sicurezza ti abbiamo mandato due codici: uno all'indirizzo attuale ({old}) e uno a "
              "quello nuovo ({new}). Valgono 15 minuti. Se non li trovi, guarda anche nello Spam.",
        "en": "For your security we sent you two codes: one to your current address ({old}) and one to "
              "the new one ({new}). They are valid for 15 minutes. If you can't find them, check Spam too.",
    },
    "email_change_old_code": {"it": "Codice arrivato all'indirizzo attuale", "en": "Code sent to your current address"},
    "email_change_new_code": {"it": "Codice arrivato al nuovo indirizzo", "en": "Code sent to the new address"},
    "email_change_confirm": {"it": "Conferma", "en": "Confirm"},
    "email_change_codes_needed": {"it": "Inserisci i due codici di 6 cifre!", "en": "Enter both 6-digit codes!"},
    "email_change_not_sent": {
        "it": "Non siamo riusciti a inviare i codici. Riprova fra qualche minuto dal Profilo.",
        "en": "We could not send the codes. Try again in a few minutes from your Profile.",
    },
    "email_change_done": {"it": "Email cambiata!", "en": "Email changed!"},
    "email_change_lost_old": {
        "it": "Non hai più accesso all'indirizzo attuale? Apri un ticket dal sito: il team ti aiuterà.",
        "en": "No longer have access to your current address? Open a ticket on the website: the team will help.",
    },

    # --- Lingua ---------------------------------------------------------------
    # --- Aggiornamento in corso (manutenzione accesa sul server) -----------
    # --- Nuova versione disponibile ------------------------------------------
    "update_title": {"it": "È uscita una versione nuova", "en": "A new version is available"},
    "update_desc": {
        "it": "Hai la {attuale}, l'ultima è la {nuova}. L'app non si aggiorna da sola: "
              "scarica la cartella nuova e sostituisci quella vecchia. Account e cronologia restano com'erano.",
        "en": "You have {attuale}, the latest is {nuova}. The app does not update itself: "
              "download the new folder and replace the old one. Your account and history stay as they are.",
    },
    "update_download": {"it": "Scarica la versione nuova", "en": "Download the new version"},
    "update_later": {"it": "Più tardi", "en": "Later"},
    "update_skip": {"it": "Non ricordarmelo per questa versione", "en": "Don\'t remind me about this version"},
    "maintenance_title": {"it": "Aggiornamento in corso", "en": "Update in progress"},
    "maintenance_text": {
        "it": "Il team sta aggiornando Discount Searcher. L'aggiornamento può richiedere "
              "qualche ora o qualche giorno: tutto riprenderà a funzionare appena sarà "
              "finito. Grazie per la pazienza.",
        "en": "The team is updating Discount Searcher. The update may take a few hours or a "
              "few days: everything will work again as soon as it is finished. Thank you for "
              "your patience.",
    },
    "maintenance_retry": {"it": "Riprova", "en": "Try again"},
    "maintenance_checking": {"it": "Controllo in corso...", "en": "Checking..."},
    "maintenance_still": {"it": "L'aggiornamento non è ancora finito: riprova più tardi.",
                          "en": "The update is not finished yet: please try again later."},
    "maintenance_offline": {"it": "Il server non risponde: controlla la connessione e riprova.",
                            "en": "The server does not answer: check your connection and try again."},
}
