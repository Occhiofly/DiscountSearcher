/**
 * Pagina "Lavora con noi".
 * Il testo fisso è nell'HTML; qui si montano le parti che vengono dai dati
 * (assets/js/data/jobs.js): i passi della selezione e i ruoli aperti.
 */

import { boot } from '../app.js';
import { PROCESS, ROLES } from '../services/content.js';
import { mountTeam } from '../components/team.js';
import { icon } from '../components/icons.js';
import { escapeHtml } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

function mountProcess() {
  const host = document.querySelector('[data-process]');
  if (!host) return;
  host.innerHTML = PROCESS.map((step, i) => `
    <li class="ds-flow__item" data-reveal data-reveal-step="70">
      <span class="ds-flow__num">0${i + 1}</span>
      <h3 class="ds-flow__title">${escapeHtml(step.title)}</h3>
      <p class="ds-flow__text">${escapeHtml(step.text)}</p>
    </li>`).join('');
}

function mountRoles() {
  const host = document.querySelector('[data-roles]');
  if (!host) return;

  //Nessun ruolo aperto: lo diciamo, invece di lasciare un vuoto inspiegabile.
  if (!ROLES.length) {
    host.innerHTML = `
      <li>
        <div class="ds-panel ds-stack ds-stack--3">
          <h3 class="ds-card__title">${t('jobs.noRolesTitle')}</h3>
          <p class="ds-card__text">${t('jobs.noRolesText')}</p>
        </div>
      </li>`;
    return;
  }

  host.innerHTML = ROLES.map((role) => `
    <li class="ds-panel ds-stack ds-stack--4" data-reveal data-reveal-step="80">
      <span class="ds-icon-box">${icon(role.icon)}</span>
      <div class="ds-stack ds-stack--2">
        <h3 class="ds-card__title" id="ruolo-${role.id}">${escapeHtml(role.title)}</h3>
        <p class="ds-card__text">${escapeHtml(role.summary)}</p>
      </div>

      <div class="ds-stack ds-stack--2">
        <span class="ds-eyebrow ds-eyebrow--plain">${t('jobs.whatYouDo')}</span>
        <ul class="ds-stack ds-stack--2">
          ${role.does.map((d) => `<li class="ds-feature__li">${icon('check', { size: 14 })}${escapeHtml(d)}</li>`).join('')}
        </ul>
      </div>

      <div class="ds-stack ds-stack--2">
        <span class="ds-eyebrow ds-eyebrow--plain">${t('jobs.whatYouSend')}</span>
        <ul class="ds-stack ds-stack--2">
          ${role.bring.map((b) => `<li class="ds-feature__li">${icon('check', { size: 14 })}${escapeHtml(b)}</li>`).join('')}
        </ul>
      </div>

      <p class="ds-hint" style="margin-top:auto"><strong>${t('apply.trial')}</strong> ${escapeHtml(role.trial)}</p>

      <a class="ds-btn ds-btn--secondary" href="${url('apply', `?r=${role.id}`)}"
         aria-describedby="ruolo-${role.id}">
        ${icon('send', { size: 16, className: 'ds-btn__icon' })}<span>${t('jobs.apply')}</span>
      </a>
    </li>`).join('');
}

mountProcess();
mountRoles();
mountTeam();
boot();
