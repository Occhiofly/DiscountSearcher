/**
 * "I miei ticket": elenco con filtro per stato e ricerca per oggetto/ID.
 * Gestisce tutti gli stati: caricamento, errore (con riprova), nessun ticket,
 * nessun risultato per i filtri scelti.
 */

import { boot } from '../app.js';
import { isLoggedIn, listTickets, TICKET_STATUS } from '../services/tickets.js';
import {
  categoryLabel, loginRequiredBlock, skeletonRows, stateBlock, statusBadge, ticketErrorBlock,
} from '../components/ticket-ui.js';
import { debounce, escapeHtml, formatDate, formatDateTime, normalize, timeAgo } from '../services/utils.js';
import { t, url } from '../services/i18n.js';
import { staffName } from '../services/staff.js';

const host = document.querySelector('[data-ticket-list]');
const chipsHost = document.querySelector('[data-status-filter]');
const toolbar = document.querySelector('.ds-toolbar');
const input = document.getElementById('ticket-search');
const status = document.getElementById('ticket-status');

let tickets = [];
let activeStatus = 'all';

function counts() {
  const c = { all: tickets.length };
  tickets.forEach((ticket) => { c[ticket.status] = (c[ticket.status] || 0) + 1; });
  return c;
}

function renderChips() {
  const c = counts();
  const options = [['all', t('list.all')], ...Object.entries(TICKET_STATUS).map(([k, v]) => [k, v.label])];
  chipsHost.innerHTML = options.map(([key, label]) => `
    <button class="ds-chip" type="button" data-status="${key}" aria-pressed="${key === activeStatus}">
      ${escapeHtml(label)} <span class="ds-mono ds-faint">${c[key] || 0}</span>
    </button>`).join('');
}

function row(ticket) {
  return `
    <li>
      <a class="ds-ticket" href="${url('ticketDetail', `?id=${encodeURIComponent(ticket.id)}`)}">
        <span class="ds-ticket__main">
          <span class="ds-ticket__id">${escapeHtml(ticket.id)}</span>
          <span class="ds-ticket__subject">${escapeHtml(ticket.subject)}</span>
          <span class="ds-meta">
            <span class="ds-meta__item"><span class="ds-meta__key">${t('list.category')}</span><span class="ds-meta__val">${escapeHtml(categoryLabel(ticket.category))}</span></span>
            <span class="ds-meta__item"><span class="ds-meta__key">${t('list.created')}</span><span class="ds-meta__val">${formatDate(ticket.createdAt)}</span></span>
          </span>
        </span>
        <span class="ds-ticket__side">
          ${statusBadge(ticket.status)}
          <span class="ds-ticket__when" title="${formatDateTime(ticket.updatedAt)}">${t('list.updated', { when: timeAgo(ticket.updatedAt) })}</span>
        </span>
      </a>
    </li>`;
}

function renderList() {
  //Nessun ticket in assoluto: stato vuoto "di benvenuto", non un errore
  if (!tickets.length) {
    host.innerHTML = stateBlock({
      title: t('list.emptyTitle'),
      text: t('list.emptyText'),
      actions: `<a class="ds-btn ds-btn--primary" href="${url('ticketNew')}">${t('list.firstTicket')}</a>`,
    });
    status.textContent = t('list.noTickets');
    return;
  }

  const q = normalize(input.value);
  const list = tickets.filter((ticket) =>
    (activeStatus === 'all' || ticket.status === activeStatus) &&
    (!q || normalize(`${ticket.id} ${ticket.subject}`).includes(q)));

  if (!list.length) {
    host.innerHTML = stateBlock({
      iconName: 'search',
      title: t('list.noMatchTitle'),
      text: t('list.noMatchText'),
      actions: `<button class="ds-btn ds-btn--secondary" type="button" data-reset>${t('list.clearFilters')}</button>`,
    });
    status.textContent = t('list.noMatchTitle');
    return;
  }

  host.innerHTML = `<ul class="ds-tickets">${list.map(row).join('')}</ul>`;
  status.textContent = t(list.length === 1 ? 'list.countOne' : 'list.countMany', { n: list.length });
}

async function load() {
  //Senza accesso non ha senso mostrare ricerca e filtri su un elenco che non c'è
  if (!isLoggedIn()) {
    toolbar.hidden = true;
    host.innerHTML = loginRequiredBlock();
    status.textContent = t('list.loginRequired');
    return;
  }

  toolbar.hidden = false;
  host.innerHTML = skeletonRows(4);
  host.setAttribute('aria-busy', 'true');
  try {
    tickets = await listTickets();
    renderChips();
    renderList();
  } catch (err) {
    toolbar.hidden = err.kind === 'auth';
    host.innerHTML = ticketErrorBlock(err, { title: t('list.loadError') });
    status.textContent = err.message;
  } finally {
    host.removeAttribute('aria-busy');
  }
}

chipsHost.addEventListener('click', (e) => {
  const chip = e.target.closest('[data-status]');
  if (!chip) return;
  activeStatus = chip.dataset.status;
  renderChips();
  renderList();
});

host.addEventListener('click', (e) => {
  if (e.target.closest('[data-retry]')) load();
  if (e.target.closest('[data-reset]')) {
    activeStatus = 'all';
    input.value = '';
    renderChips();
    renderList();
  }
});

input.addEventListener('input', debounce(renderList, 150));

/**
 * Per gli account dello staff: collegamento all'area staff accanto a "Nuovo ticket".
 * Per tutti gli altri il server risponde 404 e non compare niente.
 */
async function showStaffLink() {
  if (!isLoggedIn()) return;
  try {
    if (!(await staffName())) return;
  } catch { return; }
  //Cercato per attributo e non per indirizzo: Netlify, pubblicando, riscrive i
  //collegamenti togliendo ".html" (ticket-nuovo.html diventa /ticket-nuovo)
  const newBtn = document.querySelector('[data-new-ticket]');
  if (!newBtn || document.querySelector('[data-staff-link]')) return;
  //I due pulsanti affiancati a destra del titolo, in un gruppo
  const group = document.createElement('div');
  group.className = 'ds-row';
  newBtn.replaceWith(group);
  group.innerHTML = `
    <a class="ds-btn ds-btn--secondary" href="${url('staff')}" data-staff-link>
      <span>${t('staff.link')}</span>
    </a>`;
  group.append(newBtn);
}

boot();
load();
showStaffLink();
