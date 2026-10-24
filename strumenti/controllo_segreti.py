"""
Blocca i commit che contengono credenziali.

Lo lancia il gancio .githooks/pre-commit prima di ogni commit, sui soli file che
stai per committare. Se trova qualcosa, il commit non parte e ti dice dove.

Perché serve, anche se GitHub ha già il blocco al push: GitHub riconosce le chiavi
di servizi noti (token GitHub, chiavi AWS…), ma non sa che `DATABASE_URL=...` con
dentro la password di Supabase è un segreto nostro. Ed è esattamente il file che
era finito nella vecchia storia del progetto.

Si può usare anche a mano su file qualsiasi:
    python strumenti/controllo_segreti.py api/.env altro_file.py
"""
import re
import subprocess
import sys

#Ogni voce: (cosa è, espressione che lo riconosce)
SOSPETTI = [
    ("indirizzo di un database con la password dentro",
     re.compile(r"postgres(?:ql)?://[^\s:@/]+:[^\s@/]{3,}@", re.I)),
    ("DATABASE_URL valorizzata",
     re.compile(r"DATABASE_URL\s*[=:]\s*['\"]?\S{12,}", re.I)),
    ("password per le app di Gmail (16 lettere)",
     re.compile(r"GMAIL_APP_PASSWORD\s*[=:]\s*['\"]?[a-z]{16}\b", re.I)),
    ("token di GitHub",
     re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("chiave di Render",
     re.compile(r"\brnd_[A-Za-z0-9]{20,}\b")),
    ("chiave di servizio Supabase (JWT)",
     re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("token del bot Discord",
     re.compile(r"\b[MNO][A-Za-z\d_-]{22,}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{25,}\b")),
    ("DISCORD_TOKEN valorizzata",
     re.compile(r"DISCORD_(?:BOT_)?TOKEN\s*[=:]\s*['\"]?\S{20,}", re.I)),
    ("webhook di Discord",
     re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d+/[\w-]{20,}", re.I)),
    ("chiave privata",
     re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("password scritta nel codice",
     re.compile(r"(?:password|passwd|secret|api[_-]?key)\s*=\s*['\"][^'\"]{8,}['\"]", re.I)),
]

#Righe che parlano di credenziali senza contenerne: esempi, segnaposto, nomi di variabili.
INNOCUE = re.compile(
    r"xxxx|la_tua|il_tuo|your_|placeholder|esempio|example|<.*>|\.\.\.|"
    r"os\.environ|getenv|password_hash|hash_password|verify_password|"
    r"current_password|new_password|payload\.password|entry\.get|textvariable|"
    r"t\(|i18n|show=|type=\"password\"|\{password\}|\$\{|%s|\$1",
    re.I)

#File che non devono proprio essere committati, qualunque cosa contengano
VIETATI = re.compile(r"(^|/)\.env$|(^|/)\.env\.[^/]*$|(^|/)session\.json$|(^|/)backup/|\.zip$", re.I)
#...tranne questi, che sono modelli senza valori veri
PERMESSI = re.compile(r"\.env\.example$|\.env\.esempio$", re.I)


def file_del_commit():
    """I file aggiunti o modificati in questo commit (non quelli cancellati)."""
    uscita = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [r.strip() for r in uscita.stdout.splitlines() if r.strip()]


def contenuto_in_commit(percorso):
    """Il contenuto del file così come verrà committato (non come sta sul disco)."""
    uscita = subprocess.run(["git", "show", f":{percorso}"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return uscita.stdout if uscita.returncode == 0 else ""


def controlla(percorso, testo):
    """Elenco di (riga, cosa è, estratto) per ogni sospetto trovato."""
    trovati = []
    if VIETATI.search(percorso) and not PERMESSI.search(percorso):
        trovati.append((0, "file che non va committato", percorso))
    for numero, riga in enumerate(testo.splitlines(), start=1):
        if INNOCUE.search(riga):
            continue
        for descrizione, espressione in SOSPETTI:
            trovato = espressione.search(riga)
            if trovato:
                estratto = trovato.group(0)
                if len(estratto) > 24:          #non si stampa il segreto per intero
                    estratto = estratto[:12] + "…" + estratto[-4:]
                trovati.append((numero, descrizione, estratto))
                break
    return trovati


def main(argomenti):
    da_leggere = [(p, open(p, encoding="utf-8", errors="replace").read()) for p in argomenti] \
        if argomenti else [(p, contenuto_in_commit(p)) for p in file_del_commit()]

    problemi = []
    for percorso, testo in da_leggere:
        for riga, descrizione, estratto in controlla(percorso, testo):
            problemi.append((percorso, riga, descrizione, estratto))

    if not problemi:
        return 0

    print("\n  COMMIT FERMATO: sembra che tu stia per pubblicare delle credenziali.\n")
    for percorso, riga, descrizione, estratto in problemi:
        dove = f"{percorso}:{riga}" if riga else percorso
        print(f"   {dove}\n      {descrizione}: {estratto}")
    print("\n  Le credenziali vanno nelle variabili d'ambiente su Render e nel file api/.env,")
    print("  che non viene committato. Se invece è un falso allarme (un esempio, un segnaposto),")
    print("  riscrivi la riga in modo che si capisca, oppure committa con --no-verify.")
    print("  Se un segreto vero è già finito in un commit: cambialo subito sul servizio,")
    print("  perché toglierlo dalla storia non basta.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
