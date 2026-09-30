"""
Server locale per lavorare sul sito.

Uso (dalla cartella web/):
    python server.py           -> http://127.0.0.1:5510
    python server.py 8080      -> porta diversa

Differenze rispetto a "python -m http.server":
- ogni risposta dice al browser di ricontrollare il file prima di riusarlo
  (Cache-Control: no-cache). Senza, Chrome tiene in cache i file JavaScript e
  CSS e, dopo una modifica, può continuare a mostrare la versione vecchia;
- gli indirizzi senza estensione funzionano come su Netlify: /assistenza serve
  assistenza.html. Così in locale il sito si comporta come quello pubblicato;
- applica le intestazioni di sicurezza scritte nel file _headers, come Netlify:
  un errore nella Content-Security-Policy si vede subito anche in locale.

Solo per lo sviluppo: in produzione il sito è servito da un hosting statico.
"""
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent


def read_site_headers():
    """
    Intestazioni della sezione "/*" del file _headers (stesso formato di Netlify:
    una riga col percorso, poi le intestazioni rientrate). Sono supportate solo
    quelle valide per tutto il sito, le uniche usate.
    """
    path = SITE_DIR / "_headers"
    if not path.is_file():
        return []
    headers, in_all = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            in_all = line.strip() == "/*"
        elif in_all and ":" in line:
            name, value = line.strip().split(":", 1)
            headers.append((name.strip(), value.strip()))
    return headers


class NoCacheHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        #Come i "Pretty URLs" di Netlify: se /assistenza non esiste ma esiste
        #assistenza.html, serviamo quello. I file e le cartelle reali hanno la
        #precedenza, quindi /assets/... e /downloads/... non cambiano.
        real = super().translate_path(path)
        if not Path(real).exists() and Path(real + ".html").is_file():
            return real + ".html"
        return real

    def end_headers(self):
        #no-cache non significa "non salvare": il browser può tenere il file,
        #ma deve chiedere al server se è cambiato prima di usarlo. Se non è
        #cambiato riceve un 304 e la pagina resta veloce.
        self.send_header("Cache-Control", "no-cache")
        #Riletto a ogni risposta: modificando _headers non serve riavviare il server
        for name, value in read_site_headers():
            self.send_header(name, value)
        super().end_headers()


class QuietServer(ThreadingHTTPServer):
    #Chrome apre connessioni in anticipo e poi le chiude senza usarle (o le
    #interrompe quando si ricarica la pagina). Su Windows il server di base lo
    #stampa come un lungo traceback "ConnectionResetError [WinError 10054]",
    #che sembra un errore ma non lo è: la pagina funziona comunque.
    #Qui ignoriamo solo questi casi; qualsiasi altro errore viene mostrato.

    #Su Windows SO_REUSEADDR (attivo di default nel server di Python) permette a
    #DUE server di occupare la stessa porta, con le richieste smistate a caso fra
    #i due: un terminale dimenticato aperto servirebbe file vecchi senza avvisare.
    #SO_EXCLUSIVEADDRUSE fa invece fallire il secondo avvio, come ci si aspetta.
    allow_reuse_address = sys.platform != "win32"

    def server_bind(self):
        if sys.platform == "win32":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5510
    #Serve sempre la cartella di questo file, da qualunque cartella lo si lanci
    handler = partial(NoCacheHandler, directory=str(SITE_DIR))
    try:
        server = QuietServer(("127.0.0.1", port), handler)
    except OSError:
        #Succede quasi sempre perché un altro server è già aperto su quella porta
        print(f"La porta {port} è già in uso: probabilmente il sito è già avviato in un "
              f"altro terminale. Chiudilo oppure usa un'altra porta: python server.py 5520")
        sys.exit(1)
    print(f"Sito disponibile su http://127.0.0.1:{port}  (Ctrl+C per fermare)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
