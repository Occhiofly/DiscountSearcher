/**
 * Domande frequenti.
 *
 * Le risposte descrivono soltanto comportamenti reali dell'applicazione e del
 * suo server. `tags` serve alla ricerca interna: parole che una persona
 * potrebbe digitare ma che non compaiono nel testo della domanda.
 */

export const FAQ_GROUPS = [
  {
    id: 'prodotto',
    title: 'Il prodotto',
    items: [
      {
        id: 'faq-cos-e',
        q: 'Che cos\'è Discount Searcher?',
        tags: ['cosa', 'app', 'programma', 'windows', 'desktop'],
        a: `<p>È un'applicazione desktop per Windows che mostra le offerte sui videogiochi di
            quattro negozi digitali: Steam, Epic Games Store, GOG e Humble Store.</p>
            <p>Scegli il negozio, imposti i criteri — per esempio giochi di ruolo scontati almeno
            del 50% su Steam — e ottieni la lista corrispondente, senza aprire il sito del negozio.
            Per confrontare un altro negozio basta sceglierlo dal menu e cercare di nuovo.</p>`,
      },
      {
        id: 'faq-negozi',
        q: 'Quali negozi sono supportati?',
        tags: ['steam', 'epic', 'gog', 'humble', 'store', 'negozi'],
        a: `<p>La ricerca copre <strong>Steam</strong>, <strong>Epic Games Store</strong>,
            <strong>GOG</strong> e <strong>Humble Store</strong>.</p>
            <p>Il negozio si sceglie dal menu a tendina prima della ricerca. Discount Searcher è
            un progetto indipendente e non è affiliato a nessuno di questi negozi.</p>`,
      },
      {
        id: 'faq-dati',
        q: 'Da dove arrivano le informazioni sulle offerte?',
        tags: ['cheapshark', 'api', 'prezzi', 'fonte', 'dati'],
        a: `<p>Le offerte arrivano dall'<strong>API pubblica di CheapShark</strong>, un servizio
            che raccoglie gli sconti di più negozi digitali. I generi dei giochi arrivano
            dall'<strong>API pubblica di Steam</strong>.</p>
            <p>Discount Searcher non stabilisce i prezzi e non vende nulla: mostra quello che
            queste fonti riportano. Il prezzo valido resta sempre quello indicato dal negozio al
            momento dell'acquisto.</p>`,
      },
      {
        id: 'faq-acquisto',
        q: 'Posso comprare i giochi dall\'applicazione?',
        tags: ['comprare', 'acquisto', 'pagamento', 'carta'],
        a: `<p>No. L'applicazione apre l'offerta nel browser, sulla pagina del negozio:
            l'acquisto avviene lì.</p>
            <p>Discount Searcher non gestisce pagamenti e non chiede mai dati di pagamento.</p>`,
      },
      {
        id: 'faq-sistemi',
        q: 'Su quali sistemi operativi funziona?',
        tags: ['mac', 'linux', 'windows', 'sistema', 'compatibilità'],
        a: `<p>L'applicazione è distribuita come eseguibile per <strong>Windows</strong> e non
            richiede l'installazione di Python.</p>
            <p>Non sono disponibili versioni per altri sistemi operativi.</p>`,
      },
    ],
  },
  {
    id: 'account',
    title: 'Account',
    items: [
      {
        id: 'faq-serve-account',
        q: 'Serve un account per usare l\'applicazione?',
        tags: ['registrazione', 'obbligatorio', 'account'],
        a: `<p>Sì: l'applicazione si apre sulla schermata di accesso e registrazione, e alla
            ricerca si arriva dopo aver effettuato l'accesso.</p>
            <p>L'account è anche ciò che rende possibile la cronologia condivisa fra computer
            diversi.</p>`,
      },
      {
        id: 'faq-registrazione',
        q: 'Cosa serve per registrarsi?',
        tags: ['registrarsi', 'iscrizione', 'gmail', 'data di nascita'],
        a: `<p>Username, una password di almeno 8 caratteri, un indirizzo email che termini in
            <code>@gmail.com</code> e la data di nascita.</p>
            <p>Subito dopo la registrazione l'account non è ancora attivo: va confermato con il
            codice di verifica inviato per email.</p>
            <p>Puoi registrarti <a href="registrati.html">dal sito</a> oppure dall'applicazione:
            l'account è lo stesso. Dal sito è l'unico modo se non usi Windows.</p>`,
      },
      {
        id: 'faq-verifica',
        q: 'Come funziona la verifica dell\'email?',
        tags: ['codice', '6 cifre', 'verifica', 'email', 'attivazione'],
        a: `<p>Alla registrazione il server invia all'indirizzo indicato un codice numerico di
            <strong>6 cifre</strong>, valido per <strong>15 minuti</strong>. Inserendolo nella
            schermata di verifica, l'account viene attivato.</p>
            <p>Se il codice non arriva o scade, dalla stessa schermata puoi chiederne uno nuovo.
            Un account non verificato non può accedere: provandoci con credenziali corrette,
            l'applicazione richiede automaticamente un nuovo codice e torna alla verifica.</p>`,
      },
      {
        id: 'faq-piu-computer',
        q: 'Posso usare il mio account su un altro computer?',
        tags: ['due computer', 'portatile', 'dispositivi', 'sincronizzazione'],
        a: `<p>Sì. L'account non è legato al computer su cui è stato creato: installa
            l'applicazione altrove e accedi con le stesse credenziali.</p>
            <p>Anche la <strong>cronologia</strong> dei giochi aperti ti segue, perché è
            salvata insieme all'account e non nel singolo computer.</p>`,
      },
      {
        id: 'faq-password-dimenticata',
        q: 'Cosa succede se dimentico la password?',
        tags: ['recupero', 'reset', 'dimenticata', 'password'],
        a: `<p>Dalla schermata di accesso puoi avviare il recupero password inserendo il tuo
            username. Se l'account esiste, ricevi per email un codice a 6 cifre valido 15 minuti,
            da usare insieme alla nuova password.</p>
            <p>Una volta reimpostata, <strong>tutti</strong> i computer collegati a quell'account
            vengono disconnessi e ricevi un'email di conferma.</p>`,
      },
      {
        id: 'faq-modifica-dati',
        q: 'Come modifico username, email o password?',
        tags: ['cambiare', 'profilo', 'modificare', 'dati'],
        a: `<p>Dal pannello <strong>Profilo</strong> dell'applicazione. Lasciando vuoto il campo
            della nuova password, la password resta invariata.</p>
            <p>Ogni modifica richiede di reinserire la <strong>password attuale</strong> come
            conferma, e viene notificata per email all'indirizzo che l'account aveva prima del
            cambiamento. Cambiando la password, gli altri computer collegati vengono disconnessi.</p>
            <p>Per l'<strong>email</strong> la password non basta: ti mandiamo due codici, uno
            all'indirizzo attuale e uno a quello nuovo, da inserire nell'app (versione 1.0.4 o
            successiva). Così chi scoprisse la tua password non potrebbe mettere la sua email al
            posto della tua. Se non hai più accesso al vecchio indirizzo, apri un ticket.</p>`,
      },
    ],
  },
  {
    id: 'sicurezza',
    title: 'Sicurezza',
    items: [
      {
        id: 'faq-codice',
        q: 'Il codice dell\'applicazione è pubblico?',
        tags: ['codice', 'sorgente', 'github', 'open source', 'licenza'],
        a: `<p>Sì, si può leggere: il progetto sta su
            <a href="https://github.com/Occhiofly/DiscountSearcher" rel="noopener">GitHub</a>, insieme alla documentazione che
            spiega come è fatto e perché.</p>
            <p>Non è però open source: vale una licenza proprietaria, tutti i diritti riservati.
            Puoi guardare e studiare il codice; copiarlo, ridistribuirlo o farne una tua versione no.
            L'applicazione resta gratuita per chiunque.</p>`,
      },
      {
        id: 'faq-protezione',
        q: 'Come è protetto il mio account?',
        tags: ['sicurezza', 'password', 'hash', 'protezione', 'tentativi'],
        a: `<p>Le misure effettivamente presenti sono:</p>
            <ul>
              <li>la password non viene mai conservata in chiaro: sul server resta solo un
                  valore derivato, con un elemento casuale diverso per ogni utente;</li>
              <li>ogni modifica ai dati dell'account richiede la password attuale e genera
                  un'email di notifica all'indirizzo precedente; per cambiare l'email servono anche
                  due codici, inviati al vecchio e al nuovo indirizzo;</li>
              <li>dopo diversi tentativi di accesso falliti ravvicinati sullo stesso username,
                  l'accesso viene bloccato temporaneamente;</li>
              <li>ogni accesso crea una sessione revocabile lato server, senza dover cambiare
                  la password.</li>
            </ul>
            <p>Nessun sistema è immune da ogni rischio: una password diversa da quelle usate
            altrove resta la protezione più efficace.</p>`,
      },
      {
        id: 'faq-email-notifica',
        q: 'Ho ricevuto un\'email di modifica che non ho richiesto',
        tags: ['notifica', 'email', 'accesso non autorizzato', 'sospetto'],
        a: `<p>L'email di notifica viene inviata ogni volta che username, email o password
            vengono modificati dal pannello Profilo.</p>
            <p>Se non sei stato tu, cambia subito la password: la modifica disconnette
            automaticamente tutti gli altri computer collegati all'account. Poi apri un ticket
            indicando la data e l'ora indicate nell'email ricevuta.</p>`,
      },
      {
        id: 'faq-dati-raccolti',
        q: 'Quali dati vengono conservati?',
        tags: ['privacy', 'dati personali', 'cronologia', 'conservazione'],
        a: `<p>Per il funzionamento dell'account il server conserva username, indirizzo email,
            data di nascita, il valore derivato dalla password e la cronologia dei giochi che
            hai aperto.</p>
            <p>Per ogni accesso viene salvata una sessione con data e ora e il nome del
            dispositivo: per l'app è il <strong>nome del computer</strong> impostato in Windows,
            per il sito la dicitura "Sito web".</p>
            <p>Se apri un ticket o invii una candidatura, i messaggi restano nel ticket. Il team
            li riceve anche via email, quindi una copia resta nella casella Gmail del progetto,
            insieme agli eventuali file allegati (che il server non conserva).</p>
            <p>Non vengono richiesti né conservati dati di pagamento, perché gli acquisti
            avvengono interamente sul sito del negozio.</p>
            <p>Tempi di conservazione, servizi usati e come chiedere la cancellazione sono
            nell'<a href="privacy.html">informativa sulla privacy</a>.</p>`,
      },
    ],
  },
  {
    id: 'assistenza',
    title: 'Assistenza',
    items: [
      {
        id: 'faq-contatto',
        q: 'Come contatto l\'assistenza?',
        tags: ['contatto', 'ticket', 'aiuto', 'supporto', 'parlare', 'accedi', 'login'],
        a: `<p>Apri un ticket dal Centro assistenza, accedendo con lo stesso username e la
            stessa password dell'app; per sicurezza il sito ti chiede poi un codice che arriva
            via email. Scegli la categoria più vicina al tuo problema e descrivi cosa succede.</p>
            <p>Quando il team risponde ricevi un'email con il link al ticket; puoi seguire la
            conversazione e rispondere dalla sezione <strong>I miei ticket</strong>.</p>
            <p>Se non riesci ad accedere al tuo account, consulta prima le guide su
            <a href="assistenza-categoria.html?c=accesso">accesso</a> e
            <a href="assistenza-categoria.html?c=recupero-password">recupero password</a>.</p>
            <p>Non inserire mai la password in un ticket: non serve a chi ti assiste.</p>`,
      },
      {
        id: 'faq-tempi',
        q: 'In quanto tempo ricevo una risposta?',
        tags: ['tempi', 'attesa', 'risposta', 'quando'],
        a: `<p>Discount Searcher è un progetto indipendente portato avanti da un gruppo molto
            piccolo: non esiste un tempo di risposta garantito.</p>
            <p>Una segnalazione completa — cosa stavi facendo, cosa ti aspettavi, il testo esatto
            dell'errore — riduce i passaggi necessari e quindi l'attesa.</p>`,
      },
      {
        id: 'faq-bug',
        q: 'Come segnalo un bug?',
        tags: ['bug', 'errore', 'problema', 'segnalazione', 'crash'],
        a: `<p>Apri un ticket nella categoria <strong>Segnalare un bug</strong> indicando cosa
            stavi facendo, cosa ti aspettavi, cosa è successo, il testo esatto di eventuali
            messaggi di errore e se il problema si ripete ogni volta.</p>
            <p>Puoi allegare fino a 3 file, per esempio uno screenshot dell'errore.</p>`,
      },
    ],
  },
];

/** Tutte le domande in un unico elenco, con il gruppo di appartenenza. */
export const allFaq = () =>
  FAQ_GROUPS.flatMap((group) =>
    group.items.map((item) => ({ ...item, groupId: group.id, groupTitle: group.title })),
  );
