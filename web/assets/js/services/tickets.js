/**
 * Servizio ticket di assistenza, collegato al backend (api/tickets.py).
 *
 * Le pagine chiamano soltanto le funzioni esportate qui e ricevono dati già
 * nel formato dell'interfaccia (camelCase, "Tu" per i messaggi dell'utente).
 * Ogni errore arriva come TicketsError con un `kind` che la pagina usa per
 * scegliere cosa mostrare:
 *
 *   auth        non autenticato o sessione scaduta → invito ad accedere
 *   notfound    ticket inesistente o di un altro utente
 *   closed      ticket chiuso, non accetta risposte
 *   limit       troppi ticket aperti nelle ultime 24 ore
 *   validation  dati rifiutati dal server (per gli allegati, con il motivo preciso)
 *   network     server irraggiungibile (o in avvio)
 *   server      qualsiasi altro errore del server
 *
 * Le risposte dello staff arrivano via email e il server le aggiunge ai ticket
 * da solo: qui non serve nulla di speciale per mostrarle.
 */

import * as api from './api.js';
import { ApiError, NetworkError } from './api.js';
import { clearSession, getSession } from './session.js';
import { t } from './i18n.js';

/** Stati possibili di un ticket, con etichetta, classe del badge e spiegazione. */
export const TICKET_STATUS = {
  open: { label: t('ticket.status.open'), badge: 'ds-badge--open', canReply: true, text: t('ticket.status.openText') },
  progress: { label: t('ticket.status.progress'), badge: 'ds-badge--progress', canReply: true, text: t('ticket.status.progressText') },
  waiting: { label: t('ticket.status.waiting'), badge: 'ds-badge--waiting', canReply: true, text: t('ticket.status.waitingText') },
  resolved: { label: t('ticket.status.resolved'), badge: 'ds-badge--resolved', canReply: true, text: t('ticket.status.resolvedText') },
  closed: { label: t('ticket.status.closed'), badge: 'ds-badge--closed', canReply: false, text: t('ticket.status.closedText') },
};

export class TicketsError extends Error {
  constructor(kind, message) {
    super(message);
    this.name = 'TicketsError';
    this.kind = kind;
  }
}

/** True se nel browser c'è una sessione (non garantisce che sia ancora valida). */
export const isLoggedIn = () => getSession() !== null;

export const toMessage = (m) => ({
  id: m.id,
  role: m.author_role,
  author: m.author_role === 'user' ? t('detail.you') : m.author_name,
  at: m.created_at,
  body: m.body,
});

export const toTicket = (t) => ({
  id: t.id,
  subject: t.subject,
  category: t.category,
  status: t.status,
  createdAt: t.created_at,
  updatedAt: t.updated_at,
  extra: t.extra ?? null,
  messages: (t.messages || []).map(toMessage),
});

/**
 * Esegue una chiamata autenticata e traduce ogni errore in un TicketsError.
 * Esportata anche per l'area staff (services/staff.js), che usa le stesse regole.
 */
export async function authorized(call) {
  const session = getSession();
  if (!session) throw new TicketsError('auth', t('ticket.err.needLogin'));

  try {
    return await call(session.token);
  } catch (err) {
    if (err instanceof NetworkError) {
      throw new TicketsError('network', t('ticket.err.network'));
    }
    if (!(err instanceof ApiError)) {
      throw new TicketsError('server', t('ticket.err.server'));
    }
    switch (err.status) {
      case 401:
      case 403:
        //Token scaduto o revocato (es. password cambiata da un altro dispositivo),
        //oppure aperto senza il codice via email: il server spiega quale dei due
        clearSession();
        throw new TicketsError('auth', err.detail?.error === 'site_login_required'
          ? err.detail.message
          : t('ticket.err.sessionExpired'));
      case 404:
        throw new TicketsError('notfound', t('ticket.err.notFound'));
      case 409:
        throw new TicketsError('closed', err.message);
      case 400:
      case 413:
        //Allegati rifiutati: il server spiega quale file e perché
        throw new TicketsError('validation', err.message);
      case 422:
        throw new TicketsError('validation', t('ticket.err.validation'));
      case 429:
        throw new TicketsError('limit', err.message);
      case 503:
        //Es. allegati non recapitati al team: il messaggio del server dice cosa fare
        throw new TicketsError('server', typeof err.detail === 'string'
          ? err.message
          : t('ticket.err.unavailable'));
      default:
        throw new TicketsError('server', t('ticket.err.generic'));
    }
  }
}

/** Elenco dei ticket dell'utente, dal più recentemente aggiornato. */
export const listTickets = () =>
  authorized(async (token) => (await api.listTickets(token)).tickets.map(toTicket));

/** Un ticket con la sua conversazione. */
export const getTicket = (id) =>
  authorized(async (token) => toTicket(await api.getTicket(token, id)));

/**
 * Apre un ticket a partire dai dati del modulo.
 * `attachments` (solo candidature): [{name, content_type, data (base64)}].
 */
export const createTicket = (draft) =>
  authorized(async (token) => toTicket(await api.createTicket(token, {
    subject: draft.subject,
    category: draft.category,
    description: draft.description,
    extra: draft.extra || null,
    ...(draft.attachments?.length ? { attachments: draft.attachments } : {}),
  })));

/** Aggiunge una risposta dell'utente alla conversazione. */
export const replyToTicket = (id, body) =>
  authorized(async (token) => toMessage(await api.replyToTicket(token, id, body)));
