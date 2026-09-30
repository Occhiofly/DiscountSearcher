/**
 * Pagina di una categoria dell'assistenza: assistenza-categoria.html?c=<id>
 * Mostra gli articoli della categoria, un indice laterale e le altre categorie.
 */

import { boot } from '../app.js';
import { CATEGORIES, findCategory } from '../services/content.js';
import { icon } from '../components/icons.js';
import { stateBlock } from '../components/ticket-ui.js';
import { escapeHtml, queryParam } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const id = queryParam('c');
const category = findCategory(id);
const host = document.querySelector('[data-category]');
const crumb = document.querySelector('[data-crumb-current]');

function renderNotFound() {
  document.title = t('category.notFoundTitleTag');
  if (crumb) crumb.textContent = t('category.notFoundTitle');
  host.innerHTML = stateBlock({
    kind: 'error',
    iconName: 'help',
    title: t('category.notFoundTitle'),
    text: t('category.notFoundText'),
    actions: `<a class="ds-btn ds-btn--primary" href="${url('support')}">${t('category.backToSupport')}</a>`,
  });
}

function render() {
  document.title = t('category.docTitle', { title: category.title });
  if (crumb) crumb.textContent = category.title;

  const others = CATEGORIES.filter((c) => c.id !== category.id);

  host.innerHTML = `
    <header class="ds-stack ds-stack--4" style="margin-bottom:var(--ds-7)">
      <span class="ds-icon-box ds-icon-box--lg">${icon(category.icon)}</span>
      <h1 id="cat-title">${escapeHtml(category.title)}</h1>
      <p class="ds-lead">${escapeHtml(category.summary)}</p>
    </header>

    <div class="ds-ticket-layout">
      <div>
        ${category.articles.map((a) => `
          <article class="ds-article" id="${a.id}" aria-labelledby="${a.id}-t">
            <h2 class="ds-article__title" id="${a.id}-t">${escapeHtml(a.title)}</h2>
            <div class="ds-article__body">${a.body}</div>
          </article>`).join('')}

        <div class="ds-panel ds-stack ds-stack--4" style="margin-top:var(--ds-7)">
          <h2 style="font-size:var(--ds-fs-h3)">${t('category.noAnswer')}</h2>
          <p class="ds-card__text">${t('category.ticketPrefilled', { title: escapeHtml(category.title) })}</p>
          <div class="ds-row">
            <a class="ds-btn ds-btn--primary" href="${url('ticketNew', `?c=${category.id}`)}">
              ${icon('ticket', { size: 17, className: 'ds-btn__icon' })}<span>${t('category.openTicket')}</span>
            </a>
            <a class="ds-btn ds-btn--ghost" href="${url('faq')}">${t('category.faq')}</a>
          </div>
        </div>
      </div>

      <aside class="ds-ticket-layout__side ds-stack ds-stack--6" aria-label="${t('category.nav')}">
        <nav class="ds-toc" aria-label="${t('category.onThisPage')}">
          <span class="ds-toc__title">${t('category.onThisPage')}</span>
          ${category.articles.map((a) => `<a class="ds-toc__link" href="#${a.id}">${escapeHtml(a.title)}</a>`).join('')}
        </nav>
        <nav class="ds-toc" aria-label="${t('category.otherCategories')}">
          <span class="ds-toc__title">${t('category.otherCategories')}</span>
          ${others.map((c) => `<a class="ds-toc__link" href="${url('category', `?c=${c.id}`)}">${escapeHtml(c.title)}</a>`).join('')}
        </nav>
      </aside>
    </div>`;

  //L'ancora (#articolo) arriva prima che l'articolo esista nel DOM, quindi il
  //browser non può scorrere da solo: lo facciamo noi una volta generato.
  if (window.location.hash) {
    const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (target) requestAnimationFrame(() => target.scrollIntoView());
  }
}

if (host) {
  if (category) render(); else renderNotFound();
}
boot();
