/**
 * Contenuti del sito nella lingua della pagina.
 *
 * Le pagine e i componenti importano da qui, non dai file in data/: questo
 * modulo carica data/it/ oppure data/en/ a seconda di LANG (services/i18n.js)
 * e ne ripubblica le voci con gli stessi nomi di prima.
 *
 * Viene caricata una sola lingua per pagina: l'altra non viene nemmeno scaricata.
 */

import { LANG } from './i18n.js';

//await al primo livello del modulo: chi importa questo file aspetta che i
//contenuti siano pronti, quindi le pagine non devono cambiare il loro codice.
const content = LANG === 'en'
  ? await import('../data/en/index.js')
  : await import('../data/it/index.js');

export const SITE = content.SITE;
export const STORES = content.STORES;
export const GENRES = content.GENRES;
export const DISCOUNTS = content.DISCOUNTS;
export const MAIN_NAV = content.MAIN_NAV;
export const SUPPORT_NAV = content.SUPPORT_NAV;
export const WORK_NAV = content.WORK_NAV;
export const FOOTER_NAV = content.FOOTER_NAV;

export const CATEGORIES = content.CATEGORIES;
export const POPULAR_TOPICS = content.POPULAR_TOPICS;
export const findCategory = content.findCategory;
export const allArticles = content.allArticles;

export const FAQ_GROUPS = content.FAQ_GROUPS;
export const allFaq = content.allFaq;

export const JOB_CATEGORY = content.JOB_CATEGORY;
export const JOB_CATEGORY_LABEL = content.JOB_CATEGORY_LABEL;
export const ROLES = content.ROLES;
export const PROCESS = content.PROCESS;
export const findRole = content.findRole;

export const TEAM = content.TEAM;
