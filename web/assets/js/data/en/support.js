/**
 * Help centre content: categories and articles (English version of
 * ../it/support.js).
 *
 * Every text describes only behaviour the application really has (checked in
 * main.py, backend.py and api/main.py). Category and article ids must stay
 * identical in both languages: they are used in links and in ticket categories.
 */

export const CATEGORIES = [
  {
    id: 'account',
    icon: 'user',
    title: 'Account',
    summary: 'Creating an account, changing your details, using it on several computers.',
    articles: [
      {
        id: 'creare-account',
        title: 'Creating an account',
        body: `<p>To sign up you need a <strong>username</strong>, a <strong>password</strong> of at
          least 8 characters, an email address ending in <code>@gmail.com</code> and your date of
          birth.</p>
          <p>Right after signing up the account exists but is not active yet: you receive a 6-digit
          verification code by email and land on the screen where you type it. Until you do, signing
          in is not possible.</p>
          <p>You can sign up <a href="register.html">from the website</a> or from the application: it
          is the same account and works for both. The application is Windows only, so from a Mac or
          Linux you sign up on the website; the help centre and tickets work from any computer.</p>`,
      },
      {
        id: 'modificare-dati',
        title: 'Changing username, email or password',
        body: `<p>Open the <strong>Profile</strong> panel of the application by clicking your user
          name in the sidebar. From there you can change username, email and password. If you leave
          the new password field empty, the password is left untouched.</p>
          <p>When saving, your <strong>current password</strong> is requested as confirmation:
          without it the change is not applied. Once done, you receive a notification email at the
          address the account had <em>before</em> the change.</p>
          <p>If you change your <strong>email</strong>, after the password a screen asks for two
          6-digit codes: one is sent to your current address, the other to the new one. They are valid
          for 15 minutes; the email only changes once you enter both. You need app 1.0.4 or later. If
          you no longer have access to the old address, open a ticket.</p>
          <p>If you change the password, the other computers connected to that account are signed
          out; only the one you used stays connected.</p>`,
      },
      {
        id: 'piu-computer',
        title: 'Using the same account on several computers',
        body: `<p>The account is not tied to the computer where you created it. Install the
          application on another computer and sign in with the same credentials.</p>
          <p>You also find your <strong>history</strong> of opened games, because it is saved with
          the account and not on the single computer.</p>`,
      },
    ],
  },
  {
    id: 'accesso',
    icon: 'key',
    title: 'Signing in',
    summary: 'Problems while signing in, rejected credentials, blocked attempts.',
    articles: [
      {
        id: 'credenziali-errate',
        title: '"Wrong username or password"',
        body: `<p>This message appears both when the username does not exist and when the password
          is wrong. It is deliberately generic: telling the two apart would let anyone find out
          which usernames are registered.</p>
          <p>Check capital letters and leading or trailing spaces. If you do not remember your
          password, use the password recovery on the sign-in screen.</p>`,
      },
      {
        id: 'troppi-tentativi',
        title: '"Too many failed attempts"',
        body: `<p>After several failed sign-in attempts in a row on the same username, signing in is
          blocked temporarily. It is a protection against someone trying many passwords to guess the
          right one.</p>
          <p>The message says how long to wait. There is nothing to do: once the wait is over,
          signing in works again. A successful sign-in resets the count.</p>`,
      },
      {
        id: 'accesso-automatico',
        title: 'Why I am not asked to sign in every time',
        body: `<p>When you sign in, the application keeps a session token on your computer. At the
          next start it checks whether it is still valid and, if it is, opens the search screen
          directly.</p>
          <p>Using <strong>Sign out</strong> cancels the session on the server, and the next start
          asks for your credentials again.</p>`,
      },
    ],
  },
  {
    id: 'recupero-password',
    icon: 'lock',
    title: 'Password recovery',
    summary: 'Resetting the password when you can no longer sign in.',
    articles: [
      {
        id: 'reimpostare-password',
        title: 'Resetting a forgotten password',
        body: `<p>From the sign-in screen open the password recovery and enter your username. If the
          account exists, a 6-digit code is sent to the registered email address.</p>
          <p>Type the code together with the new password. The code is valid for
          <strong>15 minutes</strong>: once expired, request a new one.</p>
          <p>After the reset, <strong>every</strong> computer connected to that account is signed
          out and you receive a confirmation email.</p>`,
      },
      {
        id: 'messaggio-generico-recupero',
        title: 'Why the answer is always the same',
        body: `<p>Password recovery always answers with the same message, even when the username
          does not exist.</p>
          <p>The reason is security: a different answer in the two cases would turn this feature
          into a way to find out which usernames are registered, by trying many of them.</p>`,
      },
    ],
  },
  {
    id: 'verifica-email',
    icon: 'mail',
    title: 'Email verification',
    summary: 'The 6-digit code, when it expires and how to get a new one.',
    articles: [
      {
        id: 'come-funziona-codice',
        title: 'How the verification code works',
        body: `<p>After signing up you receive a 6-digit numeric code by email, valid for
          <strong>15 minutes</strong>. Typing it in the verification screen activates the
          account.</p>
          <p>The code is generated randomly by the server and compared with a technique that does
          not reveal anything about the right value through the response time.</p>`,
      },
      {
        id: 'codice-non-arrivato',
        title: 'The code did not arrive, or it expired',
        body: `<p>From the verification screen you can ask for a new code: the previous one is
          replaced.</p>
          <p>Check the spam or promotions folder of your mailbox too, and make sure the address you
          typed when signing up was correct.</p>
          <p>If the address was wrong, the code can never arrive: create a new account with the
          right address and a different username.</p>
          <p>Note: support tickets require signing in, which is only possible after the email has
          been verified.</p>`,
      },
      {
        id: 'login-non-verificato',
        title: 'Signing in with an account that is not verified yet',
        body: `<p>If you try to sign in with the right credentials but the email is not confirmed
          yet, the application automatically asks for a new code and takes you back to the
          verification screen, instead of showing a generic error.</p>`,
      },
    ],
  },
  {
    id: 'applicazione',
    icon: 'windows',
    title: 'Application',
    summary: 'Starting it, requirements and error messages of the desktop app.',
    articles: [
      {
        id: 'requisiti',
        title: 'What you need to use the application',
        body: `<p>Discount Searcher is a desktop application for <strong>Windows</strong>,
          distributed as a standalone executable: installing Python is not necessary.</p>
          <p>An active internet connection is required, because deals, genres and the account are
          requested from remote services every time.</p>`,
      },
      {
        id: 'errore-connessione',
        title: '"Connection error" during a search',
        body: `<p>It appears when the application cannot reach the deals service. Check your
          internet connection and try again.</p>
          <p>If the connection works and the error stays, the remote service may be temporarily
          unavailable: try later or open a ticket saying at what time it happened.</p>`,
      },
      {
        id: 'app-lenta',
        title: 'The application seems stuck during a search',
        body: `<p>During a search the application shows "Searching...". With the genre filter on,
          the wait is longer, because the genre of each game must be requested from Steam
          separately.</p>
          <p>Genres already requested stay in memory for the session, so later searches on the same
          games are faster.</p>`,
      },
    ],
  },
  {
    id: 'offerte',
    icon: 'tag',
    title: 'Deals and search',
    summary: 'Where prices come from, which stores are covered, how to open a deal.',
    articles: [
      {
        id: 'origine-dati',
        title: 'Where the prices come from',
        body: `<p>Deals come from the <strong>public CheapShark API</strong>, a service that
          collects discounts from several digital stores. Game genres come from the
          <strong>public Steam API</strong>.</p>
          <p>Discount Searcher does not set prices and does not sell anything: it shows what those
          sources report. Prices are in <strong>US dollars</strong>, as CheapShark provides them.
          Prices and availability can change, and the correct value is always the one shown by the
          store.</p>`,
      },
      {
        id: 'aprire-offerta',
        title: 'Opening a deal',
        body: `<p>Every result has a link that opens the deal in your default browser, on the page
          of the matching store.</p>
          <p>The purchase always happens on the store's website. The application never handles
          payments and never asks for payment details.</p>`,
      },
      {
        id: 'risultati-mancanti',
        title: 'A game I expected does not show up',
        body: `<p>The search does not go through the whole catalogue of the store: it shows its
          <strong>most recent</strong> deals, that is the ones changed in the last 7 days, up to 50
          per store. A game that has been discounted for longer, or that falls outside those 50,
          does not appear even if the deal is still valid.</p>
          <p>If you think the game is among the recent deals, try setting the minimum discount to
          "All", the genre to "All" and clearing the search field.</p>
          <p>A game without a discount in the chosen store never appears in the results.</p>`,
      },
    ],
  },
  {
    id: 'filtri',
    icon: 'filter',
    title: 'Filters',
    summary: 'Store, genre, minimum discount and title: how they work together.',
    articles: [
      {
        id: 'come-combinare',
        title: 'How the filters combine',
        body: `<p>Filters all apply together: the result shows the games that match store, genre,
          minimum discount and searched text at the same time.</p>
          <p>Setting "All" on genre or discount means not filtering by that criterion. The text
          field searches inside the game title, among the recent deals of the chosen store: it is
          not a search through the whole catalogue.</p>`,
      },
      {
        id: 'filtro-genere',
        title: 'Why the genre filter is slower',
        body: `<p>The genre is not part of the deal data: it must be requested from Steam game by
          game. With the filter on, more network requests are needed than in a search without
          genre.</p>
          <p>To reduce the wait, the title filter is applied before the genre one: games already
          excluded by the text are never requested from Steam.</p>`,
      },
    ],
  },
  {
    id: 'cronologia',
    icon: 'history',
    title: 'History',
    summary: 'The games you opened and where they are kept.',
    articles: [
      {
        id: 'cosa-registra',
        title: 'What ends up in the history',
        body: `<p>When you open the link of a deal, that game is added to the history, visible in
          the sidebar of the application. From there you can open it again without searching for
          it.</p>
          <p>The history belongs to the account, not to the computer: you find it again when signing
          in from another computer. The last 100 entries are kept.</p>`,
      },
      {
        id: 'cronologia-vuota',
        title: 'The history looks empty',
        body: `<p>If it does not load, the list simply stays empty: this is on purpose, so that a
          secondary problem does not block the use of the application.</p>
          <p>Check your connection and restart the application. If the problem stays, open a ticket
          saying when it started.</p>`,
      },
    ],
  },
  {
    id: 'bug',
    icon: 'bug',
    title: 'Report a bug',
    summary: 'What to include so that the report is useful.',
    articles: [
      {
        id: 'cosa-includere',
        title: 'What to include in the report',
        body: `<p>A useful report contains:</p>
          <ul>
            <li>what you were doing when it happened;</li>
            <li>what you expected and what happened instead;</li>
            <li>the exact text of any error message, or a screenshot attached to the ticket;</li>
            <li>whether the problem happens every time or happened only once;</li>
            <li>the filters you had set, if it is about the search.</li>
          </ul>
          <p>Never type your password in a ticket: whoever helps you does not need it.</p>`,
      },
    ],
  },
  {
    id: 'altro',
    icon: 'help',
    title: 'Other',
    summary: 'Questions that do not fit the other categories.',
    articles: [
      {
        id: 'nessuna-categoria',
        title: 'My question does not fit any category',
        body: `<p>Open a ticket choosing the "Other" category and describe the situation in your own
          words: the team reads every ticket, whatever the category.</p>`,
      },
    ],
  },
];

/** Topics highlighted on the help centre home page. */
export const POPULAR_TOPICS = [
  { label: 'The verification code does not arrive', href: 'support-category.html?c=verifica-email#codice-non-arrivato' },
  { label: 'I forgot my password',                  href: 'support-category.html?c=recupero-password#reimpostare-password' },
  { label: 'Using the account on two computers',    href: 'support-category.html?c=account#piu-computer' },
  { label: 'Where the prices come from',            href: 'support-category.html?c=offerte#origine-dati' },
  { label: 'The genre filter is slow',              href: 'support-category.html?c=filtri#filtro-genere' },
  { label: 'Changing email or password',            href: 'support-category.html?c=account#modificare-dati' },
];

/** A category by its id. */
export const findCategory = (id) => CATEGORIES.find((c) => c.id === id) || null;

/** Flat list of every article, with its category. Used by the help centre search. */
export const allArticles = () =>
  CATEGORIES.flatMap((category) =>
    category.articles.map((article) => ({
      ...article,
      categoryId: category.id,
      categoryTitle: category.title,
      href: `support-category.html?c=${category.id}#${article.id}`,
    })),
  );
