/**
 * Avvio comune a tutte le pagine.
 *
 * Ogni pagina carica un solo modulo (assets/js/pages/<pagina>.js), che chiama
 * boot() e poi fa il proprio lavoro. Così le parti condivise — header, footer,
 * navigazione dell'assistenza, animazioni — sono inizializzate sempre allo
 * stesso modo e in un solo punto.
 */

import { mountHeader } from './components/header.js';
import { mountFooter } from './components/footer.js';
import { mountSubnav } from './components/subnav.js';
import { mountLangBanner } from './components/lang-banner.js';
import { checkMaintenance } from './components/maintenance.js';
import { initReveal } from './components/reveal.js';
import { initAccordions } from './components/accordion.js';
import { icon } from './components/icons.js';

/**
 * Riempie gli elementi <span data-icon="nome"> scritti nell'HTML.
 * Le icone sono decorative: il testo accanto resta nell'HTML e porta il
 * significato, quindi senza JavaScript la pagina resta comprensibile.
 */
export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    if (el.dataset.iconReady) return;
    el.innerHTML = icon(el.dataset.icon, { size: Number(el.dataset.iconSize) || 24 });
    el.dataset.iconReady = 'true';
  });
}

export function boot() {
  mountLangBanner();
  mountHeader();
  mountSubnav();
  mountFooter();
  hydrateIcons();
  initAccordions();
  //Le rivelazioni vanno avviate per ultime: devono trovare nel DOM anche
  //gli elementi appena generati dagli altri componenti.
  initReveal();
  //In parallelo al resto: la pagina si mostra subito, e se il server risponde che
  //c'è un aggiornamento in corso l'avviso la copre.
  checkMaintenance();
}
