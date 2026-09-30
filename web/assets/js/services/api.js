/**
 * Client del backend di Discount Searcher.
 *
 * Contiene SOLO endpoint che esistono davvero nel server FastAPI del
 * repository (cartella api/, file api/main.py). Nessun indirizzo è inventato:
 * se una funzionalità non è nel server, qui non compare.
 *
 * Il sito lo usa per l'accesso (pagina accedi.html) e per i ticket di
 * assistenza (services/tickets.js). Le pagine non chiamano mai fetch
 * direttamente: passano sempre da qui.
 *
 * CORS: il server accetta chiamate dal browser solo dai siti elencati nella
 * sua variabile CORS_ORIGINS (vedi api/main.py). Un sito non elencato riceve
 * un errore di rete, anche con il server acceso e funzionante.
 */

import { API_BASE_URL } from './config.js';
import { LANG, t } from './i18n.js';

/** Errore applicativo: il server ha risposto, ma con un esito negativo. */
export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === 'string' ? detail : t('api.requestFailed'));
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/** Errore di rete: il server non è stato raggiunto affatto (o CORS blocca). */
export class NetworkError extends Error {
  constructor(cause) {
    super(t('api.networkError'));
    this.name = 'NetworkError';
    this.cause = cause;
  }
}

/**
 * Esegue una richiesta al backend.
 *
 * @param {string} path      percorso dell'endpoint, es. "/health"
 * @param {object} [options] method, body (oggetto, serializzato in JSON),
 *                           token (di sessione), signal (AbortSignal)
 */
async function request(path, options = {}) {
  const { method = 'GET', body, token, signal } = options;

  //Accept-Language: il server risponde (e manda le email) nella lingua della pagina
  const headers = { Accept: 'application/json', 'Accept-Language': LANG };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  //Lo stesso schema usato dall'app desktop (api_client.py): token di sessione
  //verificato lato server ad ogni richiesta, non un JWT autofirmato.
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      signal,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (err) {
    //fetch fallisce così sia per assenza di rete sia per un'origine non
    //presente in CORS_ORIGINS: da qui non è possibile distinguere i due casi,
    //quindi il messaggio resta generico.
    throw new NetworkError(err);
  }

  //204 e simili non hanno corpo: tentare di leggerlo come JSON darebbe errore.
  const payload = response.status === 204 ? null : await response.json().catch(() => null);

  if (!response.ok) {
    //Manutenzione iniziata mentre la pagina era già aperta: lo si dice subito a tutto
    //il sito (components/maintenance.js mostra l'avviso), oltre all'errore normale.
    if (response.status === 503 && payload?.detail?.error === 'maintenance') {
      window.dispatchEvent(new CustomEvent(MAINTENANCE_EVENT, { detail: payload.detail.message }));
    }
    throw new ApiError(response.status, payload?.detail ?? payload ?? response.statusText);
  }
  return payload;
}

/** Evento lanciato quando il server risponde che è in manutenzione. */
export const MAINTENANCE_EVENT = 'ds:maintenance';

/* -------------------------------------------------------------------------
   Endpoint pubblici (nessuna autenticazione)
   ------------------------------------------------------------------------- */

/** GET /health — verifica che il server risponda e raggiunga il database. */
export const health = (signal) => request('/health', { signal });

/** GET /status — {maintenance, message}: il team sta aggiornando il servizio? */
export const status = (signal) => request('/status', { signal });

/** POST /register — crea un account non ancora verificato e invia il codice. */
export const register = (data) => request('/register', { method: 'POST', body: data });

/** POST /verify-email — attiva l'account con il codice a 6 cifre. */
export const verifyEmail = (data) => request('/verify-email', { method: 'POST', body: data });

/** POST /resend-code — genera e invia un nuovo codice di verifica. */
export const resendCode = (data) => request('/resend-code', { method: 'POST', body: data });

/** POST /login — restituisce il token di sessione. Lo usa l'app; il sito usa siteLogin. */
export const login = (data) => request('/login', { method: 'POST', body: data });

/**
 * POST /site-login — accesso al sito, primo passaggio: con la password giusta il
 * server manda un codice via email e restituisce {challenge, email_hint, email_sent, minutes}.
 */
export const siteLogin = (data) => request('/site-login', { method: 'POST', body: data });

/** POST /site-login/verify — secondo passaggio: {challenge, code} → token di sessione. */
export const siteLoginVerify = (data) => request('/site-login/verify', { method: 'POST', body: data });

/** POST /site-login/resend — un codice nuovo per la stessa richiesta: {challenge}. */
export const siteLoginResend = (data) => request('/site-login/resend', { method: 'POST', body: data });

/** POST /forgot-password — invia il codice per reimpostare la password. */
export const forgotPassword = (data) => request('/forgot-password', { method: 'POST', body: data });

/** POST /reset-password — imposta la nuova password con il codice ricevuto. */
export const resetPassword = (data) => request('/reset-password', { method: 'POST', body: data });

/* -------------------------------------------------------------------------
   Endpoint protetti (richiedono il token di sessione)
   ------------------------------------------------------------------------- */

/** GET /me — dati dell'utente collegato al token. */
export const me = (token) => request('/me', { token });

/** PATCH /me — aggiorna username/email/password (serve la password attuale). */
export const updateProfile = (token, data) => request('/me', { method: 'PATCH', token, body: data });

/** GET /sessions — dispositivi attualmente collegati all'account. */
export const sessions = (token) => request('/sessions', { token });

/** POST /sessions/{id}/revoke — disconnette un dispositivo specifico. */
export const revokeSession = (token, id) =>
  request(`/sessions/${encodeURIComponent(id)}/revoke`, { method: 'POST', token });

/** POST /logout — revoca la sessione corrente. */
export const logout = (token) => request('/logout', { method: 'POST', token });

/** GET /history — ultimi giochi aperti dall'utente. */
export const history = (token, limit = 10) =>
  request(`/history?limit=${encodeURIComponent(limit)}`, { token });

/** POST /history — registra un gioco come visitato. */
export const addHistory = (token, data) => request('/history', { method: 'POST', token, body: data });

/* -------------------------------------------------------------------------
   Ticket di assistenza (api/tickets.py) — tutti protetti
   ------------------------------------------------------------------------- */

/** GET /tickets — i ticket dell'utente, dal più recentemente aggiornato. */
export const listTickets = (token) => request('/tickets', { token });

/** GET /tickets/{id} — un ticket con la sua conversazione. */
export const getTicket = (token, id) => request(`/tickets/${encodeURIComponent(id)}`, { token });

/** POST /tickets — apre un ticket: {subject, category, description, extra, attachments?}. */
export const createTicket = (token, data) => request('/tickets', { method: 'POST', token, body: data });

/** POST /tickets/{id}/messages — risposta dell'utente: {body}. */
export const replyToTicket = (token, id, body) =>
  request(`/tickets/${encodeURIComponent(id)}/messages`, { method: 'POST', token, body: { body } });

/* -------------------------------------------------------------------------
   Area staff (api/staff.py) — solo per gli account elencati in STAFF_ACCOUNTS.
   Per tutti gli altri il server risponde 404.
   ------------------------------------------------------------------------- */

/** GET /staff/me — {name} se l'account è dello staff. */
export const staffMe = (token) => request('/staff/me', { token });

/** GET /staff/tickets — tutti i ticket, con nome utente ed email di chi li ha aperti. */
export const staffListTickets = (token) => request('/staff/tickets', { token });

/** GET /staff/tickets/{id} — un ticket qualsiasi con la sua conversazione. */
export const staffGetTicket = (token, id) => request(`/staff/tickets/${encodeURIComponent(id)}`, { token });

/** POST /staff/tickets/{id}/messages — risposta del team: {body, status?}. */
export const staffReply = (token, id, body, status) =>
  request(`/staff/tickets/${encodeURIComponent(id)}/messages`, {
    method: 'POST', token, body: status ? { body, status } : { body },
  });

/** PATCH /staff/tickets/{id} — cambia solo lo stato: {status}. */
export const staffSetStatus = (token, id, status) =>
  request(`/staff/tickets/${encodeURIComponent(id)}`, { method: 'PATCH', token, body: { status } });
