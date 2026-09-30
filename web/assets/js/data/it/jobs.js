/**
 * "Lavora con noi": ruoli aperti e passi della selezione.
 *
 * Contiene solo quello che il progetto fa davvero: nessuna promessa su
 * compensi, contratti o tempi, che non sono stati definiti. Impegno e accordi
 * se ne parla nel ticket della candidatura, e la pagina lo dice.
 *
 * Per aprire o chiudere un ruolo: aggiungi o togli una voce da ROLES. La
 * pagina, il menu a tendina del modulo e le anteprime si aggiornano da soli.
 *
 * Nota: la categoria dei ticket di candidatura è una sola (JOB_CATEGORY) e il
 * ruolo scelto finisce nell'oggetto del ticket. Aggiungendone altre qui
 * andrebbero aggiunte anche in api/models.py, altrimenti il server le rifiuta.
 */

/** Categoria dei ticket di candidatura (deve esistere anche in api/models.py). */
export const JOB_CATEGORY = 'candidatura';

/** Etichetta leggibile della categoria, come la mostra il server nelle email. */
export const JOB_CATEGORY_LABEL = 'Candidatura';

export const ROLES = [
  {
    id: 'sviluppo',
    title: 'Sviluppo',
    icon: 'code',
    summary: 'L\'applicazione per Windows e il server che gestisce account, cronologia e ticket.',
    does: [
      'Aggiungere funzioni all\'app desktop (Python, Tkinter/CustomTkinter)',
      'Correggere i problemi che arrivano dai ticket',
      'Lavorare sul backend: account, cronologia, ticket (FastAPI, PostgreSQL)',
    ],
    bring: [
      'Python: quanto basta per leggere e modificare del codice esistente',
      'Qualcosa che hai scritto, anche piccolo (un link o un file)',
    ],
    trial: 'Una modifica o una piccola funzione da realizzare nell\'app.',
  },
  {
    id: 'grafica',
    title: 'Grafica e design',
    icon: 'sparkle',
    summary: 'Le immagini del progetto: icone, elementi dell\'interfaccia, materiali per il sito.',
    does: [
      'Icone e immagini per l\'applicazione e per il sito',
      'Materiali per presentare il progetto e gli aggiornamenti',
      'Tenere coerente l\'aspetto fra applicazione e sito',
    ],
    bring: [
      'Qualche lavoro già fatto: un portfolio, o anche solo qualche immagine',
      'Gli strumenti che usi di solito',
    ],
    trial: 'Una proposta grafica su un elemento vero del progetto.',
  },
  {
    id: 'assistenza',
    title: 'Assistenza utenti',
    icon: 'chat',
    summary: 'Le risposte agli utenti: i ticket del Centro assistenza e le domande più frequenti.',
    does: [
      'Rispondere ai ticket di chi usa Discount Searcher',
      'Riconoscere i problemi tecnici e passarli a chi sviluppa',
      'Tenere aggiornate le guide e le domande frequenti',
    ],
    bring: [
      'Italiano scritto chiaro e paziente',
      'Precisione: chi scrive ha già un problema, la risposta non deve aggiungerne',
    ],
    trial: 'Una risposta scritta da te a un ticket di esempio.',
  },
  {
    id: 'contenuti',
    title: 'Contenuti e social',
    icon: 'book',
    summary: 'I testi del progetto: guide, pagine del sito, annunci degli aggiornamenti.',
    does: [
      'Scrivere guide e testi del Centro assistenza',
      'Raccontare le novità e gli aggiornamenti del progetto',
      'Curare i canali dove il progetto si presenta',
    ],
    bring: [
      'Qualcosa che hai scritto o pubblicato',
      'I canali che sai gestire',
    ],
    trial: 'Un testo breve su un argomento del progetto.',
  },
];

/** I tre passi della selezione, mostrati nella pagina "Lavora con noi". */
export const PROCESS = [
  {
    title: 'Candidatura',
    text: 'Scegli il ruolo e racconta chi sei e cosa sai fare. La candidatura apre un ticket, '
        + 'con lo stesso funzionamento di quelli dell\'assistenza.',
  },
  {
    title: 'Provino',
    text: 'Il team ti assegna una prova pratica legata al ruolo scelto. Domande e consegna '
        + 'restano dentro allo stesso ticket.',
  },
  {
    title: 'Esito',
    text: 'La risposta arriva nel ticket e via email. Se la prova convince, si parla di come '
        + 'entrare nel team e di quanto tempo puoi dedicarci.',
  },
];

/** Un ruolo a partire dal suo identificativo, o undefined se non esiste. */
export function findRole(id) {
  return ROLES.find((r) => r.id === id);
}
