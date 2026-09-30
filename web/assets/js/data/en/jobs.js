/**
 * "Join the team": open roles and steps of the selection (English version of
 * ../it/jobs.js — the role ids must stay identical in both languages).
 *
 * Only what the project really does: no promises about pay, contracts or
 * timing, because none have been defined. Commitment and arrangements are
 * discussed in the application ticket, and the page says so.
 */

/** Ticket category used by applications (must exist in api/models.py too). */
export const JOB_CATEGORY = 'candidatura';

/** Readable label of that category, the same the server shows in its emails. */
export const JOB_CATEGORY_LABEL = 'Application';

export const ROLES = [
  {
    id: 'sviluppo',
    title: 'Development',
    icon: 'code',
    summary: 'The Windows application and the server behind accounts, history and tickets.',
    does: [
      'Add features to the desktop app (Python, Tkinter/CustomTkinter)',
      'Fix the problems that arrive through tickets',
      'Work on the backend: accounts, history, tickets (FastAPI, PostgreSQL)',
    ],
    bring: [
      'Python: enough to read and change existing code',
      'Something you wrote, even something small (a link or a file)',
    ],
    trial: 'A change or a small feature to build in the app.',
  },
  {
    id: 'grafica',
    title: 'Graphics and design',
    icon: 'sparkle',
    summary: 'The visual side of the project: icons, interface elements, material for the site.',
    does: [
      'Icons and images for the application and the website',
      'Material to present the project and its updates',
      'Keep the look consistent between app and website',
    ],
    bring: [
      'Some work you already did: a portfolio, or even just a few images',
      'The tools you normally use',
    ],
    trial: 'A design proposal for a real element of the project.',
  },
  {
    id: 'assistenza',
    title: 'User support',
    icon: 'chat',
    summary: 'The answers to users: help centre tickets and the most common questions.',
    does: [
      'Reply to the tickets of people using Discount Searcher',
      'Recognise technical problems and pass them to the developers',
      'Keep the guides and the FAQ up to date',
    ],
    bring: [
      'Clear, patient written English (Italian is a plus)',
      'Care: whoever writes already has a problem, the answer should not add one',
    ],
    trial: 'An answer written by you to an example ticket.',
  },
  {
    id: 'contenuti',
    title: 'Content and social',
    icon: 'book',
    summary: 'The words of the project: guides, website pages, update announcements.',
    does: [
      'Write guides and help centre articles',
      'Tell people about news and updates',
      'Look after the channels where the project shows up',
    ],
    bring: [
      'Something you wrote or published',
      'The channels you can manage',
    ],
    trial: 'A short text about a topic of the project.',
  },
];

/** The three steps of the selection, shown on the "Join the team" page. */
export const PROCESS = [
  {
    title: 'Application',
    text: 'Pick the role and tell us who you are and what you can do. The application opens a '
        + 'ticket, exactly like the ones in the help centre.',
  },
  {
    title: 'Trial task',
    text: 'The team gives you a practical task related to the role. Questions and delivery stay '
        + 'inside the same ticket.',
  },
  {
    title: 'Outcome',
    text: 'The answer arrives in the ticket and by email. If the task convinces us, we talk about '
        + 'joining the team and how much time you can give.',
  },
];

/** A role by its id, or undefined. */
export function findRole(id) {
  return ROLES.find((r) => r.id === id);
}
