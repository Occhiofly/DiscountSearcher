"""
Catture reali dell'app per i post e per le schede nelle directory.

Avvia main.py contro l'API di prova (account e cronologia), ma le offerte
mostrate sono quelle vere di CheapShark. Produce:
    01-lingua.png      la schermata del primo avvio
    02-accesso.png     login e registrazione
    03-ricerca.png     menu principale prima della ricerca
    04-risultati.png   risultati di una ricerca vera
    demo.gif           la sequenza, per i social

Uso: python screenshot_app.py <it|en> <cartella-di-uscita>
"""
import os
import runpy
import shutil
import sys
import tempfile

LINGUA = sys.argv[1]
USCITA = os.path.abspath(sys.argv[2])
NEGOZIO = sys.argv[3] if len(sys.argv) > 3 else "Steam"
SCONTO = sys.argv[4] if len(sys.argv) > 4 else "50%+"
TESTO = sys.argv[5] if len(sys.argv) > 5 else ""
os.makedirs(USCITA, exist_ok=True)
APP_DIR = r"C:/Users/maral/Desktop/Progetti/App python Vittorio/DiscountSearcher"

WORK = tempfile.mkdtemp(prefix="ds_shot_")
APPDATA = os.path.join(WORK, "appdata")
CWD = os.path.join(WORK, "avvio")
os.makedirs(APPDATA); os.makedirs(CWD)
os.environ["APPDATA"] = APPDATA
os.chdir(CWD)
sys.path.insert(0, APP_DIR)

import api_config  # noqa: E402
api_config.API_BASE_URL = "http://127.0.0.1:8765"
import strings  # noqa: E402
strings.system_language = lambda: LINGUA

UTENTE = "vittorio"
PASSWORD = "PasswordProva4!"

frames = []


def scatta(app, nome):
    from PIL import ImageGrab
    import time
    #La finestra deve stare davvero davanti, altrimenti si cattura quello che c'e' sopra
    app.lift()
    app.attributes("-topmost", True)
    app.focus_force()
    app.update()
    app.update_idletasks()
    time.sleep(0.6)
    x, y = app.winfo_rootx(), app.winfo_rooty()
    w, h = app.winfo_width(), app.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    percorso = os.path.join(USCITA, nome)
    img.save(percorso)
    frames.append(img.convert("P", palette=1, colors=128))
    print("  ", nome, flush=True)
    return img


def sequenza(app):
    try:
        scatta(app, "01-lingua.png")
        app._choose_language(LINGUA)
        app.update()
        scatta(app, "02-accesso.png")

        app.login_username_entry.insert(0, UTENTE)
        app.login_password_entry.insert(0, PASSWORD)
        app._handle_login()
        app.update()
        scatta(app, "03-ricerca.png")

        #Ricerca vera: negozio e sconto minimo scelti da riga di comando
        app.sidebar_menu.set(NEGOZIO)
        app.sidebar_discount_menu.set(SCONTO)
        if TESTO:
            app.sidebar_entry.insert(0, TESTO)
        app.update()
        app._handle_search()
        app.after(9000, lambda: fine(app))
        return
    except Exception as e:
        print("ERRORE:", type(e).__name__, e, flush=True)
        app.destroy()


def fine(app):
    import time
    try:
        #Dopo una ricerca lunga la finestra puo' restare non ridisegnata: la sveglio
        app.deiconify()
        app.lift()
        app.update()
        time.sleep(1.5)
        app.update()
        scatta(app, "04-risultati.png")
        #Avviso di manutenzione, come appare quando il team aggiorna
        app._show_maintenance(None)
        app.update()
        time.sleep(0.8)
        scatta(app, "05-manutenzione.png")
        frames.pop()  #Non fa parte dell'animazione per i social
        #Una piccola animazione con i passaggi, per i social
        if len(frames) >= 3:
            frames[0].save(os.path.join(USCITA, "demo.gif"), save_all=True,
                           append_images=frames[1:], duration=[1500, 1800, 1800, 3000][:len(frames)],
                           loop=0, optimize=True)
            print("   demo.gif", flush=True)
    finally:
        app.destroy()


import customtkinter  # noqa: E402
_real = customtkinter.CTk.mainloop
def _mainloop(self, *a, **kw):
    self.after(1500, lambda: sequenza(self))
    self.after(40000, self.destroy)
    _real(self, *a, **kw)
customtkinter.CTk.mainloop = _mainloop

try:
    runpy.run_path(os.path.join(APP_DIR, "main.py"), run_name="main")
finally:
    shutil.rmtree(WORK, ignore_errors=True)
print("catture in", USCITA)
