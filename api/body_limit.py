"""
Limite alla dimensione delle richieste in arrivo.

Controllare solo l'intestazione Content-Length non basta: una richiesta inviata
"a pezzi" (Transfer-Encoding: chunked) non la dichiara, e FastAPI leggerebbe
comunque tutto il corpo in memoria per interpretare il JSON, prima ancora di
verificare il login. Qui invece il corpo viene letto contando i byte, e la
lettura si ferma appena si supera il limite: in memoria non finisce mai più di
max_bytes, qualunque cosa mandi il client.

Middleware ASGI "puro" (non @app.middleware): solo così si può intercettare la
lettura del corpo mentre avviene.
"""
from fastapi.responses import JSONResponse

import i18n


class BodySizeLimitMiddleware:
    def __init__(self, app, max_bytes):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        #Dimensione dichiarata oltre il limite: rifiutata senza leggere niente
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None and declared.isdigit() and int(declared) > self.max_bytes:
            await self._too_large(scope, receive, send)
            return

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return #Il client se n'è andato: non c'è nessuno a cui rispondere
            body += message.get("body", b"")
            if len(body) > self.max_bytes:
                await self._too_large(scope, receive, send)
                return
            if not message.get("more_body", False):
                break

        #L'applicazione riceve il corpo già letto, tutto in una volta; le letture
        #successive tornano al client vero (servono a rilevarne la disconnessione).
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)

    @staticmethod
    async def _too_large(scope, receive, send):
        #La lingua si legge a mano dalle intestazioni: qui non c'è ancora una richiesta FastAPI
        header = dict(scope.get("headers") or {}).get(b"accept-language", b"").decode("latin-1")
        message = i18n.t("request_too_large", i18n.from_accept_language(header))
        response = JSONResponse(status_code=413, content={"detail": message})
        await response(scope, receive, send)
