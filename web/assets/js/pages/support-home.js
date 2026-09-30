/**
 * Pagina iniziale del Centro assistenza.
 * Ricerca istantanea su articoli e domande frequenti, categorie, argomenti
 * popolari, anteprima delle FAQ e ticket recenti.
 */

import { boot } from '../app.js';
import { CATEGORIES, POPULAR_TOPICS, allArticles, FAQ_GROUPS, allFaq } from '../services/content.js';
import { accordionMarkup } from '../components/accordion.js';
import { icon } from '../components/icons.js';
import { statusBadge, categoryLabel, skeletonRows, stateBlock } from '../components/ticket-ui.js';
import { listTickets, isLoggedIn } from '../services/tickets.js';
import { loginUrl } from '../services/session.js';
import { debounce, escapeHtml, normalize, timeAgo } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

/* ---------------------------------------------------------------------------
   Ricerca
   --------------------------------------------------------------------------- */

//Indice costruito una volta: articoli e FAQ con un testo unico su cui cercare.
const INDEX = [
  ...allArticles().map((a) => ({
    title: a.title,
    href: a.href,
    kind: a.categoryTitle,
    haystack: normalize(`${a.title} ${a.categoryTitle} ${a.body.replace(/<[^>]+>/g, ' ')}`),
  })),
  ...allFaq().map((f) => ({
    title: f.q,
    href: url('faq', `#${f.id}`),
    kind: t('support.faqTitle'),
    haystack: normalize(`${f.q} ${f.tags.join(' ')} ${f.a.replace(/<[^>]+>/g, ' ')}`),
  })),
];

/**
 * Punteggio semplice: ogni parola cercata deve comparire; una corrispondenza
 * nel titolo vale più di una nel testo. Sufficiente per poche decine di voci.
 */
function search(query) {
  const words = normalize(query).split(/\s+/).filter((w) => w.length > 1);
  if (!words.length) return [];
  return INDEX
    .filter((item) => words.every((w) => item.haystack.includes(w)))
    .map((item) => ({
      ...item,
      score: words.reduce((s, w) => s + (normalize(item.title).includes(w) ? 3 : 1), 0),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 8);
}

function initSearch() {
  const form = document.getElementById('sup-search-form');
  const input = document.getElementById('sup-search');
  const box = document.getElementById('sup-results');
  const status = document.getElementById('sup-results-status');
  if (!form || !input || !box) return;

  const renderResults = () => {
    const q = input.value.trim();
    if (q.length < 2) {
      box.hidden = true;
      box.innerHTML = '';
      status.textContent = '';
      return;
    }

    const results = search(q);
    box.hidden = false;

    if (!results.length) {
      box.innerHTML = `
        <div class="ds-sup-results__list">
          <div class="ds-sup-result" style="flex-direction:column;align-items:flex-start;gap:4px">
            <strong>${t('support.noResultFor', { q: escapeHtml(q) })}</strong>
            <span class="ds-muted" style="font-size:var(--ds-fs-xs)">
              ${t('support.tryOther', { url: url('ticketNew') })}
            </span>
          </div>
        </div>`;
      status.textContent = t('support.noResults');
      return;
    }

    box.innerHTML = `
      <ul class="ds-sup-results__list" aria-label="${t('support.searchResults')}">
        ${results.map((r) => `
          <li style="display:contents">
            <a class="ds-sup-result" href="${r.href}">
              <span>${escapeHtml(r.title)}</span>
              <span class="ds-sup-result__cat">${escapeHtml(r.kind)}</span>
            </a>
          </li>`).join('')}
      </ul>`;
    status.textContent = t(results.length === 1 ? 'support.countOne' : 'support.countMany', { n: results.length });
  };

  input.addEventListener('input', debounce(renderResults, 140));

  //Invio: porta direttamente al primo risultato, come ci si aspetta da un campo
  //di ricerca. Senza risultati, lascia visibile il messaggio "nessun risultato".
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    renderResults();
    const first = box.querySelector('a.ds-sup-result');
    if (first) first.focus();
  });

  //Esc svuota la ricerca
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { input.value = ''; renderResults(); }
  });
}

/* ---------------------------------------------------------------------------
   Contenuti generati dai dati
   --------------------------------------------------------------------------- */

function mountTopics() {
  const host = document.querySelector('[data-topics]');
  if (!host) return;
  host.innerHTML = POPULAR_TOPICS
    .map((topic) => `<li><a class="ds-chip" href="${topic.href}" style="display:inline-block;text-decoration:none">${escapeHtml(topic.label)}</a></li>`)
    .join('');
}

function mountCategories() {
  const host = document.querySelector('[data-categories]');
  if (!host) return;
  host.innerHTML = CATEGORIES.map((c) => `
    <li style="display:flex" data-reveal data-reveal-step="40">
      <a class="ds-card ds-card--interactive" style="width:100%" href="${url('category', `?c=${c.id}`)}">
        <span class="ds-icon-box">${icon(c.icon)}</span>
        <span class="ds-card__title">${escapeHtml(c.title)}</span>
        <span class="ds-card__text">${escapeHtml(c.summary)}</span>
        <span class="ds-meta" style="margin-top:auto">
          <span class="ds-meta__item">${t(c.articles.length === 1 ? 'support.article' : 'support.articles', { n: c.articles.length })}</span>
        </span>
      </a>
    </li>`).join('');
}

function mountFaqPreview() {
  const host = document.querySelector('[data-faq-preview]');
  if (!host) return;
  //Una domanda per gruppo più le più richieste: anteprima breve, il resto è in faq.html
  const pick = ['faq-cos-e', 'faq-negozi', 'faq-verifica', 'faq-piu-computer', 'faq-password-dimenticata', 'faq-contatto'];
  const items = FAQ_GROUPS.flatMap((g) => g.items).filter((i) => pick.includes(i.id));
  //Id con prefisso: la stessa domanda esiste anche in faq.html, e gli id
  //nel documento devono essere unici.
  host.innerHTML = accordionMarkup(items.map((i) => ({ ...i, id: `home-${i.id}` })));
}

async function mountRecentTickets() {
  const host = document.querySelector('[data-recent-tickets]');
  if (!host) return;

  //Pannello piccolo: un invito compatto invece del blocco grande delle pagine ticket
  const signIn = (text) => `
    <div class="ds-stack ds-stack--3">
      <p class="ds-card__text">${escapeHtml(text)}</p>
      <div><a class="ds-btn ds-btn--secondary ds-btn--sm" href="${loginUrl(url('ticketList'))}">
        ${icon('key', { size: 15, className: 'ds-btn__icon' })}<span>${t('state.signIn')}</span></a></div>
    </div>`;

  if (!isLoggedIn()) {
    host.innerHTML = signIn(t('support.recentLoginHint'));
    return;
  }

  host.innerHTML = skeletonRows(2);
  try {
    const tickets = (await listTickets()).slice(0, 3);
    if (!tickets.length) {
      host.innerHTML = stateBlock({
        title: t('support.noTicketsTitle'),
        text: t('support.noTicketsText'),
      });
      return;
    }
    host.innerHTML = `
      <ul class="ds-tickets">
        ${tickets.map((ticket) => `
          <li>
            <a class="ds-ticket" href="${url('ticketDetail', `?id=${encodeURIComponent(ticket.id)}`)}">
              <span class="ds-ticket__main">
                <span class="ds-ticket__id">${escapeHtml(ticket.id)} · ${escapeHtml(categoryLabel(ticket.category))}</span>
                <span class="ds-ticket__subject">${escapeHtml(ticket.subject)}</span>
              </span>
              <span class="ds-ticket__side">
                ${statusBadge(ticket.status)}
                <span class="ds-ticket__when">${t('list.updated', { when: timeAgo(ticket.updatedAt) })}</span>
              </span>
            </a>
          </li>`).join('')}
      </ul>`;
  } catch (err) {
    host.innerHTML = err.kind === 'auth'
      ? signIn(err.message)
      : `<p class="ds-card__text" role="alert">${escapeHtml(err.message)}</p>`;
  }
}

mountTopics();
mountCategories();
mountFaqPreview();
initSearch();
boot();
mountRecentTickets();
