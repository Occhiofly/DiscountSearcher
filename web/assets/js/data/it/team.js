/**
 * Team di Discount Searcher.
 *
 * Contiene solo informazioni confermate: nome e ruolo. Nessuna biografia,
 * esperienza o profilo social è stato aggiunto perché non sono stati forniti.
 *
 * `scope` descrive l'area di cui il ruolo si occupa *all'interno del sito*
 * (è una descrizione del ruolo, non della persona).
 *
 * Per aggiungere un membro: nuova voce in questo array. `photo` è facoltativo
 * (percorso di un'immagine reale in assets/img/team/); se manca viene
 * mostrata l'iniziale del nome.
 */

export const TEAM = [
  {
    name: 'Alessio',
    role: 'Developer',
    scope: 'Sviluppo di Discount Searcher.',
    photo: null,
  },
  {
    name: 'Vittorio',
    role: 'Support Manager, Localization Specialist',
    scope: 'Assistenza agli utenti di Discount Searcher e traduttore professionista della versione inglese del sito.',
    photo: null,
  },
  {
    name: 'Eva',
    role: 'Graphic Design',
    scope: 'Produzione di contenuti visivi digitali, Progettazione grafica.',
    photo: null,
  },
  {
    name: 'Mathias',
    role: 'Support Assistant, Sponsorships',
    scope: 'Assistenza agli utenti di Discount Searcher e ricerca di sponsor e collaborazioni.',
    photo: null,
  },
];
