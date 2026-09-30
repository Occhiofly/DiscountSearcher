"""
Ultima versione pubblicata dell'app, letta da api/release.json.

L'app chiede GET /status a ogni avvio (serve già per la modalità manutenzione): nella
risposta trova anche la versione pubblicata e le novità nella sua lingua. Se la sua è
più vecchia, mostra da sola l'avviso "è uscita una versione nuova".

Nessuna email e nessun dato personale: l'avviso lo vede chi apre l'app, cioè proprio
chi deve aggiornare. Per pubblicare una versione nuova si aggiornano version.py e
questo file, e si ripubblica il server.

Il file viene riletto se cambia sulla data di modifica, così su Render basta il deploy
e non serve un riavvio manuale.
"""
import json
import logging
import os

import i18n

log = logging.getLogger("uvicorn.error")

_PERCORSO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "release.json")
_cache = None
_modificato = None


def _leggi():
    """Il contenuto di release.json, riletto solo quando il file cambia."""
    global _cache, _modificato
    try:
        quando = os.path.getmtime(_PERCORSO)
    except OSError:
        return None #File assente: l'app semplicemente non mostra nessun avviso
    if _cache is not None and quando == _modificato:
        return _cache
    try:
        with open(_PERCORSO, "r", encoding="utf-8") as f:
            dati = json.load(f)
    except (OSError, ValueError) as e:
        log.warning("release.json non leggibile: %s", e)
        return None
    if not isinstance(dati, dict) or not dati.get("version"):
        log.warning("release.json senza versione: avviso di aggiornamento disattivato")
        return None
    _cache, _modificato = dati, quando
    return _cache


def info(lang=i18n.DEFAULT_LANG):
    """
    {"version", "url", "notes"} nella lingua richiesta, o None se il file manca o è
    rovinato. Non solleva mai: un errore qui non deve impedire l'avvio dell'app.
    """
    dati = _leggi()
    if dati is None:
        return None
    lingua = i18n.normalize(lang)
    url = dati.get("url") or {}
    note = dati.get("notes") or {}
    return {
        "version": str(dati["version"]),
        "url": url.get(lingua) or url.get(i18n.DEFAULT_LANG) or "https://discountsearcher.it/",
        "notes": [str(n) for n in (note.get(lingua) or note.get(i18n.DEFAULT_LANG) or [])][:10],
    }
