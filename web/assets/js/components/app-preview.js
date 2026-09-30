/**
 * Ricostruzione dell'interfaccia dell'applicazione desktop.
 *
 * NON è uno screenshot. Nel repository non esistono catture dello schermo,
 * quindi l'interfaccia è ridisegnata in HTML/CSS seguendo il codice reale
 * (main.py, metodo _create_main_menu): stessa struttura (barra laterale
 * "Cronologia" al 20%, area principale all'80%), stesse etichette, stessi
 * menu (Store, Genere, Sconto), stesso formato delle righe risultato
 * ("Titolo — $prezzo (-sconto%)", in dollari come li fornisce CheapShark) e stessi
 * colori (#1e1e1e, #2b2b2b, #5B5EA6).
 *
 * Titoli e prezzi sono DI ESEMPIO e inventati di proposito: usare giochi reali
 * con prezzi inventati farebbe credere a offerte che non esistono.
 */

import { icon } from './icons.js';
import { escapeHtml } from '../services/utils.js';
import { t } from '../services/i18n.js';

/* Dati di esempio: titoli fittizi, prezzi fittizi. */
const SAMPLE = {
  Steam: [
    { title: 'Hollow Keep',        genre: 'RPG',       price: '4.99',  cut: 75 },
    { title: 'Iron Meridian',      genre: 'Strategy',  price: '11.99', cut: 40 },
    { title: 'Ashen Crown',        genre: 'RPG',       price: '8.49',  cut: 66 },
    { title: 'Neon Drift',         genre: 'Action',    price: '3.74',  cut: 25 },
    { title: 'Tidebreaker',        genre: 'Adventure', price: '7.99',  cut: 60 },
    { title: 'Stellar Outpost',    genre: 'RPG',       price: '14.99', cut: 50 },
  ],
  GOG: [
    { title: 'Ashen Crown',        genre: 'RPG',       price: '7.99',  cut: 68 },
    { title: 'Lantern Vale',       genre: 'RPG',       price: '5.59',  cut: 72 },
    { title: 'Stellar Outpost',    genre: 'RPG',       price: '13.49', cut: 55 },
  ],
};

const HISTORY = ['Tidebreaker', 'Neon Drift', 'Iron Meridian'];

/**
 * Stati della finestra, uno per ogni passo della vetrina.
 * `active` indica quale controllo il passo sta mettendo in evidenza.
 */
export const PREVIEW_STATES = {
  search: {
    query: '',
    store: 'Steam', genre: t('preview.all'), discount: t('preview.all'),
    active: ['search'],
    filter: () => true,
  },
  filter: {
    query: '',
    store: 'Steam', genre: 'RPG', discount: '50%+',
    active: ['genre', 'discount'],
    filter: (g) => g.genre === 'RPG' && g.cut >= 50,
  },
  compare: {
    query: '',
    store: 'GOG', genre: 'RPG', discount: '50%+',
    active: ['store'],
    filter: (g) => g.genre === 'RPG' && g.cut >= 50,
  },
  open: {
    query: '',
    store: 'GOG', genre: 'RPG', discount: '50%+',
    active: [],
    highlight: 'Lantern Vale',
    history: ['Lantern Vale', ...HISTORY],
    filter: (g) => g.genre === 'RPG' && g.cut >= 50,
  },
};

function filterBox(key, label, value, active) {
  return `
    <div class="ds-app-filter${active.includes(key) ? ' is-active' : ''}">
      <span class="ds-app-filter__label">${label}</span>
      <span class="ds-app-filter__value">${escapeHtml(value)}</span>
    </div>`;
}

function rows(state) {
  const list = (SAMPLE[state.store] || []).filter(state.filter);
  if (!list.length) {
    return `<div class="ds-app-empty">${t('preview.empty')}</div>`;
  }
  return list
    .map((g, i) => `
      <div class="ds-app-row${state.highlight === g.title ? ' is-highlight' : ''}"
           style="animation-delay:${i * 45}ms">
        <span class="ds-app-row__title">${escapeHtml(g.title)}
          <span class="ds-app-row__price">— $${g.price}</span>
          <span class="ds-app-row__cut">(-${g.cut}%)</span>
        </span>
        <span class="ds-app-row__link">${t('preview.link')}</span>
      </div>`)
    .join('');
}

/** Contenuto interno della finestra per uno stato. */
function bodyMarkup(state) {
  const history = state.history || HISTORY;
  return `
    <div class="ds-app-side">
      <div class="ds-app-side__title">${t('preview.history')}</div>
      <div class="ds-app-side__list">
        ${history.map((title) => `
          <div class="ds-app-side__item"><span>${escapeHtml(title)}</span><span>${t('preview.sideLink')}</span></div>`).join('')}
      </div>
      <div class="ds-app-side__user">${t('preview.user')}</div>
      <div class="ds-app-side__logout">${t('preview.signOut')}</div>
    </div>

    <div class="ds-app-main">
      <div class="ds-app-searchrow">
        <span class="ds-app-btn">${t('preview.search')}</span>
        <span class="ds-app-input${state.query ? '' : ' ds-app-input--placeholder'}">
          ${state.query ? escapeHtml(state.query) : t('preview.searchPlaceholder')}
        </span>
      </div>

      <div class="ds-app-filters">
        ${filterBox('store', t('preview.store'), state.store, state.active)}
        ${filterBox('genre', t('preview.genre'), state.genre, state.active)}
        ${filterBox('discount', t('preview.discount'), state.discount, state.active)}
      </div>

      <div class="ds-app-results">${rows(state)}</div>

      <div class="ds-app-credit">${t('preview.credits')}</div>
    </div>`;
}

/**
 * Markup completo della finestra.
 * @param {keyof PREVIEW_STATES} stateName
 * @param {{label?: string}} [opts] etichetta accessibile della figura
 */
export function appPreviewMarkup(stateName = 'filter', opts = {}) {
  const state = PREVIEW_STATES[stateName] || PREVIEW_STATES.filter;
  return `
    <figure class="ds-appframe">
      <div class="ds-window" role="img"
           aria-label="${escapeHtml(opts.label || t('preview.alt'))}">
        <div class="ds-window__bar" aria-hidden="true">
          <span class="ds-window__title">${icon('search', { size: 14 })} Discount Searcher</span>
          <span class="ds-window__controls"><span>─</span><span>▢</span><span>✕</span></span>
        </div>
        <div class="ds-window__body" aria-hidden="true" data-preview-body>${bodyMarkup(state)}</div>
      </div>
      <figcaption class="ds-appframe__note">
        ${icon('info', { size: 13 })}
        ${t('preview.note')}
      </figcaption>
    </figure>`;
}

/** Aggiorna il contenuto di una finestra già montata a un nuovo stato. */
export function setPreviewState(root, stateName) {
  const body = root.querySelector('[data-preview-body]');
  const state = PREVIEW_STATES[stateName];
  if (body && state) body.innerHTML = bodyMarkup(state);
}
