/**
 * Site structure for the English version: navigation, footer, product info.
 * Italian twin: ../it/site.js — keep the two in sync when adding entries.
 * Page file names differ between languages: see services/i18n.js (PAGES).
 */

export const SITE = {
  name: 'Discount Searcher',
  tagline: 'Game deals, one single app',
  description:
    'Windows desktop app that finds video game deals on Steam, Epic Games ' +
    'Store, GOG and Humble Store, with filters for store, genre, minimum ' +
    'discount and title.',
};

/** Stores covered by the search (the same ones defined in backend.py). */
export const STORES = [
  { id: 1,  name: 'Steam',            logo: '/assets/img/stores/steam.svg' },
  { id: 25, name: 'Epic Games Store', logo: '/assets/img/stores/epic-games.svg' },
  { id: 7,  name: 'GOG',              logo: '/assets/img/stores/gog.svg' },
  { id: 11, name: 'Humble Store',     logo: '/assets/img/stores/humble.svg' },
];

export const GENRES = ['All', 'Action', 'RPG', 'FPS', 'Horror', 'Adventure', 'Strategy'];
export const DISCOUNTS = ['All', '10%+', '25%+', '50%+', '75%+'];

/** Main navigation. `match` lists the pages where the entry is "active". */
export const MAIN_NAV = [
  { label: 'Product',      href: 'index.html#product',      match: [] },
  { label: 'Features',     href: 'index.html#features',     match: [] },
  { label: 'How it works', href: 'index.html#how-it-works', match: [] },
  { label: 'Account',      href: 'index.html#account',      match: [] },
  { label: 'Team',         href: 'index.html#team',         match: [] },
  {
    label: 'Join the team',
    href: 'jobs.html',
    match: ['jobs.html', 'apply.html'],
  },
  {
    label: 'Help',
    href: 'support.html',
    match: [
      'support.html',
      'support-category.html',
      'faq.html',
      'ticket-new.html',
      'tickets.html',
      'ticket-detail.html',
    ],
  },
];

/** Navigation inside the help centre. */
export const SUPPORT_NAV = [
  { label: 'Help centre', href: 'support.html', match: ['support.html', 'support-category.html'] },
  { label: 'FAQ',         href: 'faq.html',     match: ['faq.html'] },
  { label: 'My tickets',  href: 'tickets.html', match: ['tickets.html', 'ticket-detail.html'] },
  { label: 'Open a ticket', href: 'ticket-new.html', match: ['ticket-new.html'] },
];

/** Navigation inside "Join the team". */
export const WORK_NAV = [
  { label: 'Join the team', href: 'jobs.html',  match: ['jobs.html'] },
  { label: 'Apply',         href: 'apply.html', match: ['apply.html'] },
  { label: 'My tickets',    href: 'tickets.html', match: [] },
];

/** Footer columns. */
export const FOOTER_NAV = [
  {
    title: 'Product',
    links: [
      { label: 'Overview',       href: 'index.html#product' },
      { label: 'Features',       href: 'index.html#features' },
      { label: 'How it works',   href: 'index.html#how-it-works' },
      { label: 'Supported stores', href: 'index.html#stores' },
    ],
  },
  {
    title: 'Account',
    links: [
      { label: 'Account and security', href: 'index.html#account' },
      { label: 'Email verification',   href: 'support-category.html?c=verifica-email' },
      { label: 'Password recovery',    href: 'support-category.html?c=recupero-password' },
      { label: 'Several computers',    href: 'index.html#account' },
    ],
  },
  {
    title: 'Help',
    links: [
      { label: 'Help centre',   href: 'support.html' },
      { label: 'FAQ',           href: 'faq.html' },
      { label: 'Open a ticket', href: 'ticket-new.html' },
      { label: 'My tickets',    href: 'tickets.html' },
      { label: 'Sign in',       href: 'login.html' },
      { label: 'Create an account', href: 'register.html' },
    ],
  },
  {
    title: 'Project',
    links: [
      { label: 'Team',          href: 'index.html#team' },
      { label: 'Join the team', href: 'jobs.html' },
      { label: 'Credits',       href: 'index.html#credits' },
      { label: 'Report a bug',  href: 'ticket-new.html?c=bug' },
      { label: 'Support the project', href: 'support-us.html' },
      { label: 'Code on GitHub',      href: 'https://github.com/Occhiofly/DiscountSearcher' },
      { label: 'Privacy',       href: 'privacy.html' },
    ],
  },
];
