"""
Indirizzo del server API a cui l'app desktop si collega.

Durante lo sviluppo/test in locale, lascia quello di default (il server che
fai girare tu con `uvicorn main:app` dentro la cartella api/). Quando l'API
sarà ospitata su un vero server (Render, Railway, un VPS, ecc.), cambia
questo valore con l'indirizzo pubblico di quel server — è l'UNICA riga da
modificare per far puntare l'app al server giusto.

Non contiene nessuna credenziale: può restare tracciato su git senza problemi.
"""

API_BASE_URL = "https://discountsearcher.onrender.com"
