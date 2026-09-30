"""
Funzioni di sicurezza: hashing delle password e generazione del codice di
verifica email.

Stessa identica logica già usata (e testata) nel database.py dell'app
desktop — PBKDF2-HMAC-SHA256 con salt casuale, confronto a tempo costante,
codice a 6 cifre generato con 'secrets' — semplicemente spostata qui, lato
server, così l'app desktop non dovrà più contenere questa logica.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone, timedelta

_PBKDF2_ITERATIONS = 260_000
_SESSION_VALIDITY_DAYS = 30

def hash_password(password, salt=None):
    """Genera un hash 'salt$hash' della password, con salt casuale se non fornito."""
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${hashed.hex()}"

def verify_password(password, stored):
    """Verifica una password in chiaro contro il valore 'salt$hash' salvato."""
    try:
        salt_hex, _ = stored.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    return hmac.compare_digest(hash_password(password, salt), stored)

def generate_verification_code():
    """Codice numerico a 6 cifre, generato con 'secrets' (non prevedibile)."""
    return f"{secrets.randbelow(1_000_000):06d}"

def codes_match(a, b):
    """Confronto a tempo costante tra il codice inserito e quello salvato."""
    return hmac.compare_digest(a, b)

def generate_session_token():
    """
    Genera un token di sessione casuale e sicuro (32 byte, codificato per essere
    sicuro dentro un URL/header). Questo è il valore che il client riceve e deve
    presentare ad ogni richiesta successiva.
    """
    return secrets.token_urlsafe(32)

def hash_token(token):
    """
    Hash del token per salvarlo nella tabella sessions — mai il token in chiaro,
    stessa logica delle password. A differenza delle password, qui basta SHA-256
    (senza il lavoro extra di PBKDF2): il token ha già altissima entropia perché
    generato casualmente, non è una parola scelta da una persona e quindi non è
    vulnerabile agli stessi attacchi a dizionario di una password debole.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def session_expiry():
    """Data/ora di scadenza per una sessione appena creata (adesso + 30 giorni)."""
    return datetime.now(timezone.utc) + timedelta(days=_SESSION_VALIDITY_DAYS)
