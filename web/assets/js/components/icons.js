/**
 * Set di icone del sito.
 *
 * Ogni voce è il *contenuto* di un <svg> con viewBox 0 0 24 24, disegnato a
 * tratto (stroke) e non a riempimento: così eredita automaticamente il colore
 * del testo che lo contiene e resta nitido a qualsiasi dimensione.
 *
 * Sono SVG inline invece che file separati per un motivo pratico: un'icona
 * usata in venti punti della pagina non deve generare venti richieste di rete,
 * e deve poter cambiare colore con il tema senza trucchi tipo filtri CSS.
 *
 * Per aggiungerne una: nuova voce qui, poi `icon("nome")` dove serve.
 */

const PATHS = {
  search:    '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  filter:    '<path d="M3 5h18M6 12h12M10 19h4"/>',
  compare:   '<path d="M9 4v16M15 4v16"/><path d="M4 8h5M4 15h5M15 9h5M15 16h5"/>',
  external:  '<path d="M14 4h6v6"/><path d="M20 4 11 13"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  history:   '<path d="M3 12a9 9 0 1 0 2.6-6.4"/><path d="M3 4v4h4"/><path d="M12 8v4.5l3 1.8"/>',
  user:      '<circle cx="12" cy="8" r="3.6"/><path d="M4.8 20a7.2 7.2 0 0 1 14.4 0"/>',
  shield:    '<path d="M12 3 5 6v5.5c0 4.3 2.9 7.7 7 9.5 4.1-1.8 7-5.2 7-9.5V6z"/>',
  lock:      '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7"/>',
  mail:      '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.6 7 8.4 6 8.4-6"/>',
  devices:   '<rect x="2.5" y="5" width="13" height="10" rx="1.6"/><path d="M6 19h6"/><rect x="17" y="9" width="4.5" height="10" rx="1.4"/>',
  key:       '<circle cx="8" cy="12" r="4"/><path d="M12 12h9"/><path d="M17.5 12v3.2"/><path d="M20.5 12v2.2"/>',
  tag:       '<path d="M11.4 3.6H20v8.6l-8.2 8.2a1.6 1.6 0 0 1-2.3 0l-6.3-6.3a1.6 1.6 0 0 1 0-2.3z"/><circle cx="16.2" cy="7.8" r="1.4"/>',
  store:     '<path d="M4 9h16v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="m5 4h14l1.6 5H3.4z"/><path d="M10 20v-5h4v5"/>',
  ticket:    '<path d="M4 7.5A1.5 1.5 0 0 1 5.5 6h13A1.5 1.5 0 0 1 20 7.5V10a2 2 0 0 0 0 4v2.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 16.5V14a2 2 0 0 0 0-4z"/><path d="M13 7.5v9" stroke-dasharray="2 2.5"/>',
  chat:      '<path d="M20.5 12.6c0 3.9-3.8 7-8.5 7a9.9 9.9 0 0 1-2.8-.4L4 21l1.4-3.7a6.6 6.6 0 0 1-1.9-4.7c0-3.9 3.8-7 8.5-7s8.5 3.1 8.5 7z"/>',
  book:      '<path d="M4 5.2A1.5 1.5 0 0 1 5.5 3.7H19v16.6H5.5A1.5 1.5 0 0 1 4 18.8z"/><path d="M4 17.3h15"/>',
  bug:       '<rect x="8" y="8" width="8" height="12" rx="4"/><path d="M9.2 9.4 8 6.6M14.8 9.4 16 6.6"/><path d="M4.5 12h3.5M16 12h3.5M5 17.5 8.2 16M19 17.5 15.8 16"/>',
  help:      '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.6a2.5 2.5 0 1 1 3.3 2.4c-.6.2-.9.8-.9 1.4v.4"/><path d="M12 17h.01"/>',
  check:     '<path d="m4.5 12.5 5 5 10-11"/>',
  checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8 12.3 2.6 2.6L16 9.5"/>',
  alert:     '<path d="M12 4.5 2.8 20h18.4z"/><path d="M12 10.2v4"/><path d="M12 17.2h.01"/>',
  info:      '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.2"/><path d="M12 7.8h.01"/>',
  arrowRight:'<path d="M4.5 12h14"/><path d="m13 6.5 5.5 5.5L13 17.5"/>',
  arrowLeft: '<path d="M19.5 12h-14"/><path d="M11 6.5 5.5 12 11 17.5"/>',
  chevronDown:'<path d="m6 9.5 6 6 6-6"/>',
  download:  '<path d="M12 3.5v11"/><path d="m7.5 10.5 4.5 4.5 4.5-4.5"/><path d="M4.5 19.5h15"/>',
  send:      '<path d="M20.5 3.5 10.8 13.2"/><path d="M20.5 3.5 14.3 20.5l-3.5-7.3-7.3-3.5z"/>',
  clock:     '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.3 2"/>',
  refresh:   '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20.5 3.5V9h-5.5"/>',
  inbox:     '<path d="M3.5 13.5h4l1.5 3h6l1.5-3h4"/><path d="M5.6 5h12.8l2.1 8.5v4a1.5 1.5 0 0 1-1.5 1.5H5a1.5 1.5 0 0 1-1.5-1.5v-4z"/>',
  code:      '<path d="m8.5 8.5-4 3.5 4 3.5"/><path d="m15.5 8.5 4 3.5-4 3.5"/><path d="m13.5 5.5-3 13"/>',
  heart:     '<path d="M12 19.6 4.9 12.5a4.3 4.3 0 0 1 6.1-6.1l1 1 1-1a4.3 4.3 0 0 1 6.1 6.1z"/>',
  sparkle:   '<path d="M12 3.5 13.9 9 19.5 11l-5.6 2L12 18.5 10.1 13 4.5 11 10.1 9z"/>',
  grid:      '<rect x="3.5" y="3.5" width="7" height="7" rx="1.4"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.4"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.4"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.4"/>',
  file:      '<path d="M14 3.5H7A1.5 1.5 0 0 0 5.5 5v14A1.5 1.5 0 0 0 7 20.5h10a1.5 1.5 0 0 0 1.5-1.5V8z"/><path d="M14 3.5V8h4.5"/>',
  image:     '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="m20.5 16-5-5-9 8.5"/>',
  paperclip: '<path d="M20 11.5 12.2 19.3a4.5 4.5 0 0 1-6.4-6.4l8-8a3 3 0 0 1 4.3 4.3l-8 8a1.5 1.5 0 0 1-2.1-2.1l7.3-7.3"/>',
  windows:   '<path d="M3.5 6.2 10.5 5.2v6.3H3.5z"/><path d="M12.2 5 20.5 3.8v7.7h-8.3z"/><path d="M3.5 13.2h7v6.3L3.5 18.5z"/><path d="M12.2 13.2h8.3v7.7l-8.3-1.2z"/>',
};

/**
 * Restituisce il markup di un'icona.
 *
 * @param {string} name  nome della voce in PATHS
 * @param {{size?: number, className?: string}} [opts]
 * @returns {string} markup <svg>, o stringa vuota se il nome non esiste
 */
export function icon(name, opts = {}) {
  const d = PATHS[name];
  if (!d) {
    //Meglio un buco silenzioso che un'icona rotta a video: segnaliamo in
    //console così l'errore si vede in sviluppo senza rompere la pagina.
    console.warn(`[icons] icona sconosciuta: "${name}"`);
    return '';
  }
  const size = opts.size || 24;
  const cls = opts.className ? ` class="${opts.className}"` : '';
  return `<svg${cls} width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" `
       + `stroke="currentColor" stroke-width="1.6" stroke-linecap="round" `
       + `stroke-linejoin="round" aria-hidden="true" focusable="false">${d}</svg>`;
}

/**
 * Il logo ufficiale di Discount Searcher.
 *
 * Usa logo-144.png e non logo.png: l'originale è 1254×1254 px (~1,5 MB) mentre
 * qui il logo si vede a 36 px. La versione a 144 px resta nitida anche sugli
 * schermi ad alta densità e pesa ~38 KB, su ogni pagina del sito.
 * alt vuoto: accanto c'è sempre il nome "Discount Searcher" scritto.
 */
export function logoMark(size = 36, className = 'ds-logo__mark') {
  //Percorso assoluto: le pagine inglesi stanno in /en/ e un percorso relativo
  //cercherebbe l'immagine dentro quella cartella.
  return `<img class="${className}" src="/assets/img/logo-144.png" alt="" `
       + `width="${size}" height="${size}" decoding="async">`;
}

export const iconNames = Object.keys(PATHS);
