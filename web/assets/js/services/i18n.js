/**
 * Lingua del sito e indirizzi delle pagine.
 *
 * Il sito ha due versioni complete: l'italiano nella cartella principale e
 * l'inglese in /en/. La lingua NON si sceglie con JavaScript: è decisa
 * dall'indirizzo della pagina, e ogni pagina la dichiara nel suo tag
 * <html lang="...">. Così ogni lingua ha i suoi indirizzi, i motori di ricerca
 * le trovano entrambe e chi condivide un link condivide la lingua giusta.
 *
 * Qui dentro:
 *   LANG          la lingua della pagina aperta ("it" o "en")
 *   t(chiave)     il testo dell'interfaccia in quella lingua (i18n/ui.js)
 *   url(pagina)   l'indirizzo di una pagina del sito nella lingua corrente
 *   otherLangUrl() la stessa pagina nell'altra lingua, per il selettore
 */

import { UI } from '../i18n/ui.js';
import { currentPage } from './utils.js';

/** "en" se la pagina dichiara lang="en" (tutte quelle in /en/), altrimenti "it". */
export const LANG = document.documentElement.lang === 'en' ? 'en' : 'it';

/**
 * Testo dell'interfaccia. I segnaposto {cosi} si riempiono con
 * t('chiave', { cosi: 'valore' }).
 */
export function t(key, values) {
  const entry = UI[key];
  if (!entry) {
    //Meglio accorgersene in sviluppo che mostrare una pagina con un buco
    console.warn(`[i18n] testo mancante: "${key}"`);
    return '';
  }
  const text = entry[LANG] ?? entry.it;
  return values ? text.replace(/\{(\w+)\}/g, (_, name) => values[name] ?? '') : text;
}

/**
 * Nome del file di ogni pagina nelle due lingue. Le pagine inglesi stanno in
 * /en/ e hanno nomi inglesi: aggiungendo una pagina, va aggiunta qui.
 */
export const PAGES = {
  home:         { it: 'index.html',                en: 'index.html' },
  support:      { it: 'assistenza.html',           en: 'support.html' },
  category:     { it: 'assistenza-categoria.html', en: 'support-category.html' },
  faq:          { it: 'faq.html',                  en: 'faq.html' },
  login:        { it: 'accedi.html',               en: 'login.html' },
  register:     { it: 'registrati.html',           en: 'register.html' },
  ticketNew:    { it: 'ticket-nuovo.html',         en: 'ticket-new.html' },
  ticketList:   { it: 'ticket-lista.html',         en: 'tickets.html' },
  ticketDetail: { it: 'ticket-dettaglio.html',     en: 'ticket-detail.html' },
  jobs:         { it: 'lavora-con-noi.html',       en: 'jobs.html' },
  apply:        { it: 'candidatura.html',          en: 'apply.html' },
  privacy:      { it: 'privacy.html',              en: 'privacy.html' },
  donate:       { it: 'sostieni.html',             en: 'support-us.html' },
  staff:        { it: 'staff.html',                en: 'staff.html' },
};

/** Indirizzo di una pagina nella lingua corrente, con eventuale coda (?c=bug, #ancora). */
export function url(page, suffix = '') {
  const file = PAGES[page]?.[LANG];
  if (!file) {
    console.warn(`[i18n] pagina sconosciuta: "${page}"`);
    return '#';
  }
  return file + suffix;
}

/** Chiave della pagina aperta ("support", "faq", ...), o null se non è una del sito. */
export function currentPageKey() {
  const file = currentPage();
  return Object.keys(PAGES).find((key) => PAGES[key][LANG] === file) || null;
}

/**
 * La stessa pagina nell'altra lingua, mantenendo i parametri (per esempio
 * ?c=bug o ?id=DS-1001). Se la pagina non esiste nell'altra lingua si torna
 * alla sua pagina iniziale.
 */
export function otherLangUrl() {
  const other = LANG === 'it' ? 'en' : 'it';
  const key = currentPageKey();
  const file = key ? PAGES[key][other] : PAGES.home[other];
  //La query non si copia così com'è: viene riscritta da URLSearchParams, che
  //codifica virgolette e parentesi angolari. L'indirizzo finisce dentro un
  //attributo href scritto con innerHTML, e un parametro inventato ad arte
  //potrebbe altrimenti uscire dall'attributo.
  const params = key ? new URLSearchParams(window.location.search).toString() : '';
  //Dall'italiano si scende in /en/, dall'inglese si risale alla cartella principale
  return (other === 'en' ? `en/${file}` : `../${file}`) + (params ? `?${params}` : '');
}

/** Codice della lingua per l'attributo lang e per le intestazioni. */
export const OTHER_LANG = LANG === 'it' ? 'en' : 'it';
