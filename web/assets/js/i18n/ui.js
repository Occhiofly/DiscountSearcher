/**
 * Testi dell'interfaccia del sito, in italiano e in inglese.
 *
 * Qui stanno SOLO i testi generati da JavaScript (bottoni, messaggi, stati
 * vuoti, errori). Il testo fisso delle pagine è nell'HTML: quello italiano
 * nella cartella principale, quello inglese in /en/.
 *
 * I contenuti veri e propri — articoli dell'assistenza, domande frequenti,
 * ruoli, team, menu — stanno in assets/js/data/it/ e assets/js/data/en/.
 *
 * Per aggiungere un testo: una voce con entrambe le lingue, poi t('chiave').
 */

export const UI = {
  // --- Intestazione, footer e navigazione ---------------------------------
  'header.logoAria': {
    it: 'Discount Searcher — vai alla pagina iniziale',
    en: 'Discount Searcher — go to the home page',
  },
  'header.tagline': { it: 'per Windows', en: 'for Windows' },
  'header.download': { it: 'Scarica', en: 'Download' },
  'header.downloadLong': { it: 'Scarica per Windows', en: 'Download for Windows' },
  'header.openTicket': { it: 'Apri un ticket', en: 'Open a ticket' },
  'header.nav': { it: 'Navigazione principale', en: 'Main navigation' },
  'header.navMobile': { it: 'Navigazione principale (mobile)', en: 'Main navigation (mobile)' },
  'header.menuOpen': { it: 'Apri il menu di navigazione', en: 'Open the navigation menu' },
  'header.menuClose': { it: 'Chiudi il menu di navigazione', en: 'Close the navigation menu' },
  'header.language': { it: 'English', en: 'Italiano' },
  'header.languageAria': { it: 'Switch to English', en: 'Passa all\'italiano' },
  'footer.legalTitle': { it: 'Note legali', en: 'Legal notes' },
  'footer.credits': {
    it: 'Dati sulle offerte forniti da CheapShark',
    en: 'Deal data provided by CheapShark',
  },
  'footer.rights': {
    it: '© {year} {name}. Tutti i diritti riservati. Progetto indipendente.',
    en: '© {year} {name}. All rights reserved. Independent project.',
  },
  'footer.legal1': {
    it: 'Discount Searcher è un progetto indipendente. Non è affiliato, sponsorizzato o approvato '
      + 'da Valve / Steam, Epic Games, GOG, Humble Bundle o CheapShark. I nomi dei negozi e i '
      + 'relativi marchi appartengono ai rispettivi proprietari e sono citati solo per indicare '
      + 'dove sono disponibili le offerte.',
    en: 'Discount Searcher is an independent project. It is not affiliated with, sponsored by or '
      + 'endorsed by Valve / Steam, Epic Games, GOG, Humble Bundle or CheapShark. Store names and '
      + 'trademarks belong to their respective owners and are mentioned only to say where the '
      + 'deals can be found.',
  },
  'footer.legal2': {
    it: 'I dati sulle offerte provengono dall\'API pubblica di CheapShark e le informazioni sui '
      + 'generi dall\'API pubblica di Steam: prezzi, sconti e disponibilità sono quelli forniti da '
      + 'queste fonti e possono cambiare o non essere aggiornati in tempo reale. L\'acquisto '
      + 'avviene sempre sul sito del negozio, mai dentro l\'applicazione.',
    en: 'Deal data comes from the public CheapShark API and genre information from the public '
      + 'Steam API: prices, discounts and availability are the ones these sources provide and may '
      + 'change or not be up to date. Purchases always happen on the store\'s website, never '
      + 'inside the application.',
  },
  'lang.bannerText': {
    it: 'This site is also available in English.',
    en: 'Questo sito è disponibile anche in italiano.',
  },
  'lang.bannerAction': { it: 'Read in English', en: 'Leggi in italiano' },
  'lang.bannerClose': { it: 'Chiudi', en: 'Close' },

  // --- Aggiornamento in corso (components/maintenance.js) ------------------
  'maintenance.title': { it: 'Aggiornamento in corso', en: 'Update in progress' },
  'maintenance.text': {
    it: 'Il team sta aggiornando Discount Searcher. L\'aggiornamento può richiedere qualche '
      + 'ora o qualche giorno: tutto riprenderà a funzionare appena sarà finito. Grazie per '
      + 'la pazienza.',
    en: 'The team is updating Discount Searcher. The update may take a few hours or a few days: '
      + 'everything will work again as soon as it is finished. Thank you for your patience.',
  },
  'maintenance.retry': { it: 'Riprova', en: 'Try again' },

  // --- Barra dell'assistenza / lavora con noi ------------------------------
  'subnav.support': { it: 'Sezioni del Centro assistenza', en: 'Help centre sections' },
  'subnav.jobs': { it: 'Sezioni di Lavora con noi', en: 'Join the team sections' },
  'subnav.signIn': { it: 'Accedi', en: 'Sign in' },
  'subnav.signOut': { it: 'Esci', en: 'Sign out' },
  'subnav.signedInAs': { it: 'Accesso effettuato come {username}', en: 'Signed in as {username}' },

  // --- Stati comuni dei ticket ---------------------------------------------
  'state.loginRequiredTitle': { it: 'Accedi per continuare', en: 'Sign in to continue' },
  'state.loginRequiredText': {
    it: 'I ticket sono legati al tuo account: accedi con lo stesso username e la stessa password '
      + 'dell\'app Discount Searcher.',
    en: 'Tickets belong to your account: sign in with the same username and password you use in '
      + 'the Discount Searcher app.',
  },
  'state.signIn': { it: 'Accedi', en: 'Sign in' },
  'state.noAccount': { it: 'Non hai un account? Creane uno', en: 'No account? Create one' },
  'state.errorTitle': { it: 'Qualcosa non ha funzionato', en: 'Something went wrong' },
  'state.retry': { it: 'Riprova', en: 'Try again' },
  'state.unexpected': { it: 'Si è verificato un errore imprevisto.', en: 'An unexpected error occurred.' },
  'state.otherCategory': { it: 'Altro', en: 'Other' },

  // --- Servizio ticket: stati e messaggi d'errore ---------------------------
  'ticket.status.open': { it: 'Aperto', en: 'Open' },
  'ticket.status.openText': {
    it: 'In attesa di una risposta del team. Riceverai un\'email quando arriva.',
    en: 'Waiting for the team to reply. You will get an email when it does.',
  },
  'ticket.status.progress': { it: 'In lavorazione', en: 'In progress' },
  'ticket.status.progressText': {
    it: 'Il team sta lavorando alla tua richiesta.',
    en: 'The team is working on your request.',
  },
  'ticket.status.waiting': { it: 'In attesa di risposta', en: 'Waiting for your reply' },
  'ticket.status.waitingText': {
    it: 'Il team ti ha risposto e attende un tuo messaggio per procedere.',
    en: 'The team replied and is waiting for your message to continue.',
  },
  'ticket.status.resolved': { it: 'Risolto', en: 'Resolved' },
  'ticket.status.resolvedText': {
    it: 'La richiesta è stata segnata come risolta. Se il problema si ripresenta puoi rispondere qui.',
    en: 'The request was marked as resolved. If the problem comes back you can reply here.',
  },
  'ticket.status.closed': { it: 'Chiuso', en: 'Closed' },
  'ticket.status.closedText': {
    it: 'Il ticket è chiuso e non accetta nuove risposte. Per un nuovo problema apri un altro ticket.',
    en: 'This ticket is closed and does not accept new replies. Open a new ticket for a new problem.',
  },
  'ticket.err.needLogin': {
    it: 'Accedi con il tuo account per usare i ticket.',
    en: 'Sign in with your account to use tickets.',
  },
  'ticket.err.network': {
    it: 'Impossibile contattare il server. Se non lo usava nessuno da un po\' potrebbe essere in '
      + 'avvio: riprova tra qualche secondo.',
    en: 'Could not reach the server. If nobody used it for a while it may be starting up: try '
      + 'again in a few seconds.',
  },
  'ticket.err.server': {
    it: 'Si è verificato un errore imprevisto. Riprova tra qualche istante.',
    en: 'An unexpected error occurred. Please try again in a moment.',
  },
  'ticket.err.sessionExpired': {
    it: 'La sessione è scaduta: accedi di nuovo per continuare.',
    en: 'Your session expired: sign in again to continue.',
  },
  'ticket.err.notFound': { it: 'Ticket non trovato.', en: 'Ticket not found.' },
  'ticket.err.validation': {
    it: 'Alcuni dati non sono validi: controlla i campi e riprova.',
    en: 'Some details are not valid: check the fields and try again.',
  },
  'ticket.err.unavailable': {
    it: 'Il server non è disponibile in questo momento. Riprova tra qualche istante.',
    en: 'The server is not available right now. Please try again in a moment.',
  },
  'ticket.err.generic': {
    it: 'Il server ha restituito un errore. Riprova tra qualche istante.',
    en: 'The server returned an error. Please try again in a moment.',
  },
  'api.networkError': {
    it: 'Impossibile contattare il server. Controlla la connessione e riprova.',
    en: 'Could not reach the server. Check your connection and try again.',
  },
  'api.requestFailed': { it: 'Richiesta non riuscita', en: 'Request failed' },

  // --- Accesso --------------------------------------------------------------
  'login.alreadyTitle': { it: 'Hai già effettuato l\'accesso', en: 'You are already signed in' },
  'login.alreadyText': { it: 'Sei collegato come <strong>{username}</strong>.', en: 'You are signed in as <strong>{username}</strong>.' },
  'login.continue': { it: 'Continua', en: 'Continue' },
  'login.switchAccount': { it: 'Esci e accedi con un altro account', en: 'Sign out and use another account' },
  'login.slowServer': {
    it: 'Impossibile contattare il server. Controlla la connessione e riprova tra qualche secondo.',
    en: 'Could not reach the server. Check your connection and try again in a few seconds.',
  },
  'login.wrongCredentials': { it: 'Username o password errati.', en: 'Wrong username or password.' },
  'login.notVerified': {
    it: 'L\'email di questo account non è ancora verificata. Apri l\'app Discount Searcher e '
      + 'inserisci il codice che ti è stato inviato.',
    en: 'The email of this account is not verified yet. Open the Discount Searcher app and enter '
      + 'the code you received.',
  },
  'login.missingFields': { it: 'Inserisci username e password.', en: 'Enter your username and password.' },
  'login.serverError': {
    it: 'Accesso non riuscito per un errore del server. Riprova tra qualche istante.',
    en: 'Sign-in failed because of a server error. Please try again in a moment.',
  },
  'login.device': { it: 'Sito web', en: 'Website' },
  // --- Crea un account (pages/register.js) ---
  'register.missingFields': { it: 'Compila tutti i campi.', en: 'Fill in all the fields.' },
  'register.gmailOnly': {
    it: 'Per ora l\'indirizzo deve essere @gmail.com.',
    en: 'For now the address must be @gmail.com.',
  },
  'register.shortPassword': { it: 'La password deve avere almeno 8 caratteri.', en: 'The password must be at least 8 characters long.' },
  'register.taken': { it: 'Questo username è già in uso: scegline un altro.', en: 'This username is already taken: choose another one.' },
  'register.slowServer': {
    it: 'Non siamo riusciti a contattare il server. Controlla la connessione e riprova.',
    en: 'We could not reach the server. Check your connection and try again.',
  },
  'register.serverError': {
    it: 'Qualcosa non ha funzionato. Riprova fra qualche istante.',
    en: 'Something went wrong. Please try again in a moment.',
  },
  'register.codeTitle': { it: 'Controlla la tua email', en: 'Check your email' },
  'register.codeText': {
    it: 'Abbiamo mandato un codice di 6 cifre a <strong>{email}</strong>. Vale 15 minuti.',
    en: 'We sent a 6-digit code to <strong>{email}</strong>. It is valid for 15 minutes.',
  },
  'register.codeLabel': { it: 'Codice di verifica', en: 'Verification code' },
  'register.codeSubmit': { it: 'Verifica l\'email', en: 'Verify the email' },
  'register.codeInvalid': { it: 'Il codice è fatto di 6 cifre.', en: 'The code is made of 6 digits.' },
  'register.codeResend': { it: 'Invia un nuovo codice', en: 'Send a new code' },
  'register.codeResendIn': { it: 'Nuovo codice fra {seconds} s', en: 'New code in {seconds} s' },
  'register.codeResent': { it: 'Ti abbiamo mandato un nuovo codice.', en: 'We sent you a new code.' },
  'register.codeNotSent': {
    it: 'Non siamo riusciti a inviare l\'email. Riprova fra qualche minuto.',
    en: 'We could not send the email. Try again in a few minutes.',
  },
  'register.codeWrongEmail': {
    it: 'Hai sbagliato indirizzo? L\'account esiste già con quel nome utente: scrivici dal '
      + '<a href="{url}">Centro assistenza</a> e lo sistemiamo noi.',
    en: 'Wrong address? The account already exists with that username: write to us from the '
      + '<a href="{url}">help centre</a> and we will sort it out.',
  },
  'register.codeSpam': {
    it: 'Non la trovi? Guarda anche nella cartella Spam di Gmail.',
    en: 'Can\'t find it? Check your Gmail Spam folder too.',
  },
  'register.doneTitle': { it: 'Account pronto', en: 'Account ready' },
  'register.doneText': {
    it: 'L\'account <strong>{username}</strong> è attivo. Puoi accedere qui sul sito, dove per '
      + 'sicurezza ti manderemo un codice via email, e usare lo stesso account nell\'app.',
    en: 'The account <strong>{username}</strong> is active. You can sign in here on the site, where '
      + 'for your security we will email you a code, and use the same account in the app.',
  },
  'register.goToLogin': { it: 'Accedi', en: 'Sign in' },
  'register.downloadApp': { it: 'Scarica l\'app (Windows)', en: 'Download the app (Windows)' },
  'register.myTickets': { it: 'I miei ticket', en: 'My tickets' },
  // --- Area staff (pages/staff.js) ---
  'staff.title': { it: 'Area staff', en: 'Staff area' },
  'staff.link': { it: 'Area staff', en: 'Staff area' },
  'staff.docTitle': { it: '{id} — Area staff — Discount Searcher', en: '{id} — Staff area — Discount Searcher' },
  'staff.lead': {
    it: 'Tutti i ticket e le candidature. Rispondi come <strong>{name}</strong>.',
    en: 'All tickets and applications. You reply as <strong>{name}</strong>.',
  },
  'staff.refresh': { it: 'Aggiorna', en: 'Refresh' },
  'staff.search': { it: 'Cerca per oggetto, ID o utente', en: 'Search by subject, ID or user' },
  'staff.filterByStatus': { it: 'Filtra per stato', en: 'Filter by status' },
  'staff.user': { it: 'Utente', en: 'User' },
  'staff.email': { it: 'Email', en: 'Email' },
  'staff.opened': { it: 'Aperto', en: 'Opened' },
  'staff.emptyTitle': { it: 'Nessun ticket', en: 'No tickets' },
  'staff.emptyText': {
    it: 'Quando qualcuno apre un ticket o si candida, compare qui.',
    en: 'When someone opens a ticket or applies, it shows up here.',
  },
  'staff.noMatchText': { it: 'Prova con "Tutti" o cambia la ricerca.', en: 'Try "All" or change the search.' },
  'staff.extra': { it: 'Informazioni aggiuntive', en: 'Additional information' },
  'staff.replyAs': { it: 'Rispondi come {name}', en: 'Reply as {name}' },
  'staff.replyPlaceholder': { it: 'Scrivi la risposta per {user}…', en: 'Write your reply to {user}…' },
  'staff.statusAfter': { it: 'Stato dopo la risposta', en: 'Status after the reply' },
  'staff.replyHint': {
    it: '{user} riceve un avviso via email. Ctrl+Invio per inviare.',
    en: '{user} gets an email notification. Ctrl+Enter to send.',
  },
  'staff.statusWaiting': { it: 'In attesa dell\'utente', en: 'Waiting for the user' },
  'staff.statusOnly': { it: 'Cambia solo lo stato', en: 'Change the status only' },
  'staff.newStatus': { it: 'Nuovo stato', en: 'New status' },
  'staff.saveStatus': { it: 'Salva stato', en: 'Save status' },
  'staff.statusSaved': {
    it: 'Stato salvato: {status}. {user} riceve un avviso.',
    en: 'Status saved: {status}. {user} gets a notification.',
  },
  'staff.statusFailed': { it: 'Stato non salvato, riprova.', en: 'Status not saved, please try again.' },
  'staff.emailStillWorks': {
    it: 'Le risposte via email funzionano come prima: puoi usare indifferentemente il sito o l\'email.',
    en: 'Replying by email still works as before: you can use either the site or email.',
  },
  'staff.allTickets': { it: 'Tutti i ticket', en: 'All tickets' },
  'staff.notFoundText': { it: 'Non esiste un ticket {id}.', en: 'There is no ticket {id}.' },
  'staff.loginText': {
    it: 'Accedi con l\'account del team per vedere i ticket.',
    en: 'Sign in with your team account to see the tickets.',
  },
  'staff.checkFailed': { it: 'Impossibile verificare l\'accesso', en: 'Could not check your access' },
  'staff.reservedTitle': { it: 'Area riservata al team', en: 'Team-only area' },
  'staff.reservedText': {
    it: 'Questo account non fa parte dello staff di Discount Searcher.',
    en: 'This account is not part of the Discount Searcher staff.',
  },
  'staff.myTickets': { it: 'I miei ticket', en: 'My tickets' },
  'login.codeTitle': { it: 'Controlla la tua email', en: 'Check your email' },
  'login.codeText': {
    it: 'Per sicurezza ti abbiamo mandato un codice di 6 cifre a <strong>{email}</strong>. Vale {minutes} minuti.',
    en: 'For your security we sent a 6-digit code to <strong>{email}</strong>. It is valid for {minutes} minutes.',
  },
  'login.codeNotSent': {
    it: 'Non siamo riusciti a inviare l\'email con il codice. Riprova fra qualche istante con "Invia un nuovo codice".',
    en: 'We could not send the email with the code. Try again in a moment with "Send a new code".',
  },
  'login.codeLabel': { it: 'Codice di verifica', en: 'Verification code' },
  'login.codeSubmit': { it: 'Verifica e accedi', en: 'Verify and sign in' },
  'login.codeInvalid': { it: 'Il codice è fatto di 6 cifre.', en: 'The code is made of 6 digits.' },
  'login.codeResend': { it: 'Invia un nuovo codice', en: 'Send a new code' },
  'login.codeResendIn': { it: 'Nuovo codice fra {seconds} s', en: 'New code in {seconds} s' },
  'login.codeResent': { it: 'Ti abbiamo mandato un nuovo codice.', en: 'We sent you a new code.' },
  'login.codeBack': { it: 'Torna indietro', en: 'Go back' },
  'login.codeSpam': {
    it: 'Non la trovi? Guarda anche nella cartella Spam. Se non sei stato tu a inserire la password, cambiala dall\'app.',
    en: 'Can\'t find it? Check your Spam folder too. If you did not enter the password yourself, change it from the app.',
  },
  'login.showPassword': { it: 'Mostra', en: 'Show' },
  'login.hidePassword': { it: 'Nascondi', en: 'Hide' },

  // --- Elenco dei ticket -----------------------------------------------------
  'list.emptyTitle': { it: 'Non hai ancora aperto nessun ticket', en: 'You have not opened any ticket yet' },
  'list.emptyText': {
    it: 'Quando avrai bisogno di aiuto, i ticket che apri compariranno qui insieme al loro stato.',
    en: 'When you need help, the tickets you open will appear here with their status.',
  },
  'list.firstTicket': { it: 'Apri il primo ticket', en: 'Open your first ticket' },
  'list.noTickets': { it: 'Nessun ticket.', en: 'No tickets.' },
  'list.noMatchTitle': { it: 'Nessun ticket corrisponde ai filtri', en: 'No ticket matches the filters' },
  'list.noMatchText': {
    it: 'Cambia lo stato selezionato o il testo cercato.',
    en: 'Change the selected status or the text you searched for.',
  },
  'list.clearFilters': { it: 'Azzera i filtri', en: 'Clear filters' },
  'list.countOne': { it: '{n} ticket mostrato.', en: '{n} ticket shown.' },
  'list.countMany': { it: '{n} ticket mostrati.', en: '{n} tickets shown.' },
  'list.loginRequired': { it: 'Accesso richiesto.', en: 'Sign-in required.' },
  'list.loadError': { it: 'Impossibile caricare i ticket', en: 'Could not load your tickets' },
  'list.all': { it: 'Tutti', en: 'All' },
  'list.category': { it: 'Categoria', en: 'Category' },
  'list.created': { it: 'Creato', en: 'Created' },
  'list.updated': { it: 'Aggiornato {when}', en: 'Updated {when}' },

  // --- Dettaglio del ticket ---------------------------------------------------
  'detail.you': { it: 'Tu', en: 'You' },
  'detail.teamRole': { it: 'Team Discount Searcher', en: 'Discount Searcher team' },
  'detail.messageFrom': { it: 'Messaggio di {author}', en: 'Message from {author}' },
  'detail.closedTitle': { it: 'Ticket chiuso.', en: 'Ticket closed.' },
  'detail.closedText': { it: 'Non è possibile rispondere.', en: 'You cannot reply to it.' },
  'detail.openAnother': { it: 'Apri un nuovo ticket', en: 'Open a new ticket' },
  'detail.ifAnother': { it: ' se hai un altro problema.', en: ' if you have another problem.' },
  'detail.replyLabel': { it: 'Rispondi', en: 'Reply' },
  'detail.replyPlaceholder': { it: 'Scrivi la tua risposta al team', en: 'Write your reply to the team' },
  'detail.replyFailed': { it: 'Risposta non inviata.', en: 'Reply not sent.' },
  'detail.sendReply': { it: 'Invia risposta', en: 'Send reply' },
  'detail.noPassword': { it: 'Non inserire mai la tua password.', en: 'Never type your password here.' },
  'detail.thread': { it: 'Conversazione', en: 'Conversation' },
  'detail.detailsTitle': { it: 'Dettagli del ticket', en: 'Ticket details' },
  'detail.id': { it: 'ID', en: 'ID' },
  'detail.status': { it: 'Stato', en: 'Status' },
  'detail.category': { it: 'Categoria', en: 'Category' },
  'detail.extra': { it: 'Informazioni aggiuntive', en: 'Additional information' },
  'detail.created': { it: 'Creato', en: 'Created' },
  'detail.updated': { it: 'Aggiornato', en: 'Updated' },
  'detail.statusMeaning': { it: 'Cosa significa lo stato', en: 'What the status means' },
  'detail.emailNote': {
    it: 'Quando il team risponde ricevi un\'email all\'indirizzo del tuo account, con il link a questa pagina.',
    en: 'When the team replies you get an email at your account address, with a link to this page.',
  },
  'detail.notFoundTitle': { it: 'Ticket non trovato', en: 'Ticket not found' },
  'detail.notFoundWithId': {
    it: 'Non esiste nessun ticket con ID <span class="ds-mono">{id}</span> fra i tuoi ticket.',
    en: 'There is no ticket with ID <span class="ds-mono">{id}</span> among yours.',
  },
  'detail.notFoundNoId': {
    it: 'Il collegamento non contiene nessun numero di ticket.',
    en: 'The link does not contain a ticket number.',
  },
  'detail.backToList': { it: 'Vai a I miei ticket', en: 'Go to My tickets' },
  'detail.loadError': { it: 'Impossibile caricare il ticket', en: 'Could not load the ticket' },
  'detail.ticketWord': { it: 'Ticket {id}', en: 'Ticket {id}' },
  'detail.loading': { it: 'Caricamento del ticket…', en: 'Loading the ticket…' },
  'detail.copyBeforeLogin': {
    it: 'Copia il tuo messaggio prima di <a href="{url}">accedere di nuovo</a>.',
    en: 'Copy your message before <a href="{url}">signing in again</a>.',
  },
  'detail.retryLater': { it: 'Riprova tra qualche istante.', en: 'Try again in a moment.' },
  'detail.replyEmpty': { it: 'Scrivi un messaggio prima di inviarlo.', en: 'Write a message before sending it.' },
  'detail.replyTooLong': {
    it: 'Il messaggio può avere al massimo {max} caratteri.',
    en: 'The message can be at most {max} characters long.',
  },
  'detail.docTitle': { it: '{id} · {subject} — Discount Searcher', en: '{id} · {subject} — Discount Searcher' },

  // --- Modulo dei ticket e delle candidature ---------------------------------
  'form.checkOne': { it: 'Controlla il campo evidenziato:', en: 'Check the highlighted field:' },
  'form.checkMany': { it: 'Controlla i {n} campi evidenziati:', en: 'Check the {n} highlighted fields:' },
  'form.sendFailed': { it: 'Non è stato possibile inviare il modulo.', en: 'The form could not be sent.' },
  'form.dataKept': {
    it: 'I dati inseriti sono ancora nel modulo: puoi riprovare.',
    en: 'Your data is still in the form: you can try again.',
  },
  'form.copyThenLogin': {
    it: 'Copia il testo che hai scritto, poi <a href="{url}">accedi di nuovo</a>.',
    en: 'Copy what you wrote, then <a href="{url}">sign in again</a>.',
  },
  'form.accountNotice': {
    it: 'Il ticket verrà aperto con l\'account <strong>{username}</strong>. Le risposte del team ti '
      + 'arriveranno anche via email.',
    en: 'The ticket will be opened with the account <strong>{username}</strong>. The team\'s replies '
      + 'will also reach you by email.',
  },
  'form.accountNoticeApply': {
    it: 'La candidatura verrà inviata con l\'account <strong>{username}</strong>. Le risposte del '
      + 'team ti arriveranno anche via email.',
    en: 'Your application will be sent with the account <strong>{username}</strong>. The team\'s '
      + 'replies will also reach you by email.',
  },

  // --- Apertura di un ticket ---------------------------------------------------
  'new.subjectRequired': { it: 'Inserisci un oggetto.', en: 'Enter a subject.' },
  'new.subjectShort': { it: 'L\'oggetto deve avere almeno 8 caratteri.', en: 'The subject must be at least 8 characters long.' },
  'new.subjectLong': { it: 'L\'oggetto può avere al massimo 120 caratteri.', en: 'The subject can be at most 120 characters long.' },
  'new.categoryRequired': { it: 'Seleziona una categoria.', en: 'Select a category.' },
  'new.descriptionRequired': { it: 'Descrivi il problema.', en: 'Describe the problem.' },
  'new.descriptionShort': {
    it: 'Aggiungi qualche dettaglio: servono almeno 30 caratteri.',
    en: 'Add some detail: at least 30 characters are needed.',
  },
  'new.descriptionLong': {
    it: 'La descrizione può avere al massimo 3000 caratteri.',
    en: 'The description can be at most 3000 characters long.',
  },
  'new.extraLong': {
    it: 'Le informazioni aggiuntive possono avere al massimo 1000 caratteri.',
    en: 'The additional information can be at most 1000 characters long.',
  },
  'new.labelSubject': { it: 'Oggetto', en: 'Subject' },
  'new.labelCategory': { it: 'Categoria', en: 'Category' },
  'new.labelDescription': { it: 'Descrizione', en: 'Description' },
  'new.labelExtra': { it: 'Informazioni aggiuntive', en: 'Additional information' },
  'new.labelFiles': { it: 'Allegati', en: 'Attachments' },
  'new.chooseCategory': { it: 'Seleziona una categoria', en: 'Select a category' },
  'new.suggestionsHint': {
    it: 'Scegli una categoria per vedere gli articoli collegati.',
    en: 'Pick a category to see the related articles.',
  },
  'new.newTab': { it: ' (si apre in una nuova scheda)', en: ' (opens in a new tab)' },
  'new.loginRequired': {
    it: 'Per aprire un ticket accedi con lo stesso username e la stessa password dell\'app Discount '
      + 'Searcher: così potrai seguirlo e ricevere le risposte via email.',
    en: 'To open a ticket, sign in with the same username and password as the Discount Searcher '
      + 'app: this way you can follow it and get replies by email.',
  },
  'new.meanwhile': {
    it: 'Nel frattempo puoi cercare una risposta nel <a href="{support}">Centro assistenza</a> o '
      + 'nelle <a href="{faq}">domande frequenti</a>.',
    en: 'Meanwhile you can look for an answer in the <a href="{support}">help centre</a> or in the '
      + '<a href="{faq}">FAQ</a>.',
  },
  'new.successTitle': { it: 'Ticket inviato', en: 'Ticket sent' },
  'new.successText': {
    it: 'Il team ha ricevuto la tua richiesta. Riceverai un\'email quando risponde, e puoi seguire '
      + 'lo stato e rispondere dalla pagina del ticket.',
    en: 'The team received your request. You will get an email when they reply, and you can follow '
      + 'the status and answer from the ticket page.',
  },
  'new.openTicket': { it: 'Apri il ticket', en: 'Open the ticket' },
  'new.attachmentsSent': { it: '{n} file inviato al team', en: '{n} file sent to the team' },
  'new.attachmentsSentMany': { it: '{n} file inviati al team', en: '{n} files sent to the team' },

  // --- Candidature ---------------------------------------------------------------
  'apply.roleRequired': { it: 'Scegli il ruolo per cui ti candidi.', en: 'Choose the role you are applying for.' },
  'apply.presentationRequired': { it: 'Scrivi qualcosa su di te.', en: 'Write something about yourself.' },
  'apply.presentationShort': {
    it: 'Raccontaci qualcosa in più: servono almeno 30 caratteri.',
    en: 'Tell us a bit more: at least 30 characters are needed.',
  },
  'apply.presentationLong': {
    it: 'La presentazione può avere al massimo 3000 caratteri.',
    en: 'Your introduction can be at most 3000 characters long.',
  },
  'apply.linksLong': { it: 'I link possono occupare al massimo 600 caratteri.', en: 'Links can be at most 600 characters long.' },
  'apply.availabilityLong': { it: 'La disponibilità può avere al massimo 200 caratteri.', en: 'Availability can be at most 200 characters long.' },
  'apply.labelRole': { it: 'Ruolo', en: 'Role' },
  'apply.labelPresentation': { it: 'Presentazione', en: 'Introduction' },
  'apply.labelLinks': { it: 'Link', en: 'Links' },
  'apply.labelAvailability': { it: 'Disponibilità', en: 'Availability' },
  'apply.chooseRole': { it: 'Scegli un ruolo', en: 'Choose a role' },
  'apply.roleHint': {
    it: 'Scegli un ruolo per vedere di cosa si occupa e com\'è la prova.',
    en: 'Choose a role to see what it does and what the trial task looks like.',
  },
  'apply.trial': { it: 'La prova:', en: 'The trial task:' },
  'apply.loginRequired': {
    it: 'La candidatura diventa un ticket legato al tuo account: accedi con lo stesso username e la '
      + 'stessa password dell\'app Discount Searcher. Se non hai un account, scarica l\'app e creane '
      + 'uno: serve un indirizzo Gmail.',
    en: 'Your application becomes a ticket linked to your account: sign in with the same username '
      + 'and password as the Discount Searcher app. If you do not have an account, download the app '
      + 'and create one: a Gmail address is required.',
  },
  'apply.meanwhile': {
    it: 'Intanto puoi leggere i ruoli aperti in <a href="{jobs}">Lavora con noi</a>.',
    en: 'Meanwhile you can read the open roles in <a href="{jobs}">Join the team</a>.',
  },
  'apply.successTitle': { it: 'Candidatura inviata', en: 'Application sent' },
  'apply.successText': {
    it: 'Il team l\'ha ricevuta. Il prossimo passo è la prova pratica: te la assegniamo rispondendo '
      + 'a questo ticket, e riceverai un\'email quando succede.',
    en: 'The team received it. The next step is the trial task: we assign it by replying to this '
      + 'ticket, and you will get an email when that happens.',
  },
  'apply.openApplication': { it: 'Apri la candidatura', en: 'Open the application' },
  'apply.role': { it: 'Ruolo', en: 'Role' },
  'apply.number': { it: 'Numero', en: 'Number' },
  'apply.attachments': { it: 'Allegati', en: 'Attachments' },
  'apply.subject': { it: 'Candidatura — {role}', en: 'Application — {role}' },
  'apply.extraRole': { it: 'Ruolo: {role}', en: 'Role: {role}' },
  'apply.extraAvailability': { it: 'Disponibilità: {value}', en: 'Availability: {value}' },
  'apply.extraLinks': { it: 'Link: {value}', en: 'Links: {value}' },

  // --- Allegati ---------------------------------------------------------------------
  'files.notAllowed': { it: 'non è un PDF o un\'immagine', en: 'is not a PDF or an image' },
  'files.empty': { it: 'è vuoto', en: 'is empty' },
  'files.tooBig': { it: 'supera {limit}', en: 'is larger than {limit}' },
  'files.remove': { it: 'Rimuovi', en: 'Remove' },
  'files.removeAria': { it: 'Rimuovi {name}', en: 'Remove {name}' },
  'files.tooMany': {
    it: 'Puoi allegare al massimo {limit} file: togline {extra}.',
    en: 'You can attach at most {limit} files: remove {extra}.',
  },
  'files.problem': { it: '"{name}" {problem}: toglilo dall\'elenco.', en: '"{name}" {problem}: remove it from the list.' },
  'files.totalTooBig': { it: 'Gli allegati insieme superano {limit}.', en: 'The attachments together are larger than {limit}.' },
  'files.bytes': { it: '{n} byte', en: '{n} bytes' },
  //Separatore dei decimali: "2,1 MB" in italiano, "2.1 MB" in inglese
  'files.decimalSep': { it: ',', en: '.' },

  // --- Centro assistenza ---------------------------------------------------------------
  'support.searchResults': { it: 'Risultati della ricerca', en: 'Search results' },
  'support.noResults': { it: 'Nessun risultato trovato.', en: 'No results found.' },
  'support.resultsNone': { it: 'nessun risultato', en: 'no results' },
  'support.articles': { it: '{n} articoli', en: '{n} articles' },
  'support.article': { it: '{n} articolo', en: '{n} article' },
  'support.faqTitle': { it: 'Domande frequenti', en: 'Frequently asked questions' },
  'support.recentLoginHint': {
    it: 'Accedi con il tuo account dell\'app per vedere i tuoi ticket.',
    en: 'Sign in with your app account to see your tickets.',
  },
  'support.noTicketsTitle': { it: 'Nessun ticket', en: 'No tickets' },
  'support.noTicketsText': {
    it: 'Quando aprirai un ticket lo troverai qui.',
    en: 'When you open a ticket you will find it here.',
  },

  'support.noResultFor': { it: 'Nessun risultato per “{q}”', en: 'No results for “{q}”' },
  'support.tryOther': {
    it: 'Prova con parole diverse, sfoglia le categorie qui sotto oppure '
      + '<a href="{url}">apri un ticket</a>.',
    en: 'Try different words, browse the categories below, or '
      + '<a href="{url}">open a ticket</a>.',
  },
  'support.countOne': { it: '{n} risultato trovato.', en: '{n} result found.' },
  'support.countMany': { it: '{n} risultati trovati.', en: '{n} results found.' },

  // --- Categoria dell'assistenza --------------------------------------------------------
  'category.notFoundTitleTag': {
    it: 'Categoria non trovata — Centro assistenza — Discount Searcher',
    en: 'Category not found — Help centre — Discount Searcher',
  },
  'category.notFoundTitle': { it: 'Categoria non trovata', en: 'Category not found' },
  'category.notFoundText': {
    it: 'Il collegamento che hai seguito non corrisponde a nessuna categoria dell\'assistenza.',
    en: 'The link you followed does not match any help centre category.',
  },
  'category.backToSupport': { it: 'Torna al Centro assistenza', en: 'Back to the help centre' },
  'category.noAnswer': { it: 'Non hai trovato la risposta?', en: 'Did not find the answer?' },
  'category.openTicket': { it: 'Apri un ticket', en: 'Open a ticket' },
  'category.faq': { it: 'Domande frequenti', en: 'FAQ' },
  'category.onThisPage': { it: 'In questa pagina', en: 'On this page' },
  'category.otherCategories': { it: 'Altre categorie', en: 'Other categories' },
  'category.nav': { it: 'Navigazione della categoria', en: 'Category navigation' },
  'category.docTitle': {
    it: '{title} — Centro assistenza — Discount Searcher',
    en: '{title} — Help centre — Discount Searcher',
  },
  'category.ticketPrefilled': {
    it: 'Apri un ticket in questa categoria: il modulo sarà già impostato su “{title}”.',
    en: 'Open a ticket in this category: the form will already be set to “{title}”.',
  },

  // --- Domande frequenti -------------------------------------------------------------------
  'faq.noMatchTitle': { it: 'Nessuna domanda corrisponde alla ricerca', en: 'No question matches your search' },
  'faq.noMatchText': {
    it: 'Prova con parole diverse, mostra tutte le categorie oppure apri un ticket per chiedere '
      + 'direttamente al team.',
    en: 'Try different words, show every category, or open a ticket to ask the team directly.',
  },
  'faq.showAll': { it: 'Mostra tutte le domande', en: 'Show every question' },
  'faq.none': { it: 'Nessuna domanda trovata.', en: 'No question found.' },
  'faq.countOne': { it: '{n} domanda trovata.', en: '{n} question found.' },
  'faq.countMany': { it: '{n} domande trovate.', en: '{n} questions found.' },
  'faq.all': { it: 'Tutte', en: 'All' },
  'faq.openTicket': { it: 'Apri un ticket', en: 'Open a ticket' },

  // --- Lavora con noi ------------------------------------------------------------------------
  'jobs.noRolesTitle': { it: 'Al momento nessun ruolo aperto', en: 'No open roles right now' },
  'jobs.noRolesText': {
    it: 'Le posizioni vengono pubblicate qui quando il team ne apre una.',
    en: 'Open positions appear here when the team opens one.',
  },
  'jobs.whatYouDo': { it: 'Di cosa ti occuperesti', en: 'What you would do' },
  'jobs.whatYouSend': { it: 'Cosa ci mandi', en: 'What you send us' },
  'jobs.apply': { it: 'Candidati', en: 'Apply' },

  // --- Pagina iniziale --------------------------------------------------------------------
  'home.storeMeta': { it: 'Offerte tramite CheapShark', en: 'Deals via CheapShark' },

  // --- Finestra dell'app ricostruita nella home ------------------------------------------------
  'preview.history': { it: 'Cronologia', en: 'History' },
  'preview.signOut': { it: 'Esci dal profilo', en: 'Sign out' },
  'preview.search': { it: 'Cerca', en: 'Search' },
  'preview.searchPlaceholder': { it: 'Cerca un gioco...', en: 'Search for a game...' },
  'preview.store': { it: 'Store', en: 'Store' },
  'preview.genre': { it: 'Genere', en: 'Genre' },
  'preview.discount': { it: 'Sconto', en: 'Discount' },
  'preview.all': { it: 'Tutti', en: 'All' },
  'preview.link': { it: 'Link ↗', en: 'Open ↗' },
  'preview.sideLink': { it: 'Link', en: 'Open' },
  'preview.user': { it: '● utente', en: '● user' },
  'preview.note': {
    it: 'Ricostruzione dell\'interfaccia · titoli e prezzi di esempio',
    en: 'Reconstruction of the interface · sample titles and prices',
  },
  'preview.empty': { it: 'Nessun risultato trovato con questi filtri', en: 'No results with these filters' },
  'preview.credits': { it: 'Dati sulle offerte forniti da CheapShark', en: 'Deal data provided by CheapShark' },
  'preview.alt': {
    it: 'Ricostruzione dell\'interfaccia di Discount Searcher: cronologia a sinistra, ricerca e '
      + 'filtri Store, Genere e Sconto in alto, elenco delle offerte al centro.',
    en: 'Reconstruction of the Discount Searcher window: history on the left, search and the Store, '
      + 'Genre and Discount filters on top, list of deals in the middle.',
  },
};
