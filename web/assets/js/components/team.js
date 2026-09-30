/**
 * Elenco del team, mostrato nella home e in "Lavora con noi".
 * Una sola funzione per entrambe: aggiungendo una persona in data/team.js
 * compare in tutte e due le pagine, senza doversi ricordare della seconda.
 */

import { TEAM } from '../services/content.js';
import { escapeHtml } from '../services/utils.js';

/** Riempie l'elenco [data-team] con le persone del team. */
export function mountTeam(root = document) {
  const host = root.querySelector('[data-team]');
  if (!host) return;

  host.innerHTML = TEAM.map((m) => {
    //Senza foto mostriamo l'iniziale del nome: un segnaposto, non un'immagine finta
    const avatar = m.photo
      ? `<img class="ds-member__avatar" src="${escapeHtml(m.photo)}" alt="" width="62" height="62">`
      : `<span class="ds-member__avatar" aria-hidden="true">${escapeHtml(m.name.charAt(0))}</span>`;
    return `
      <li class="ds-member" data-reveal data-reveal-step="80">
        ${avatar}
        <div>
          <h3 class="ds-member__name">${escapeHtml(m.name)}</h3>
          <p class="ds-member__role">${escapeHtml(m.role)}</p>
        </div>
        <p class="ds-member__scope">${escapeHtml(m.scope)}</p>
      </li>`;
  }).join('');
}
