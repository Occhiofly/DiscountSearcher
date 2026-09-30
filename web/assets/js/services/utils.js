/**
 * Piccole funzioni di servizio condivise da più pagine.
 * Niente logica di prodotto qui: solo utilità generiche.
 */

/**
 * Lingua per date e orari. Si legge dall'attributo lang della pagina, non da
 * services/i18n.js: quel modulo importa questo, e importarsi a vicenda
 * lascerebbe uno dei due a metà caricamento.
 */
const LOCALE = document.documentElement.lang === 'en' ? 'en-GB' : 'it-IT';
const JUST_NOW = document.documentElement.lang === 'en' ? 'just now' : 'poco fa';

/**
 * Nome del file HTML attualmente aperto, sempre nella forma "assistenza.html".
 *
 * Su Netlify la stessa pagina è raggiungibile sia come /assistenza.html sia
 * come /assistenza (la funzione "Pretty URLs" riscrive anche i link dell'HTML
 * nella seconda forma). Senza normalizzare, su /assistenza il menu non
 * riconoscerebbe la pagina e non evidenzierebbe la voce attiva.
 */
export function currentPage() {
  const last = decodeURIComponent(window.location.pathname.split('/').pop());
  //Aprendo la cartella ("/" o ".../web/") il nome file è vuoto: è la home.
  if (last === '' || last === 'index') return 'index.html';
  return last.includes('.') ? last : `${last}.html`;
}

/** Legge un parametro dalla query string dell'URL. */
export function queryParam(name, fallback = null) {
  const value = new URLSearchParams(window.location.search).get(name);
  return value === null || value === '' ? fallback : value;
}

/**
 * Rende sicuro un testo prima di inserirlo in un template HTML.
 *
 * Qualsiasi contenuto che non abbiamo scritto noi (il testo di un ticket, una
 * risposta dell'operatore, un termine cercato) passa da qui: senza, un utente
 * potrebbe scrivere del markup nel proprio ticket e vederlo eseguito dalla
 * pagina.
 */
export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** Data leggibile, es. "14 set 2026" oppure "14 Sep 2026". */
export function formatDate(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(LOCALE, { day: '2-digit', month: 'short', year: 'numeric' });
}

/** Data e ora leggibili, es. "14 set 2026, 15:32". */
export function formatDateTime(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString(LOCALE, {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

/** Distanza dal presente in forma breve, es. "2 giorni fa" o "2 days ago". */
export function timeAgo(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '—';

  const seconds = Math.round((Date.now() - d.getTime()) / 1000);
  if (seconds < 45) return JUST_NOW;

  //[soglia in secondi, unità, divisore] — la prima soglia superata decide
  //l'unità di misura. Le parole le mette il browser, nella lingua della pagina.
  const steps = [
    [60, 'second', 1],
    [3600, 'minute', 60],
    [86400, 'hour', 3600],
    [604800, 'day', 86400],
    [2629800, 'week', 604800],
    [31557600, 'month', 2629800],
  ];

  const relative = new Intl.RelativeTimeFormat(LOCALE, { numeric: 'always' });
  for (const [limit, unit, divisor] of steps) {
    if (seconds < limit) return relative.format(-Math.floor(seconds / divisor), unit);
  }
  return formatDate(d);
}

/**
 * Ritarda l'esecuzione finché non passa `wait` ms dall'ultima chiamata.
 * Serve per la ricerca mentre si digita: senza, filtreremmo la lista ad ogni
 * singolo tasto premuto.
 */
export function debounce(fn, wait = 200) {
  let timer;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), wait);
  };
}

/**
 * Normalizza un testo per la ricerca: minuscolo e senza accenti, così
 * cercando "pero" si trova anche "però" e viceversa.
 *
 * normalize('NFD') separa la lettera dal suo accento, e la sostituzione
 * elimina i segni diacritici rimasti (intervallo ̀-ͯ).
 */
export function normalize(text) {
  return String(text ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .trim();
}

/** Sostituisce il contenuto di un elemento, se esiste. */
export function render(selectorOrEl, html) {
  const el = typeof selectorOrEl === 'string' ? document.querySelector(selectorOrEl) : selectorOrEl;
  if (el) el.innerHTML = html;
  return el;
}

/** Attesa non bloccante, usata per simulare la latenza nei dati dimostrativi. */
export function delay(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
