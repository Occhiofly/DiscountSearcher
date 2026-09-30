"""
Compila l'app desktop con Nuitka e prepara lo zip per il sito.

Uso (dalla cartella principale del progetto):
    python build_app.py

Risultato:
    build_nuitka/main.dist/                l'applicazione (exe + le sue librerie)
    web/downloads/DiscountSearcher.zip     lo zip scaricabile dal sito
                                           (cartella DiscountSearcher/ da estrarre)

Perché Nuitka e non PyInstaller: PyInstaller mette dentro l'exe i file Python
quasi come sono, e con strumenti gratuiti se ne ricava il codice sorgente in
pochi minuti. Nuitka traduce il Python in C e lo compila in codice macchina:
recuperare il sorgente diventa molto più difficile. Le docstring vengono tolte.

Serve (una volta sola):
    python -m pip install --user nuitka ordered-set zstandard
Alla prima compilazione Nuitka scarica da solo il compilatore C (MinGW, circa
100-200 MB). La prima volta richiede anche 10-20 minuti; le successive meno.

Perché a cartella (--standalone) e non in un solo file (--onefile): l'exe in
file singolo si estrae da solo in una cartella temporanea all'avvio, lo stesso
comportamento dei programmi che nascondono del codice. I modelli automatici
degli antivirus lo segnalano: Windows Defender dava "Trojan:Win32/Wacatac.B!ml"
sul file singolo e nessun rilevamento sulla stessa identica applicazione
distribuita a cartella (verificato con MpCmdRun.exe).

Nota: l'exe non è firmato digitalmente, quindi Windows mostra ancora l'avviso
SmartScreen "Editore sconosciuto" (serve un certificato di firma per toglierlo).
"""
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "build_nuitka")
EXE_NAME = "DiscountSearcher.exe"
ZIP_PATH = os.path.join(ROOT, "web", "downloads", "DiscountSearcher.zip")

#Numero di versione mostrato nelle proprietà del file (tasto destro -> Proprietà -> Dettagli)
from version import APP_VERSION #Numero di versione: un posto solo (version.py)

VERSION = f"{APP_VERSION}.0" #Windows vuole quattro numeri (1.0.7.0)


def build():
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",                               #cartella con exe e librerie: meno falsi positivi
        "--windows-console-mode=disable",             #nessuna finestra nera
        "--enable-plugin=tk-inter",
        "--include-package-data=customtkinter",       #temi e font di customtkinter
        "--include-data-dir=assets=assets",           #icona e immagini dell'app
        "--windows-icon-from-ico=assets/logo.ico",
        "--python-flag=no_docstrings,no_asserts",     #meno testo leggibile dentro l'exe
        "--company-name=DiscountSearcher Team",
        "--product-name=Discount Searcher",
        "--file-description=Discount Searcher - ricerca offerte sui videogiochi",
        f"--file-version={VERSION}",
        f"--product-version={VERSION}",
        "--copyright=(c) 2026 DiscountSearcher Team. Tutti i diritti riservati.",
        "--assume-yes-for-downloads",                 #scarica il compilatore senza chiedere
        f"--output-dir={OUT_DIR}",
        f"--output-filename={EXE_NAME}",
        "main.py",
    ]
    print("Compilazione in corso (la prima volta può richiedere 10-20 minuti)...", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def make_zip():
    """Mette l'intera cartella dell'applicazione nello zip, sotto DiscountSearcher/."""
    dist = os.path.join(OUT_DIR, "main.dist")
    exe = os.path.join(dist, EXE_NAME)
    if not os.path.isfile(exe):
        sys.exit(f"Eseguibile non trovato: {exe}")
    os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)

    temp_zip = ZIP_PATH + ".tmp"
    numero = 0
    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for radice, _, files in os.walk(dist):
            for nome in files:
                percorso = os.path.join(radice, nome)
                dentro = os.path.join("DiscountSearcher", os.path.relpath(percorso, dist))
                z.write(percorso, dentro.replace(os.sep, "/"))
                numero += 1
    os.replace(temp_zip, ZIP_PATH)

    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    #L'impronta serve a chi vuole verificare di aver scaricato il file giusto
    with open(ZIP_PATH, "rb") as f:
        impronta = hashlib.sha256(f.read()).hexdigest()

    print(f"\nZip pronto: {ZIP_PATH} ({size_mb:.0f} MB, {numero} file)")
    print(f"SHA-256: {impronta}")
    print('Se la dimensione è cambiata molto, aggiorna "Archivio ZIP da ... MB" in')
    print('web/index.html e "... MB ZIP archive" in web/en/index.html.')


if __name__ == "__main__":
    if shutil.which("git"):
        #Un promemoria, non un blocco: meglio compilare codice già salvato su git
        dirty = subprocess.run(["git", "status", "--porcelain", "main.py", "backend.py", "api_client.py", "api_config.py"],
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if dirty:
            print("Attenzione: ci sono modifiche non committate ai file dell'app:\n" + dirty + "\n")
    build()
    make_zip()
