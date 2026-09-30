"""
Modalità manutenzione: sito e app si fermano con un avviso mentre il team aggiorna.

Si accende dalle variabili d'ambiente di Render (o dal .env in locale):
    MAINTENANCE_MODE=1
e si spegne togliendola, o mettendola a 0. Render riavvia il server quando cambia
una variabile: ci vuole circa un minuto.

Con la manutenzione accesa:
- GET /status risponde {"maintenance": true, "message": "..."} nella lingua della
  richiesta: il sito e l'app lo leggono all'avvio e mostrano la schermata
  "aggiornamento in corso";
- tutti gli altri endpoint rispondono 503 con {"error": "maintenance", ...}: così si
  fermano anche le versioni dell'app già installate, che /status non lo conoscono;
- /health continua a rispondere, perché Render lo usa per sapere se il server è vivo;
- le richieste OPTIONS (il "preflight" del browser) passano, altrimenti il sito non
  riuscirebbe nemmeno a leggere la risposta di /status.

Middleware ASGI "puro" come quello del limite sulle richieste (body_limit.py):
risponde prima che la richiesta arrivi agli endpoint e prima che se ne legga il corpo.
"""
import json
import os

import i18n

#Sempre raggiungibili, anche in manutenzione
_ALWAYS_OPEN = {"/health", "/status"}

#Fra quanto suggerire di riprovare, in secondi (intestazione Retry-After): un'ora.
#Un aggiornamento può durare ore o giorni, quindi niente attese di pochi minuti.
_RETRY_AFTER = "3600"


def is_on():
    """True se la manutenzione è accesa. Si legge a ogni richiesta: costa niente."""
    return os.getenv("MAINTENANCE_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def message(lang):
    """Il testo mostrato a sito e app, nella lingua richiesta."""
    return i18n.t("maintenance", lang)


class MaintenanceMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (scope["type"] != "http" or not is_on()
                or scope.get("method") == "OPTIONS" or scope.get("path") in _ALWAYS_OPEN):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        lang = i18n.from_accept_language(headers.get(b"accept-language", b"").decode("latin-1"))
        body = json.dumps({"detail": {"error": "maintenance", "message": message(lang)}}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 503,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
                (b"retry-after", _RETRY_AFTER.encode()),
            ],
        })
        await send({"type": "http.response.body", "body": body})
