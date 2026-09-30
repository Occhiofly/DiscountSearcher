/**
 * Frequently asked questions (English version of ../it/faq.js).
 *
 * The answers describe only real behaviour of the application and its server.
 * `tags` feed the internal search: words someone might type that do not appear
 * in the question itself. Ids must stay identical in both languages: they are
 * used in the links (faq.html#faq-verifica).
 */

export const FAQ_GROUPS = [
  {
    id: 'prodotto',
    title: 'The product',
    items: [
      {
        id: 'faq-cos-e',
        q: 'What is Discount Searcher?',
        tags: ['what', 'app', 'program', 'windows', 'desktop'],
        a: `<p>It is a Windows desktop application that shows video game deals from four digital
            stores: <strong>Steam</strong>, <strong>Epic Games Store</strong>, <strong>GOG</strong>
            and <strong>Humble Store</strong>.</p>
            <p>You pick the store, set your criteria — for example role-playing games discounted at
            least 50% on Steam — and get the matching list, without opening the store's website.
            To compare another store, pick it from the menu and search again.</p>`,
      },
      {
        id: 'faq-negozi',
        q: 'Which stores are supported?',
        tags: ['steam', 'epic', 'gog', 'humble', 'store', 'shops'],
        a: `<p>The search covers <strong>Steam</strong>, <strong>Epic Games Store</strong>,
            <strong>GOG</strong> and <strong>Humble Store</strong>.</p>
            <p>You choose the store from a drop-down menu before searching. Discount Searcher is an
            independent project and is not affiliated with any of these stores.</p>`,
      },
      {
        id: 'faq-dati',
        q: 'Where does the deal information come from?',
        tags: ['cheapshark', 'api', 'prices', 'source', 'data'],
        a: `<p>Deals come from the <strong>public CheapShark API</strong>, a service that collects
            discounts from several digital stores. Game genres come from the
            <strong>public Steam API</strong>.</p>
            <p>Discount Searcher does not set prices and does not sell anything: it shows what those
            sources report. The valid price is always the one shown by the store at the moment of
            purchase.</p>`,
      },
      {
        id: 'faq-acquisto',
        q: 'Can I buy games inside the application?',
        tags: ['buy', 'purchase', 'payment', 'card'],
        a: `<p>No. The application opens the deal in your browser, on the store's page: the purchase
            happens there.</p>
            <p>Discount Searcher never handles payments and never asks for payment details.</p>`,
      },
      {
        id: 'faq-sistemi',
        q: 'Which operating systems does it run on?',
        tags: ['mac', 'linux', 'windows', 'system', 'compatibility'],
        a: `<p>The application is distributed as an executable for <strong>Windows</strong> and does
            not require installing Python.</p>
            <p>There are no versions for other operating systems.</p>`,
      },
    ],
  },
  {
    id: 'account',
    title: 'Account',
    items: [
      {
        id: 'faq-serve-account',
        q: 'Do I need an account to use the application?',
        tags: ['registration', 'required', 'account', 'sign up'],
        a: `<p>Yes: the application opens on the sign-in and sign-up screen, and you reach the
            search after signing in.</p>
            <p>The account is also what makes the history available across different computers.</p>`,
      },
      {
        id: 'faq-registrazione',
        q: 'What do I need to sign up?',
        tags: ['sign up', 'register', 'gmail', 'date of birth'],
        a: `<p>A username, a password of at least 8 characters, an email address ending in
            <code>@gmail.com</code> and your date of birth.</p>
            <p>Right after signing up the account is not active yet: it must be confirmed with the
            verification code sent by email.</p>
            <p>You can sign up <a href="register.html">from the website</a> or from the application:
            it is the same account. The website is the only way if you do not use Windows.</p>`,
      },
      {
        id: 'faq-verifica',
        q: 'How does email verification work?',
        tags: ['code', '6 digits', 'verification', 'email', 'activation'],
        a: `<p>When you sign up the server sends a <strong>6-digit</strong> numeric code to the
            address you entered, valid for <strong>15 minutes</strong>. Typing it in the
            verification screen activates the account.</p>
            <p>If the code does not arrive or expires, you can ask for a new one from the same
            screen. An unverified account cannot sign in: trying with the right credentials, the
            application asks for a new code automatically and goes back to verification.</p>`,
      },
      {
        id: 'faq-piu-computer',
        q: 'Can I use my account on another computer?',
        tags: ['two computers', 'laptop', 'devices', 'sync'],
        a: `<p>Yes. The account is not tied to the computer where it was created: install the
            application elsewhere and sign in with the same credentials.</p>
            <p>Your <strong>history</strong> of opened games follows you too, because it is saved
            with the account and not on the single computer.</p>`,
      },
      {
        id: 'faq-password-dimenticata',
        q: 'What if I forget my password?',
        tags: ['recovery', 'reset', 'forgot', 'password'],
        a: `<p>From the sign-in screen you can start the password recovery by entering your
            username. If the account exists, you receive a 6-digit code by email, valid for 15
            minutes, to use together with the new password.</p>
            <p>Once the password is reset, <strong>every</strong> computer connected to that account
            is signed out and you receive a confirmation email.</p>`,
      },
      {
        id: 'faq-modifica-dati',
        q: 'How do I change my username, email or password?',
        tags: ['change', 'profile', 'edit', 'details'],
        a: `<p>From the <strong>Profile</strong> panel of the application. Leaving the new password
            field empty keeps the current password.</p>
            <p>Every change requires your <strong>current password</strong> as confirmation, and is
            notified by email to the address the account had before the change. When the password
            changes, the other connected computers are signed out.</p>
            <p>For the <strong>email</strong> the password is not enough: we send you two codes, one to
            your current address and one to the new one, to enter in the app (version 1.0.4 or later).
            This way someone who found out your password could not put their email in place of yours.
            If you no longer have access to the old address, open a ticket.</p>`,
      },
    ],
  },
  {
    id: 'sicurezza',
    title: 'Security',
    items: [
      {
        id: 'faq-codice',
        q: 'Is the application source code public?',
        tags: ['code', 'source', 'github', 'open source', 'licence'],
        a: `<p>Yes, you can read it: the project is on
            <a href="https://github.com/Occhiofly/DiscountSearcher" rel="noopener">GitHub</a>, together with the documentation that
            explains how it is built and why.</p>
            <p>It is not open source though: a proprietary licence applies, all rights reserved.
            You may read and study the code; copying, redistributing or making your own version of
            it is not allowed. The application stays free for everyone.</p>`,
      },
      {
        id: 'faq-protezione',
        q: 'How is my account protected?',
        tags: ['security', 'password', 'hash', 'protection', 'attempts'],
        a: `<p>The measures actually in place are:</p>
            <ul>
              <li>the password is never stored in clear text: the server only keeps a derived
                  value, with a random element that differs for every user;</li>
              <li>every change to the account details requires the current password and triggers a
                  notification email to the previous address; changing the email also needs two codes,
                  sent to the old and the new address;</li>
              <li>after several failed sign-in attempts in a row on the same username, sign-in is
                  temporarily blocked;</li>
              <li>every sign-in creates a session that the server can revoke, without changing the
                  password.</li>
            </ul>
            <p>No system is free of risk: a password different from the ones you use elsewhere
            remains the most effective protection.</p>`,
      },
      {
        id: 'faq-email-notifica',
        q: 'I received a change notification I did not ask for',
        tags: ['notification', 'email', 'unauthorised access', 'suspicious'],
        a: `<p>The notification email is sent every time the username, email or password is changed
            from the Profile panel.</p>
            <p>If it was not you, change your password immediately: doing so signs out every other
            computer connected to the account. Then open a ticket quoting the date and time shown in
            the email you received.</p>`,
      },
      {
        id: 'faq-dati-raccolti',
        q: 'Which data is kept?',
        tags: ['privacy', 'personal data', 'history', 'retention'],
        a: `<p>To run the account the server keeps your username, email address, date of birth, the
            value derived from your password and the history of the games you opened.</p>
            <p>Every sign-in saves a session with date, time and the device name: for the app it is
            the <strong>computer name</strong> set in Windows, for the website the word "Website".</p>
            <p>If you open a ticket or send an application, the messages stay in the ticket. The
            team also receives them by email, so a copy stays in the project's Gmail mailbox,
            together with any attached files (which the server does not keep).</p>
            <p>No payment data is requested or stored, because purchases happen entirely on the
            store's website.</p>
            <p>Retention times, the services involved and how to ask for deletion are in the
            <a href="privacy.html">privacy notice</a>.</p>`,
      },
    ],
  },
  {
    id: 'assistenza',
    title: 'Support',
    items: [
      {
        id: 'faq-contatto',
        q: 'How do I contact support?',
        tags: ['contact', 'ticket', 'help', 'support', 'talk', 'sign in', 'login'],
        a: `<p>Open a ticket from the help centre, signing in with the same username and password as
            the app; for your security the site then asks for a code sent by email. Choose the
            category closest to your problem and describe what happens.</p>
            <p>When the team replies you receive an email with the link to the ticket; you can
            follow the conversation and answer from the <strong>My tickets</strong> section.</p>
            <p>If you cannot sign in, read the guides about
            <a href="support-category.html?c=accesso">signing in</a> and
            <a href="support-category.html?c=recupero-password">password recovery</a> first.</p>
            <p>Never type your password in a ticket: whoever helps you does not need it.</p>`,
      },
      {
        id: 'faq-tempi',
        q: 'How long does it take to get an answer?',
        tags: ['time', 'wait', 'answer', 'when'],
        a: `<p>Discount Searcher is an independent project run by a very small group: there is no
            guaranteed response time.</p>
            <p>A complete report — what you were doing, what you expected, the exact error text —
            reduces the back and forth, and therefore the wait.</p>`,
      },
      {
        id: 'faq-bug',
        q: 'How do I report a bug?',
        tags: ['bug', 'error', 'problem', 'report', 'crash'],
        a: `<p>Open a ticket in the <strong>Report a bug</strong> category saying what you were
            doing, what you expected, what happened instead, the exact text of any error message and
            whether the problem happens every time.</p>
            <p>You can attach up to 3 files, for example a screenshot of the error.</p>`,
      },
    ],
  },
];

/** Every question in a single list, with the group it belongs to. */
export const allFaq = () =>
  FAQ_GROUPS.flatMap((group) =>
    group.items.map((item) => ({ ...item, groupId: group.id, groupTitle: group.title })),
  );
