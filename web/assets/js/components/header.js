/**
 * Header del sito.
 *
 * Viene montato dentro l'elemento [data-ds-header] presente in ogni pagina.
 * Header e footer sono gli unici blocchi generati da JavaScript: il contenuto
 * vero di ogni pagina resta scritto nell'HTML, così resta leggibile dai motori
 * di ricerca anche senza eseguire script.
 */

import { MAIN_NAV } from '../services/content.js';
import { icon, logoMark } from './icons.js';
import { currentPage } from '../services/utils.js';
import { OTHER_LANG, otherLangUrl, t, url } from '../services/i18n.js';

/** Una voce è attiva se il file corrente compare fra i suoi `match`. */
function isActive(item, page) {
  return item.match.includes(page);
}

function navLink(item, page, className) {
  const active = isActive(item, page) ? ' aria-current="page"' : '';
  return `<a class="${className}" href="${item.href}"${active}>${item.label}</a>`;
}

export function mountHeader() {
  const host = document.querySelector('[data-ds-header]');
  if (!host) return;

  const page = currentPage();

  host.className = 'ds-header';
  host.innerHTML = `
    <div class="ds-container ds-container--wide ds-header__inner">
      <a class="ds-logo" href="${url('home')}" aria-label="${t('header.logoAria')}">
        ${logoMark()}
        <span class="ds-logo__text">
          <span class="ds-logo__name">Discount Searcher</span>
          <span class="ds-logo__sub">${t('header.tagline')}</span>
        </span>
      </a>

      <nav class="ds-nav" aria-label="${t('header.nav')}">
        ${MAIN_NAV.map((i) => navLink(i, page, 'ds-nav__link')).join('')}
      </nav>

      <div class="ds-header__actions">
        <!-- Selettore di lingua: porta alla stessa pagina nell'altra lingua (services/i18n.js) -->
        <a class="ds-lang" href="${otherLangUrl()}" hreflang="${OTHER_LANG}" lang="${OTHER_LANG}"
           aria-label="${t('header.languageAria')}">${t('header.language')}</a>
        <a class="ds-btn ds-btn--primary ds-btn--sm" href="${url('home', '#download')}">
          ${icon('download', { size: 16, className: 'ds-btn__icon' })}
          <span>${t('header.download')}</span>
        </a>
        <button class="ds-burger" type="button"
                aria-expanded="false"
                aria-controls="ds-mobile-nav"
                aria-label="${t('header.menuOpen')}">
          <span class="ds-burger__box"><span></span><span></span></span>
        </button>
      </div>
    </div>
  `;

  //Il pannello mobile va inserito DOPO l'header e non dentro: il
  //backdrop-filter dell'header farebbe da contenitore al position:fixed del
  //pannello, ritagliandolo all'altezza dell'header stesso.
  const panel = document.createElement('div');
  panel.className = 'ds-mobile-nav';
  panel.id = 'ds-mobile-nav';
  panel.hidden = true;
  panel.innerHTML = `
    <nav aria-label="${t('header.navMobile')}">
      ${MAIN_NAV.map((i) => navLink(i, page, 'ds-mobile-nav__link')).join('')}
    </nav>
    <div class="ds-mobile-nav__actions">
      <a class="ds-btn ds-btn--primary ds-btn--block" href="${url('home', '#download')}">
        ${icon('download', { size: 17, className: 'ds-btn__icon' })}
        <span>${t('header.downloadLong')}</span>
      </a>
      <a class="ds-btn ds-btn--secondary ds-btn--block" href="${url('ticketNew')}">
        ${icon('ticket', { size: 17, className: 'ds-btn__icon' })}
        <span>${t('header.openTicket')}</span>
      </a>
      <a class="ds-btn ds-btn--ghost ds-btn--block" href="${otherLangUrl()}" hreflang="${OTHER_LANG}"
         lang="${OTHER_LANG}">${t('header.language')}</a>
    </div>`;
  host.after(panel);

  setupScrollState(host);
  setupMobileNav(host, panel);
}

/** Il bordo sotto l'header compare solo dopo qualche pixel di scroll. */
function setupScrollState(host) {
  const update = () => host.classList.toggle('is-stuck', window.scrollY > 8);
  update();
  window.addEventListener('scroll', update, { passive: true });
}

function setupMobileNav(host, panel) {
  const burger = host.querySelector('.ds-burger');
  if (!burger || !panel) return;

  //Il pannello parte con l'attributo hidden per non essere raggiungibile da
  //tastiera quando è chiuso; lo togliamo prima dell'animazione di apertura.
  const open = () => {
    panel.hidden = false;
    //Un frame di attesa: senza, il browser applica insieme "hidden via" e la
    //classe, e la transizione non parte perché non c'è uno stato iniziale.
    requestAnimationFrame(() => panel.classList.add('is-open'));
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', t('header.menuClose'));
    document.body.classList.add('is-locked');
  };

  const close = () => {
    panel.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', t('header.menuOpen'));
    document.body.classList.remove('is-locked');
    //Aspettiamo la fine della transizione prima di rinascondere il pannello,
    //altrimenti sparirebbe di colpo invece di dissolversi.
    window.setTimeout(() => { if (!panel.classList.contains('is-open')) panel.hidden = true; }, 240);
  };

  const toggle = () => (burger.getAttribute('aria-expanded') === 'true' ? close() : open());

  burger.addEventListener('click', toggle);

  //Un link toccato nel menu deve anche chiudere il menu
  panel.addEventListener('click', (e) => {
    if (e.target.closest('a')) close();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') {
      close();
      burger.focus();
    }
  });

  //Se si torna a schermo largo con il menu aperto, il pannello va chiuso:
  //altrimenti resterebbe un overlay invisibile che blocca lo scroll.
  window.matchMedia('(min-width: 901px)').addEventListener('change', (e) => {
    if (e.matches) close();
  });
}
