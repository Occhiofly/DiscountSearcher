/**
 * Area staff: staff.html (elenco di tutti i ticket) e staff.html?id=DS-1001 (un ticket).
 *
 * Il team vede chi ha aperto il ticket, risponde e cambia lo stato. Sono le stesse
 * azioni delle risposte via email (#inlavorazione, #risolto, #chiuso), che
 * continuano a funzionare: l'utente riceve lo stesso avviso in entrambi i casi.
 *
 * Pagina in due lingue come il resto del sito (staff.html e en/staff.html): i testi
 * sono in i18n/ui.js, chiavi "staff.*".
 */

import { boot } from '../app.js';
import { isLoggedIn, TICKET_STATUS } from '../services/tickets.js';
import { staffGetTicket, staffListTickets, staffName, staffReply, staffSetStatus } from '../services/staff.js';
import {
  categoryLabel, loginRequiredBlock, skeletonRows, stateBlock, statusBadge, ticketErrorBlock,
} from '../components/ticket-ui.js';
import { icon } from '../components/icons.js';
import { debounce, escapeHtml, formatDate, formatDateTime, normalize, queryParam, timeAgo } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const MAX_REPLY = 20000;

const host = document.querySelector('[data-staff]');
const crumb = document.querySelector('[data-crumb-ticket]');
const id = queryParam('id');

//Stati selezionabili dopo una risposta: senza scelta vale "In attesa di risposta",
//come per una risposta via email senza parola chiave.
const AFTER_REPLY = ['waiting', 'progress', 'resolved', 'closed'];

//Gli stati come li legge il team: "waiting" per l'utente è "tocca a te", per lo staff
//è "tocca all'utente" (in inglese "Waiting for your reply" sarebbe sbagliato qui)
const statusLabel = (k) => (k === 'waiting' ? t('staff.statusWaiting') : TICKET_STATUS[k]?.label || k);
const badge = (k) => statusBadge(k, statusLabel(k));

const statusOptions = (keys, selected) => keys.map((k) => `
  <option value="${k}"${k === selected ? ' selected' : ''}>${escapeHtml(statusLabel(k))}</option>`).join('');

const pageHeading = (text) => `<h1 class="ds-sr-only">${escapeHtml(text)}</h1>`;

/* ---------------------------------------------------------------------------
   Elenco
   --------------------------------------------------------------------------- */

let tickets = [];
let activeStatus = 'open';

function renderListShell(name) {
  host.innerHTML = `
    <header class="ds-row" style="justify-content:space-between;align-items:flex-end;margin-bottom:var(--ds-5)">
      <div class="ds-stack ds-stack--3">
        <h1>${t('staff.title')}</h1>
        <p class="ds-muted">${t('staff.lead', { name: escapeHtml(name) })}</p>
      </div>
      <button class="ds-btn ds-btn--secondary" type="button" data-refresh>
        ${icon('refresh', { size: 17, className: 'ds-btn__icon' })}<span>${t('staff.refresh')}</span>
      </button>
    </header>
    <div class="ds-toolbar">
      <div class="ds-search" style="flex:1 1 260px;max-width:360px">
        <span class="ds-search__icon">${icon('search', { size: 19 })}</span>
        <label class="ds-sr-only" for="staff-search">${t('staff.search')}</label>
        <input class="ds-input" id="staff-search" type="search" placeholder="${t('staff.search')}" autocomplete="off">
      </div>
      <div class="ds-chips" role="group" aria-label="${t('staff.filterByStatus')}" data-status-filter></div>
    </div>
    <p class="ds-sr-only" id="staff-status" role="status" aria-live="polite"></p>
    <div data-staff-list>${skeletonRows(4)}</div>`;

  host.querySelector('#staff-search').addEventListener('input', debounce(renderRows, 150));
  host.querySelector('[data-status-filter]').addEventListener('click', (e) => {
    const chip = e.target.closest('[data-status]');
    if (!chip) return;
    activeStatus = chip.dataset.status;
    renderChips();
    renderRows();
  });
  host.querySelector('[data-refresh]').addEventListener('click', () => loadList(name));
}

function renderChips() {
  const c = { all: tickets.length };
  tickets.forEach((tk) => { c[tk.status] = (c[tk.status] || 0) + 1; });
  const options = [['all', t('list.all')], ...Object.keys(TICKET_STATUS).map((k) => [k, statusLabel(k)])];
  host.querySelector('[data-status-filter]').innerHTML = options.map(([key, label]) => `
    <button class="ds-chip" type="button" data-status="${key}" aria-pressed="${key === activeStatus}">
      ${escapeHtml(label)} <span class="ds-mono ds-faint">${c[key] || 0}</span>
    </button>`).join('');
}

function row(tk) {
  return `
    <li>
      <a class="ds-ticket" href="${url('staff', `?id=${encodeURIComponent(tk.id)}`)}">
        <span class="ds-ticket__main">
          <span class="ds-ticket__id">${escapeHtml(tk.id)}</span>
          <span class="ds-ticket__subject">${escapeHtml(tk.subject)}</span>
          <span class="ds-meta">
            <span class="ds-meta__item"><span class="ds-meta__key">${t('staff.user')}</span><span class="ds-meta__val">${escapeHtml(tk.username)}</span></span>
            <span class="ds-meta__item"><span class="ds-meta__key">${t('list.category')}</span><span class="ds-meta__val">${escapeHtml(categoryLabel(tk.category))}</span></span>
            <span class="ds-meta__item"><span class="ds-meta__key">${t('staff.opened')}</span><span class="ds-meta__val">${formatDate(tk.createdAt)}</span></span>
          </span>
        </span>
        <span class="ds-ticket__side">
          ${badge(tk.status)}
          <span class="ds-ticket__when" title="${formatDateTime(tk.updatedAt)}">${t('list.updated', { when: timeAgo(tk.updatedAt) })}</span>
        </span>
      </a>
    </li>`;
}

function renderRows() {
  const list = host.querySelector('[data-staff-list]');
  const status = host.querySelector('#staff-status');
  if (!tickets.length) {
    list.innerHTML = stateBlock({ title: t('staff.emptyTitle'), text: t('staff.emptyText') });
    status.textContent = t('staff.emptyTitle');
    return;
  }
  const q = normalize(host.querySelector('#staff-search').value);
  const shown = tickets.filter((tk) =>
    (activeStatus === 'all' || tk.status === activeStatus) &&
    (!q || normalize(`${tk.id} ${tk.subject} ${tk.username}`).includes(q)));
  if (!shown.length) {
    list.innerHTML = stateBlock({ iconName: 'search', title: t('list.noMatchTitle'), text: t('staff.noMatchText') });
    status.textContent = t('list.noMatchTitle');
    return;
  }
  list.innerHTML = `<ul class="ds-tickets">${shown.map(row).join('')}</ul>`;
  status.textContent = t(shown.length === 1 ? 'list.countOne' : 'list.countMany', { n: shown.length });
}

async function loadList(name) {
  if (!host.querySelector('[data-staff-list]')) renderListShell(name);
  const list = host.querySelector('[data-staff-list]');
  list.innerHTML = skeletonRows(4);
  try {
    tickets = await staffListTickets();
    //Se non c'è niente da fare fra gli aperti, meglio mostrare subito tutto
    if (activeStatus === 'open' && !tickets.some((tk) => tk.status === 'open')) activeStatus = 'all';
    renderChips();
    renderRows();
  } catch (err) {
    list.innerHTML = ticketErrorBlock(err, { title: t('list.loadError') });
    list.querySelector('[data-retry]')?.addEventListener('click', () => loadList(name));
  }
}

/* ---------------------------------------------------------------------------
   Dettaglio
   --------------------------------------------------------------------------- */

function message(m) {
  const staff = m.role === 'staff';
  return `
    <li class="ds-msg${staff ? ' ds-msg--staff' : ''}">
      <span class="ds-msg__avatar" aria-hidden="true">${escapeHtml((m.author || '?').charAt(0))}</span>
      <article class="ds-msg__bubble" aria-label="${t('detail.messageFrom', { author: escapeHtml(m.author) })}">
        <header class="ds-msg__head">
          <span class="ds-msg__author">${escapeHtml(m.author)}</span>
          <span class="ds-msg__role">${staff ? t('detail.teamRole') : t('staff.user')}</span>
          <time class="ds-msg__when" datetime="${escapeHtml(m.at)}" title="${formatDateTime(m.at)}">${timeAgo(m.at)}</time>
        </header>
        <p class="ds-msg__body">${escapeHtml(m.body)}</p>
      </article>
    </li>`;
}

function renderDetail(tk, name) {
  document.title = t('staff.docTitle', { id: tk.id });
  crumb.hidden = false;
  crumb.querySelector('span').textContent = tk.id;

  host.innerHTML = `
    <header class="ds-stack ds-stack--3" style="margin-bottom:var(--ds-6)">
      <div class="ds-row">
        <span class="ds-badge ds-badge--accent">${escapeHtml(tk.id)}</span>
        <span data-status-badge>${badge(tk.status)}</span>
      </div>
      <h1 style="font-size:var(--ds-fs-h2)">${escapeHtml(tk.subject)}</h1>
    </header>

    <div class="ds-ticket-layout">
      <section class="ds-stack ds-stack--5" aria-labelledby="conv-title">
        <h2 class="ds-sr-only" id="conv-title">${t('detail.thread')}</h2>
        ${tk.extra ? `
          <div class="ds-panel ds-stack ds-stack--2">
            <h3 style="font-size:1rem">${t('staff.extra')}</h3>
            <p class="ds-card__text" style="white-space:pre-line">${escapeHtml(tk.extra)}</p>
          </div>` : ''}
        <ol class="ds-thread" data-thread>${tk.messages.map(message).join('')}</ol>

        <form class="ds-panel ds-reply" id="reply-form" novalidate>
          <div class="ds-field" id="reply-field">
            <div class="ds-field-row">
              <label class="ds-label" for="reply">${t('staff.replyAs', { name: escapeHtml(name) })}</label>
              <span class="ds-counter" id="reply-counter" aria-hidden="true">0</span>
            </div>
            <textarea class="ds-textarea" id="reply" name="reply" rows="6" required
                      placeholder="${t('staff.replyPlaceholder', { user: escapeHtml(tk.username) })}" aria-describedby="reply-err"></textarea>
            <p class="ds-error" id="reply-err">${icon('alert', { size: 14 })}<span></span></p>
          </div>
          <div class="ds-field">
            <label class="ds-label" for="reply-status">${t('staff.statusAfter')}</label>
            <select class="ds-select" id="reply-status" name="status">${statusOptions(AFTER_REPLY, 'waiting')}</select>
          </div>
          <div class="ds-notice ds-notice--warn" id="reply-fail" role="alert" hidden>
            <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
            <p><strong>${t('detail.replyFailed')}</strong> <span data-msg></span></p>
          </div>
          <div class="ds-reply__actions">
            <button class="ds-btn ds-btn--primary" type="submit">
              ${icon('send', { size: 17, className: 'ds-btn__icon' })}<span>${t('detail.sendReply')}</span>
            </button>
            <span class="ds-hint">${t('staff.replyHint', { user: escapeHtml(tk.username) })}</span>
          </div>
        </form>
      </section>

      <aside class="ds-ticket-layout__side ds-stack ds-stack--4" aria-label="${t('detail.detailsTitle')}">
        <div class="ds-panel">
          <h2 style="font-size:1rem;margin-bottom:var(--ds-3)">${t('detail.detailsTitle')}</h2>
          <dl class="ds-ticket-meta">
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('staff.user')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(tk.username)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('staff.email')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0;font-size:var(--ds-fs-xs);word-break:break-all">${escapeHtml(tk.email)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.category')}</dt><dd class="ds-ticket-meta__val" style="margin:0">${escapeHtml(categoryLabel(tk.category))}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.created')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0;font-size:var(--ds-fs-xs)">${formatDateTime(tk.createdAt)}</dd></div>
            <div class="ds-ticket-meta__row"><dt class="ds-ticket-meta__key">${t('detail.updated')}</dt><dd class="ds-ticket-meta__val ds-mono" style="margin:0;font-size:var(--ds-fs-xs)" data-updated>${formatDateTime(tk.updatedAt)}</dd></div>
          </dl>
        </div>

        <form class="ds-panel ds-stack ds-stack--3" id="status-form">
          <h2 style="font-size:1rem">${t('staff.statusOnly')}</h2>
          <label class="ds-sr-only" for="only-status">${t('staff.newStatus')}</label>
          <select class="ds-select" id="only-status">${statusOptions(Object.keys(TICKET_STATUS), tk.status)}</select>
          <button class="ds-btn ds-btn--secondary" type="submit">${t('staff.saveStatus')}</button>
          <p class="ds-hint" data-status-msg role="status"></p>
        </form>

        <div class="ds-notice">
          <span class="ds-notice__icon">${icon('mail', { size: 17 })}</span>
          <p>${t('staff.emailStillWorks')}</p>
        </div>
        <a class="ds-btn ds-btn--ghost" href="${url('staff')}">
          ${icon('arrowLeft', { size: 17, className: 'ds-btn__icon' })}<span>${t('staff.allTickets')}</span>
        </a>
      </aside>
    </div>`;

  initReply(tk);
  initStatus(tk);
}

function setStatusShown(status, updatedAt) {
  host.querySelector('[data-status-badge]').innerHTML = badge(status);
  host.querySelector('#only-status').value = status;
  if (updatedAt) host.querySelector('[data-updated]').textContent = formatDateTime(updatedAt);
}

function initReply(tk) {
  const form = host.querySelector('#reply-form');
  const textarea = form.elements.reply;
  const wrap = host.querySelector('#reply-field');
  const counter = host.querySelector('#reply-counter');
  const errText = wrap.querySelector('.ds-error > span:last-child');
  const btn = form.querySelector('[type="submit"]');
  const fail = host.querySelector('#reply-fail');

  const validate = () => {
    const v = textarea.value.trim();
    const msg = !v ? t('detail.replyEmpty')
      : textarea.value.length > MAX_REPLY ? t('detail.replyTooLong', { max: MAX_REPLY }) : null;
    wrap.classList.toggle('is-invalid', Boolean(msg));
    textarea.setAttribute('aria-invalid', String(Boolean(msg)));
    errText.textContent = msg || '';
    return !msg;
  };

  textarea.addEventListener('input', () => {
    counter.textContent = String(textarea.value.length);
    if (wrap.classList.contains('is-invalid')) validate();
  });
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) form.requestSubmit();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    fail.hidden = true;
    if (!validate()) { textarea.focus(); return; }
    const status = form.elements.status.value;
    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    textarea.disabled = true;
    try {
      const msg = await staffReply(tk.id, textarea.value.trim(), status);
      host.querySelector('[data-thread]').insertAdjacentHTML('beforeend', message(msg));
      textarea.value = '';
      counter.textContent = '0';
      form.elements.status.value = 'waiting';
      setStatusShown(status, msg.at);
    } catch (err) {
      //Il testo resta nel campo: niente va perso se la sessione è scaduta
      fail.hidden = false;
      fail.querySelector('[data-msg]').textContent = err.message || t('detail.retryLater');
    } finally {
      btn.classList.remove('is-loading');
      btn.removeAttribute('aria-busy');
      textarea.disabled = false;
      textarea.focus();
    }
  });
}

function initStatus(tk) {
  const form = host.querySelector('#status-form');
  const select = host.querySelector('#only-status');
  const msg = host.querySelector('[data-status-msg]');
  const btn = form.querySelector('[type="submit"]');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    btn.classList.add('is-loading');
    msg.textContent = '';
    try {
      const updated = await staffSetStatus(tk.id, select.value);
      setStatusShown(updated.status, updated.updated_at);
      msg.textContent = t('staff.statusSaved', { status: statusLabel(updated.status), user: tk.username });
    } catch (err) {
      msg.textContent = err.message || t('staff.statusFailed');
    } finally {
      btn.classList.remove('is-loading');
    }
  });
}

async function loadDetail(name) {
  try {
    renderDetail(await staffGetTicket(id), name);
  } catch (err) {
    if (err.kind === 'notfound') {
      host.innerHTML = pageHeading(t('detail.notFoundTitle')) + stateBlock({
        kind: 'error', iconName: 'ticket', title: t('detail.notFoundTitle'),
        text: t('staff.notFoundText', { id: escapeHtml(id) }),
        actions: `<a class="ds-btn ds-btn--primary" href="${url('staff')}">${t('staff.allTickets')}</a>`,
      });
      return;
    }
    host.innerHTML = pageHeading(t('state.errorTitle')) + ticketErrorBlock(err, { title: t('detail.loadError') });
    host.querySelector('[data-retry]')?.addEventListener('click', () => loadDetail(name));
  }
}

/* ---------------------------------------------------------------------------
   Avvio
   --------------------------------------------------------------------------- */

async function start() {
  if (!isLoggedIn()) {
    //Dopo l'accesso si torna qui, anche sul ticket aperto (?id=...)
    host.innerHTML = pageHeading(t('staff.title')) + loginRequiredBlock(t('staff.loginText'));
    return;
  }
  let name;
  try {
    name = await staffName();
  } catch (err) {
    host.innerHTML = pageHeading(t('staff.title')) + ticketErrorBlock(err, { title: t('staff.checkFailed') });
    host.querySelector('[data-retry]')?.addEventListener('click', start);
    return;
  }
  if (!name) {
    host.innerHTML = pageHeading(t('staff.reservedTitle')) + stateBlock({
      iconName: 'lock', title: t('staff.reservedTitle'),
      text: t('staff.reservedText'),
      actions: `<a class="ds-btn ds-btn--primary" href="${url('ticketList')}">${t('staff.myTickets')}</a>`,
    });
    return;
  }
  if (id) loadDetail(name); else loadList(name);
}

boot();
start();
