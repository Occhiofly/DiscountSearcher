#Importazioni
import requests
import datetime

#ID degli store sull api di CheapShark
STORES = {
    "Steam": 1,
    "Epic Games": 25,
    "GOG": 7,
    "Humble Store": 11
}

#Genere di videogioco
GENRES = ["Tutti", "Action", "RPG", "FPS", "Horror", "Adventure", "Strategy"]

#Percentuale di sconto
DISCOUNT = ["Tutti", "10%+", "25%+", "50%+", "75%+"]

#Cache dei generi già richiesti a Steam in questa sessione dell'app: se lo stesso gioco
#viene incontrato di nuovo (stessa ricerca o una successiva), evitiamo di richiederlo
#un'altra volta a Steam — è questo il motivo principale della lentezza col filtro Genere attivo.
_genre_cache = {}

#CheapShark chiede uno User-Agent descrittivo con un contatto, per non bloccare
#per sbaglio chi usa la loro API: "MyApp/1.0 (contact@example.com)".
from version import APP_VERSION

USER_AGENT = f"DiscountSearcher/{APP_VERSION} (+https://discountsearcher.it; searcherdiscuont@gmail.com)"


def get_deals(store_id, days=7, max_results=50):
    """
    Chiede all'API di CheapShark le offerte di un negozio.

    Parametri:
        store_id    → il negozio scelto dall'utente
        days        → quanti giorni indietro cercare (default 7)
        max_results → quanti risultati massimi restituire (default 50)

    Restituisce una lista di dizionari, uno per ogni offerta trovata.
    """
    
    #Calcolo da quando cercare offerte
    time_window = datetime.datetime.now() - datetime.timedelta(days=days)

    try:
        response = requests.get(
            "https://www.cheapshark.com/api/1.0/deals",
            params={
                "storeID": store_id,
                "onSale": 1,
                "pageSize": 100,
                "sortBy": "recent"
            },
            headers={"User-Agent": USER_AGENT},
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Errore di rete: {e}")
    
    #Conversione di dati json in una lista python
    deals = response.json()

    #Qui é dove si trova la lista python
    recent_deals = []

    #Ciclo con Debug
    for deal in deals:
        try:
            start_time = datetime.datetime.fromtimestamp(int(deal["lastChange"]))
        except (ValueError, OSError):
            continue

        if start_time >= time_window:
            recent_deals.append({
                "title": deal.get("title", "N/A"), #Titolo del videgioco
                "normalPrice": float(deal.get("normalPrice", 0)), #Prezzo originale del gioco
                "salePrice": float(deal.get("salePrice", 0)), #Applicazione dello sconto al prezzo originale
                "savings": float(deal.get("savings", 0)), #La percentuale di sconto del gioco
                "lastChange": start_time.strftime("%d/%m/%Y"), #Conversione in data formato italiano
                "dealID": deal.get("dealID", ""), #ID del gioco che servira per il link del gioco
                "steamAppID": deal.get("steamAppID", "") #ID Steam per richiedere il genere
            })
    return recent_deals[:max_results] #Limitazione dei risulatati

def get_game_genres(steam_app_id):
    """
    Chiede a Steam il genere di un gioco usando il suo steamAppID.
    Restituisce una lista di generi (es. ["Action", "Adventure"]) o lista vuota se non trovato.
    Il risultato viene tenuto in cache (per tutta la durata dell'app), così lo stesso gioco
    non viene richiesto a Steam più di una volta per sessione.
    """
    if not steam_app_id:
        return [] #Nessuno Steam ID associato al gioco: impossibile chiedere il genere, niente richiesta di rete

    if steam_app_id in _genre_cache: #Già richiesto in questa sessione: risparmiamo la chiamata di rete
        return _genre_cache[steam_app_id]

    try:
        response = requests.get(
            "https://store.steampowered.com/api/appdetails",
            params={"appids": steam_app_id, "l": "english"},
            headers={"User-Agent": USER_AGENT},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        #Steam a volte risponde con null invece che con un oggetto vuoto per ID non validi:
        #(data or {}) evita che il '.get' successivo faccia crashare l'app in quel caso.
        app_data = (data or {}).get(str(steam_app_id), {})
        if not app_data.get("success"):
            result = []
        else:
            genres = app_data["data"].get("genres", [])
            result = [g["description"] for g in genres] #Lista di nomi genere
    except (requests.exceptions.RequestException, KeyError, ValueError, AttributeError, TypeError):
        result = [] #In caso di errore, nessun genere

    _genre_cache[steam_app_id] = result #Salviamo il risultato (anche vuoto) per non richiederlo di nuovo
    return result