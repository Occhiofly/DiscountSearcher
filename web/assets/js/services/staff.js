/**
 * Area staff: il team vede tutti i ticket, risponde e cambia lo stato dal sito
 * (server: api/staff.py). Stessi errori dei ticket normali (TicketsError), con
 * una differenza: per chi non è dello staff il server risponde 404, quindi
 * staffName() restituisce null invece di lanciare un errore.
 */

import * as api from './api.js';
import { authorized, toMessage, toTicket, TicketsError } from './tickets.js';

/** Un ticket visto dallo staff: in più, chi lo ha aperto. I messaggi dell'utente portano il suo nome. */
const toStaffTicket = (raw) => {
  const ticket = toTicket(raw);
  ticket.username = raw.username;
  ticket.email = raw.email;
  ticket.messages = (raw.messages || []).map((m) => ({
    ...toMessage(m),
    author: m.author_role === 'user' ? raw.username : m.author_name,
  }));
  return ticket;
};

/** Nome con cui firmano le risposte di questo account, o null se non è dello staff. */
export async function staffName() {
  try {
    return (await authorized((token) => api.staffMe(token))).name;
  } catch (err) {
    if (err instanceof TicketsError && err.kind === 'notfound') return null;
    throw err;
  }
}

/** Tutti i ticket, dal più recentemente aggiornato. */
export const staffListTickets = () =>
  authorized(async (token) => (await api.staffListTickets(token)).tickets.map(toStaffTicket));

/** Un ticket qualsiasi, con la conversazione. */
export const staffGetTicket = (id) =>
  authorized(async (token) => toStaffTicket(await api.staffGetTicket(token, id)));

/** Risposta del team; `status` facoltativo (senza: "In attesa di risposta"). */
export const staffReply = (id, body, status) =>
  authorized(async (token) => toMessage(await api.staffReply(token, id, body, status)));

/** Cambia solo lo stato. */
export const staffSetStatus = (id, status) =>
  authorized((token) => api.staffSetStatus(token, id, status));
