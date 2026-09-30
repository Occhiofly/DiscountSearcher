/**
 * Avviso della versione nell'altra lingua.
 *
 * Il sito NON cambia lingua da solo: ogni lingua ha i suoi indirizzi e chi
 * arriva da un link deve trovare la pagina che il link prometteva. Quando però
 * la lingua del browser è l'altra, mostriamo una barra che la propone, con un
 * collegamento alla stessa pagina tradotta.
 *
 * La scelta di chiudere la barra resta nel browser di chi legge (localStorage):
 * non viene mandata da nessuna parte e non serve a riconoscere nessuno.
 */

import { LANG, OTHER_LANG, otherLangUrl, t } from '../services/i18n.js';

const KEY = 'ds_lang_banner';

/** true se fra le lingue preferite del browser c'è l'altra lingua del sito. */
function prefersOtherLanguage() {
  const preferred = navigator.languages?.length ? navigator.languages : [navigator.language || ''];
  for (const code of preferred) {
    const lang = String(code).toLowerCase().split('-')[0];
    //Decide la prima delle due che compare nell'elenco: se l'italiano viene
    //prima dell'inglese, chi legge la pagina italiana è già dove voleva essere.
    if (lang === LANG) return false;
    if (lang === OTHER_LANG) return true;
  }
  return false;
}

function dismissed() {
  try {
    return localStorage.getItem(KEY) === '1';
  } catch {
    //localStorage non disponibile (navigazione privata restrittiva): niente barra
    return true;
  }
}

/** Mostra la barra, se serve. Chiamata da boot() su ogni pagina. */
export function mountLangBanner() {
  if (!prefersOtherLanguage() || dismissed()) return;

  const bar = document.createElement('div');
  bar.className = 'ds-langbar';
  bar.lang = OTHER_LANG;
  bar.innerHTML = `
    <span>${t('lang.bannerText')}</span>
    <a class="ds-langbar__link" href="${otherLangUrl()}" hreflang="${OTHER_LANG}">${t('lang.bannerAction')}</a>
    <button class="ds-langbar__close" type="button" aria-label="${t('lang.bannerClose')}">✕</button>`;

  bar.querySelector('.ds-langbar__close').addEventListener('click', () => {
    bar.remove();
    try { localStorage.setItem(KEY, '1'); } catch { /* niente da salvare, pazienza */ }
  });

  document.body.prepend(bar);
}
