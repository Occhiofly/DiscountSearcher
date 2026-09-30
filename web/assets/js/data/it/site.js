/**
 * Dati di struttura del sito: navigazione, footer, informazioni di prodotto.
 *
 * Tenerli qui invece che duplicati nell'HTML di ogni pagina significa che
 * aggiungere una voce di menu o cambiare un'etichetta è una modifica in un
 * punto solo, e header e footer restano automaticamente coerenti ovunque.
 */

export const SITE = {
  name: 'Discount Searcher',
  tagline: 'Offerte videogiochi, un solo posto',
  description:
    'Applicazione desktop per Windows che cerca le offerte sui videogiochi ' +
    'su Steam, Epic Games Store, GOG e Humble Store, con filtri per negozio, ' +
    'genere, sconto minimo e titolo.',
};

/**
 * Negozi coperti dalla ricerca (gli stessi definiti in backend.py).
 *
 * Loghi: tracciati SVG di Simple Icons 16.31.0 (licenza CC0-1.0), ricavati
 * dalle pagine ufficiali dei marchi e salvati in versione monocromatica.
 * I marchi appartengono ai rispettivi proprietari. Il logo è decorativo
 * (alt vuoto): il nome del negozio è sempre scritto accanto.
 */
export const STORES = [
  { id: 1,  name: 'Steam',            logo: '/assets/img/stores/steam.svg' },
  { id: 25, name: 'Epic Games Store', logo: '/assets/img/stores/epic-games.svg' },
  { id: 7,  name: 'GOG',              logo: '/assets/img/stores/gog.svg' },
  { id: 11, name: 'Humble Store',     logo: '/assets/img/stores/humble.svg' },
];

/** Generi filtrabili (gli stessi definiti in backend.py). */
export const GENRES = ['Tutti', 'Action', 'RPG', 'FPS', 'Horror', 'Adventure', 'Strategy'];

/** Soglie di sconto filtrabili (le stesse definite in backend.py). */
export const DISCOUNTS = ['Tutti', '10%+', '25%+', '50%+', '75%+'];

/** Navigazione principale. `match` elenca i file su cui la voce è "attiva". */
export const MAIN_NAV = [
  { label: 'Prodotto',   href: 'index.html#prodotto',      match: [] },
  { label: 'Funzioni',   href: 'index.html#funzioni',      match: [] },
  { label: 'Come funziona', href: 'index.html#come-funziona', match: [] },
  { label: 'Account',    href: 'index.html#account',       match: [] },
  { label: 'Team',       href: 'index.html#team',          match: [] },
  {
    label: 'Lavora con noi',
    href: 'lavora-con-noi.html',
    match: ['lavora-con-noi.html', 'candidatura.html'],
  },
  {
    label: 'Assistenza',
    href: 'assistenza.html',
    match: [
      'assistenza.html',
      'assistenza-categoria.html',
      'faq.html',
      'ticket-nuovo.html',
      'ticket-lista.html',
      'ticket-dettaglio.html',
    ],
  },
];

/** Navigazione interna al Centro assistenza. */
export const SUPPORT_NAV = [
  { label: 'Centro assistenza', href: 'assistenza.html',  match: ['assistenza.html', 'assistenza-categoria.html'] },
  { label: 'Domande frequenti', href: 'faq.html',         match: ['faq.html'] },
  { label: 'I miei ticket',     href: 'ticket-lista.html', match: ['ticket-lista.html', 'ticket-dettaglio.html'] },
  { label: 'Apri un ticket',    href: 'ticket-nuovo.html', match: ['ticket-nuovo.html'] },
];

/**
 * Navigazione interna a "Lavora con noi".
 * Stessa barra dell'assistenza: le candidature sono ticket, quindi "I miei
 * ticket" serve anche qui per ritrovare la propria.
 */
export const WORK_NAV = [
  { label: 'Lavora con noi', href: 'lavora-con-noi.html', match: ['lavora-con-noi.html'] },
  { label: 'Candidati',      href: 'candidatura.html',    match: ['candidatura.html'] },
  { label: 'I miei ticket',  href: 'ticket-lista.html',   match: [] },
];

/** Colonne del footer. */
export const FOOTER_NAV = [
  {
    title: 'Prodotto',
    links: [
      { label: 'Panoramica',      href: 'index.html#prodotto' },
      { label: 'Funzioni',        href: 'index.html#funzioni' },
      { label: 'Come funziona',   href: 'index.html#come-funziona' },
      { label: 'Negozi supportati', href: 'index.html#negozi' },
    ],
  },
  {
    title: 'Account',
    links: [
      { label: 'Account e sicurezza', href: 'index.html#account' },
      { label: 'Verifica email',      href: 'assistenza-categoria.html?c=verifica-email' },
      { label: 'Recupero password',   href: 'assistenza-categoria.html?c=recupero-password' },
      { label: 'Più dispositivi',     href: 'index.html#account' },
    ],
  },
  {
    title: 'Assistenza',
    links: [
      { label: 'Centro assistenza',  href: 'assistenza.html' },
      { label: 'Domande frequenti',  href: 'faq.html' },
      { label: 'Apri un ticket',     href: 'ticket-nuovo.html' },
      { label: 'I miei ticket',      href: 'ticket-lista.html' },
      { label: 'Accedi',             href: 'accedi.html' },
      { label: 'Crea un account',    href: 'registrati.html' },
    ],
  },
  {
    title: 'Progetto',
    links: [
      { label: 'Team',      href: 'index.html#team' },
      { label: 'Lavora con noi', href: 'lavora-con-noi.html' },
      { label: 'Crediti',   href: 'index.html#crediti' },
      { label: 'Sostieni il progetto', href: 'sostieni.html' },
      { label: 'Codice su GitHub',    href: 'https://github.com/Occhiofly/DiscountSearcher' },
      { label: 'Privacy',   href: 'privacy.html' },
      { label: 'Segnala un bug', href: 'ticket-nuovo.html?c=bug' },
    ],
  },
];
