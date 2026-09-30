/**
 * Accordion accessibile, usato dalle domande frequenti.
 *
 * Costruito su <button aria-expanded> + pannello con id collegato: uno screen
 * reader annuncia correttamente "espanso/compresso" e la navigazione da
 * tastiera funziona senza codice aggiuntivo (è un vero bottone).
 *
 * Non si usa <details>/<summary> perché l'apertura andrebbe animata con
 * accorgimenti aggiuntivi e non permette di tenere aperta una sola voce.
 */

import { escapeHtml } from '../services/utils.js';

let uid = 0;

/**
 * Genera il markup di un accordion.
 *
 * @param {Array<{q: string, a: string, id?: string}>} items
 *        `a` è HTML già formattato (paragrafi, elenchi) scritto da noi;
 *        `q` viene comunque messo in sicurezza.
 * @param {{single?: boolean}} [opts] `single`: una sola voce aperta per volta.
 */
export function accordionMarkup(items, opts = {}) {
  const group = `ds-acc-${++uid}`;
  const single = opts.single !== false;

  const rows = items
    .map((item, i) => {
      const id = item.id || `${group}-${i}`;
      return `
        <div class="ds-accordion__item" data-faq-item data-faq-id="${escapeHtml(id)}">
          <h3>
            <button class="ds-accordion__trigger" type="button"
                    id="${id}-trigger"
                    aria-expanded="false"
                    aria-controls="${id}-panel">
              <span>${escapeHtml(item.q)}</span>
              <span class="ds-accordion__sign" aria-hidden="true"></span>
            </button>
          </h3>
          <div class="ds-accordion__panel" id="${id}-panel" role="region"
               aria-labelledby="${id}-trigger">
            <div><div class="ds-accordion__body">${item.a}</div></div>
          </div>
        </div>`;
    })
    .join('');

  return `<div class="ds-accordion" data-accordion${single ? ' data-single' : ''}>${rows}</div>`;
}

/** Attiva il comportamento su tutti gli accordion presenti in `root`. */
export function initAccordions(root = document) {
  root.querySelectorAll('[data-accordion]').forEach((acc) => {
    if (acc.dataset.ready === 'true') return; //Evita doppi ascoltatori se richiamato
    acc.dataset.ready = 'true';

    acc.addEventListener('click', (e) => {
      const trigger = e.target.closest('.ds-accordion__trigger');
      if (!trigger || !acc.contains(trigger)) return;

      const isOpen = trigger.getAttribute('aria-expanded') === 'true';

      if (acc.hasAttribute('data-single') && !isOpen) {
        acc.querySelectorAll('.ds-accordion__trigger[aria-expanded="true"]')
          .forEach((other) => setOpen(other, false));
      }
      setOpen(trigger, !isOpen);
    });
  });
}

function setOpen(trigger, open) {
  trigger.setAttribute('aria-expanded', String(open));
  const panel = document.getElementById(trigger.getAttribute('aria-controls'));
  if (panel) panel.classList.toggle('is-open', open);
}

/** Apre una voce specifica e la porta in vista (usato dai link con #ancora). */
export function openAccordionItem(id) {
  const trigger = document.getElementById(`${id}-trigger`);
  if (!trigger) return false;

  const acc = trigger.closest('[data-accordion]');
  if (acc && acc.hasAttribute('data-single')) {
    acc.querySelectorAll('.ds-accordion__trigger[aria-expanded="true"]')
      .forEach((other) => setOpen(other, false));
  }
  setOpen(trigger, true);
  trigger.scrollIntoView({ block: 'center', behavior: 'smooth' });
  trigger.focus({ preventScroll: true });
  return true;
}
