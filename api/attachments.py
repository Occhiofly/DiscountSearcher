"""
Allegati dei ticket: quelli dell'assistenza (es. uno screenshot dell'errore) e
le candidature di "Lavora con noi".

I file NON vengono salvati sul server né nel database: arrivano insieme al
ticket, vengono controllati qui e spediti come allegati nell'email allo staff.
Nel ticket resta solo l'elenco dei nomi e delle dimensioni.

Arrivano da persone sconosciute, quindi il controllo è rigido:
  - al massimo MAX_FILES file, MAX_FILE_BYTES l'uno e MAX_TOTAL_BYTES in tutto;
  - solo PDF e immagini (PNG, JPEG, GIF, WEBP): niente archivi o eseguibili;
  - il tipo si verifica dai primi byte del file, non dal nome né da quello che
    dichiara il browser: un "cv.pdf" che in realtà è un programma viene rifiutato;
  - il nome viene ripulito (niente percorsi o caratteri strani) e l'estensione
    viene sempre rimessa quella giusta per il tipo.
"""
import base64
import binascii
import re
from dataclasses import dataclass

import i18n

MAX_FILES = 3
MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 10 * 1024 * 1024
#Lunghezza massima del testo base64 di un file da MAX_FILE_BYTES (4 caratteri ogni 3 byte)
MAX_BASE64_CHARS = -(-MAX_FILE_BYTES // 3) * 4

#Tipo -> (estensioni accettate, la prima è quella usata se manca; controllo dei primi byte)
ALLOWED_TYPES = {
    "application/pdf": ((".pdf",), lambda b: b.startswith(b"%PDF-")),
    "image/png": ((".png",), lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/jpeg": ((".jpg", ".jpeg"), lambda b: b.startswith(b"\xff\xd8\xff")),
    "image/gif": ((".gif",), lambda b: b[:6] in (b"GIF87a", b"GIF89a")),
    "image/webp": ((".webp",), lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
}


class AttachmentError(ValueError):
    """
    Allegato rifiutato. Porta con sé la chiave del messaggio (i18n.py) e i valori
    da inserirci: chi la cattura la traduce nella lingua di chi ha fatto la richiesta.
    """

    def __init__(self, key, **values):
        self.key = key
        self.values = values
        super().__init__(i18n.t(key, i18n.DEFAULT_LANG, **values))

    def message(self, lang):
        return i18n.t(self.key, lang, **self.values)


@dataclass(frozen=True)
class Attachment:
    name: str
    content_type: str
    data: bytes

    @property
    def size_label(self):
        return format_size(len(self.data))


def format_size(n):
    """Dimensione leggibile, uguale a quella del sito: "508 byte", "310 KB", "2,1 MB"."""
    if n < 1024:
        return f"{n} byte"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB".replace(".", ",")


def clean_name(name, content_type):
    """
    Nome sicuro da usare nell'email: senza cartelle, caratteri di controllo o
    simboli che i sistemi operativi non accettano, e con l'estensione giusta.
    """
    extensions = ALLOWED_TYPES[content_type][0]
    base = re.split(r"[\\/]", name)[-1]                   #"C:\cartella\cv.pdf" -> "cv.pdf"
    base = re.sub(r'[\x00-\x1f\x7f<>:"|?*]', "", base)
    base = re.sub(r"\s+", " ", base).strip()
    stem, dot, ext = base.rpartition(".")
    ext = f".{ext.lower()}" if dot else ""
    if ext not in extensions:
        stem, ext = base, extensions[0]                   #estensione assente o sbagliata: la rimettiamo noi
    stem = stem.strip(" .")[:80] or "allegato"
    return stem + ext


def decode_all(items):
    """
    Controlla e decodifica gli allegati della richiesta (modelli TicketAttachment).
    Restituisce una lista di Attachment o solleva AttachmentError.
    """
    if len(items) > MAX_FILES:
        raise AttachmentError("attachment_too_many", limit=MAX_FILES)

    result, total = [], 0
    for item in items:
        try:
            data = base64.b64decode(item.data, validate=True)
        except (binascii.Error, ValueError):
            raise AttachmentError("attachment_broken", name=item.name)
        if not data:
            raise AttachmentError("attachment_empty", name=item.name)
        if len(data) > MAX_FILE_BYTES:
            raise AttachmentError("attachment_too_big", name=item.name, limit=format_size(MAX_FILE_BYTES))
        if not ALLOWED_TYPES[item.content_type][1](data):
            raise AttachmentError("attachment_bad_type", name=item.name)
        total += len(data)
        result.append(Attachment(clean_name(item.name, item.content_type), item.content_type, data))

    if total > MAX_TOTAL_BYTES:
        raise AttachmentError("attachment_total_too_big", limit=format_size(MAX_TOTAL_BYTES))
    return result


def summary_line(attachments, lang=i18n.DEFAULT_LANG):
    """Riga aggiunta al primo messaggio del ticket, così la persona sa cosa ha inviato."""
    names = " · ".join(f"{a.name} ({a.size_label})" for a in attachments)
    return i18n.t("attachment_summary", lang, files=names)
