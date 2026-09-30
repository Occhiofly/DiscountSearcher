/**
 * Sessione dell'utente sul sito.
 *
 * Dopo il login il server restituisce un token di sessione (lo stesso tipo
 * usato dall'app desktop), che qui conserviamo nel localStorage del browser
 * per restare collegati fra una pagina e l'altra.
 *
 * Sicurezza: il localStorage è leggibile da qualsiasi script della pagina.
 * Per questo il sito non carica script di terze parti e mette in sicurezza
 * (escapeHtml) ogni testo scritto dagli utenti prima di mostrarlo. Il token
 * resta comunque revocabile dal server: "Esci" lo annulla davvero.
 */

import * as api from './api.js';
import { url } from './i18n.js';

const KEY = 'ds_session';

/** {token, username} se l'utente ha effettuato l'accesso, altrimenti null. */
export function getSession() {
  try {
    const session = JSON.parse(localStorage.getItem(KEY));
    return session && typeof session.token === 'string' ? session : null;
  } catch {
    //localStorage può non essere disponibile (es. navigazione privata restrittiva)
    return null;
  }
}

/** Evento emesso quando la sessione cambia: la barra dell'account si aggiorna da sola. */
export const SESSION_EVENT = 'ds:session-change';

export function saveSession({ token, username }) {
  localStorage.setItem(KEY, JSON.stringify({ token, username }));
  window.dispatchEvent(new Event(SESSION_EVENT));
}

export function clearSession() {
  try { localStorage.removeItem(KEY); } catch { /* niente da fare */ }
  window.dispatchEvent(new Event(SESSION_EVENT));
}

/** Esce: annulla la sessione anche sul server, e comunque la toglie dal browser. */
export async function logout() {
  const session = getSession();
  clearSession();
  if (session) {
    try { await api.logout(session.token); } catch { /* token già scaduto o server irraggiungibile */ }
  }
}

/**
 * Indirizzo della pagina di accesso che, dopo il login, riporta alla pagina
 * corrente (o a quella indicata).
 */
export function loginUrl(next) {
  const here = (window.location.pathname.split('/').pop() || 'index.html') + window.location.search;
  return `${url('login')}?next=${encodeURIComponent(next || here)}`;
}

/**
 * Dove tornare dopo il login. Accetta solo pagine di questo sito (es.
 * "ticket-lista.html" o "ticket-dettaglio?id=DS-1001"): un parametro come
 * "https://sito-malevolo.example" verrebbe altrimenti usato per portare
 * l'utente altrove subito dopo che ha inserito la password.
 */
export function safeNext(value, fallback = url('ticketList')) {
  if (!value || !/^[a-z0-9-]+(\.html)?(\?[\w\-.=&%]*)?$/i.test(value)) return fallback;
  return value;
}
