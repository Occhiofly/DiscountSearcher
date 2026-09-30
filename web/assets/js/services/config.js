/**
 * Configurazione dei servizi remoti del sito.
 *
 * Unico punto da modificare per far puntare il sito a un backend diverso —
 * stesso ruolo che api_config.py ha per l'app desktop.
 */

/**
 * Indirizzo del backend di Discount Searcher (FastAPI, cartella api/ del
 * repository). È lo stesso valore di API_BASE_URL in api_config.py.
 *
 * Il server accetta chiamate dal browser solo dai siti elencati nella sua
 * variabile CORS_ORIGINS (su Render).
 */
export const API_BASE_URL = 'https://discountsearcher.onrender.com';
