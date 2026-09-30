/**
 * Footer del sito, montato dentro [data-ds-footer].
 *
 * Le note legali sono volutamente formulate come dichiarazioni di NON
 * affiliazione: il progetto usa API pubbliche di terzi e i marchi citati
 * appartengono ai rispettivi proprietari.
 */

import { FOOTER_NAV, SITE } from '../services/content.js';
import { t, url } from '../services/i18n.js';
import { logoMark } from './icons.js';

function column(col) {
  return `
    <div class="ds-footer__col">
      <h2 class="ds-footer__title">${col.title}</h2>
      ${col.links
        .map((l) => `<a class="ds-footer__link" href="${l.href}">${l.label}</a>`)
        .join('')}
    </div>`;
}

export function mountFooter() {
  const host = document.querySelector('[data-ds-footer]');
  if (!host) return;

  const year = new Date().getFullYear();

  host.className = 'ds-footer';
  host.innerHTML = `
    <div class="ds-container ds-container--wide">
      <div class="ds-footer__grid">
        <div class="ds-footer__col ds-footer__col--brand">
          <a class="ds-logo" href="${url('home')}">
            ${logoMark()}
            <span class="ds-logo__text">
              <span class="ds-logo__name">${SITE.name}</span>
              <span class="ds-logo__sub">${t('header.tagline')}</span>
            </span>
          </a>
          <p class="ds-card__text" style="max-width: 34ch">${SITE.description}</p>
        </div>
        ${FOOTER_NAV.map(column).join('')}
      </div>

      <div class="ds-stack ds-stack--3" style="margin-top: var(--ds-8)">
        <h2 class="ds-footer__title">${t('footer.legalTitle')}</h2>
        <p class="ds-footer__legal">${t('footer.legal1')}</p>
        <p class="ds-footer__legal">${t('footer.legal2')}</p>
      </div>

      <div class="ds-footer__bottom">
        <span>${t('footer.rights', { year, name: SITE.name })}</span>
        <span class="ds-mono">${t('footer.credits')}</span>
      </div>
    </div>
  `;
}
