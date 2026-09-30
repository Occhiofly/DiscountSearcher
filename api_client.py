"""
Client HTTP per il backend API di Discount Searcher.

Sostituisce completamente database.py ed email_utils.py nell'app desktop:
da qui in poi l'app non tocca più direttamente né il database né l'invio
delle email — parla solo con l'API via richieste HTTP (usando 'requests',
già una dipendenza esistente grazie a backend.py), ed è l'API a occuparsi
di tutto il resto lato server.
"""
import requests
from api_config import API_BASE_URL

#Lingua da chiedere al server (intestazione Accept-Language): main.py la collega a
#strings.current, così i messaggi e le email arrivano nella lingua scelta nell'app.
language_provider = lambda: "it"

#Attesa massima: (connessione, risposta), in secondi. La risposta può tardare fino a
#un minuto quando il server su Render si sta "svegliando" dopo un periodo senza
#richieste: con un'attesa più corta il primo accesso della giornata fallirebbe
#sempre con "Impossibile contattare il server", anche con il server funzionante.
_TIMEOUT = (10, 75)

#Chiamata quando il server risponde che è in manutenzione: main.py la collega
#all'avviso a schermo intero. Così non serve gestire il caso in ogni schermata.
on_maintenance = None

class APIError(Exception):
    """
    Sollevata per qualunque errore restituito dall'API (credenziali sbagliate,
    dati non validi, username già in uso, ecc.).
    """
    def __init__(self, message, status_code=None, error_code=None, email=None):
        self.status_code = status_code
        self.error_code = error_code #es. "email_not_verified": per distinguere casi specifici da gestire diversamente
        self.email = email #Presente solo per l'errore "email_not_verified"
        super().__init__(message)

class ConnectionErrorAPI(Exception):
    """Sollevata quando l'API non è raggiungibile (rete assente, server spento, ecc.)."""
    pass

#Messaggio da mostrare all'utente per ConnectionErrorAPI, uguale in tutte le schermate
CONNECTION_ERROR_TEXT = ("Impossibile contattare il server. Controlla la connessione a internet; "
                         "se il server non veniva usato da un po' può servire fino a un minuto per "
                         "avviarsi, quindi riprova.")

def _request(method, path, token=None, **kwargs):
    """
    Funzione privata che fa la richiesta HTTP vera e propria, centralizzando
    la gestione degli errori: ogni funzione pubblica sotto la richiama invece
    di ripetere try/except e interpretazione degli errori ad ogni chiamata.
    """
    headers = kwargs.pop("headers", {})
    timeout = kwargs.pop("timeout", _TIMEOUT)
    headers.setdefault("Accept-Language", language_provider())
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(method, f"{API_BASE_URL}{path}", headers=headers, timeout=timeout, **kwargs)
    except requests.exceptions.RequestException as e:
        raise ConnectionErrorAPI(f"Impossibile contattare il server: {e}")

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = None

        #L'API a volte restituisce 'detail' come stringa semplice (es. "Password attuale errata"),
        #a volte come oggetto con 'error'+'message' (es. per l'email non verificata) — gestiamo entrambi.
        if isinstance(detail, dict):
            message = detail.get("message", "Errore sconosciuto")
            error_code = detail.get("error")
            email = detail.get("email")
        else:
            message = detail or "Errore sconosciuto"
            error_code = None
            email = None

        if error_code == "maintenance" and on_maintenance is not None:
            on_maintenance(message)
        raise APIError(message, status_code=response.status_code, error_code=error_code, email=email)

    return response.json() if response.content else None

def get_status():
    """
    Stato del servizio: {"maintenance": True/False, "message": ...}. Attesa breve,
    perché si chiede all'avvio: se il server tarda, l'app non deve restare bloccata.
    """
    return _request("GET", "/status", timeout=(5, 8))

def register(username, password, email, birth_date):
    """birth_date deve essere una stringa 'AAAA-MM-GG' (formato ISO)."""
    return _request("POST", "/register", json={
        "username": username, "password": password, "email": email, "birth_date": birth_date,
    })

def verify_email(username, code):
    return _request("POST", "/verify-email", json={"username": username, "code": code})

def resend_code(username):
    return _request("POST", "/resend-code", json={"username": username})

def forgot_password(username):
    return _request("POST", "/forgot-password", json={"username": username})

def reset_password(username, code, new_password):
    return _request("POST", "/reset-password", json={"username": username, "code": code, "new_password": new_password})

def login(username, password, device_info=None):
    return _request("POST", "/login", json={"username": username, "password": password, "device_info": device_info})

def get_me(token):
    return _request("GET", "/me", token=token)

def logout(token):
    return _request("POST", "/logout", token=token)

def update_profile(token, username, email, current_password, password=None):
    body = {"username": username, "email": email, "current_password": current_password}
    if password:
        body["password"] = password
    return _request("PATCH", "/me", token=token, json=body)

def confirm_email_change(token, old_code, new_code):
    """Conferma il cambio email con i due codici (all'indirizzo attuale e al nuovo)."""
    return _request("POST", "/me/email/confirm", token=token,
                    json={"old_code": old_code, "new_code": new_code})

def get_history(token, limit=10):
    return _request("GET", f"/history?limit={limit}", token=token)

def add_history(token, title, deal_id):
    return _request("POST", "/history", token=token, json={"title": title, "deal_id": deal_id})

def list_sessions(token):
    return _request("GET", "/sessions", token=token)

def revoke_session(token, session_id):
    return _request("POST", f"/sessions/{session_id}/revoke", token=token)
