/**
 * Punto unico da cui il sito prende i contenuti in it.
 * Non importare direttamente i file qui accanto: usa services/content.js, che
 * sceglie la cartella giusta in base alla lingua della pagina.
 */

export { SITE, STORES, GENRES, DISCOUNTS, MAIN_NAV, SUPPORT_NAV, WORK_NAV, FOOTER_NAV } from './site.js';
export { CATEGORIES, POPULAR_TOPICS, findCategory, allArticles } from './support.js';
export { FAQ_GROUPS, allFaq } from './faq.js';
export { JOB_CATEGORY, JOB_CATEGORY_LABEL, ROLES, PROCESS, findRole } from './jobs.js';
export { TEAM } from './team.js';
