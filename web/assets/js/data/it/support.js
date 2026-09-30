/**
 * Contenuti del Centro assistenza: categorie e articoli.
 *
 * Ogni testo descrive solo comportamenti che l'applicazione ha davvero
 * (verificati su main.py, backend.py e api/main.py). Aggiungere una categoria
 * significa aggiungere una voce a CATEGORIES e i relativi articoli: le pagine
 * si aggiornano da sole.
 */

export const CATEGORIES = [
  {
    id: 'account',
    icon: 'user',
    title: 'Account',
    summary: 'Creare un account, modificare i propri dati, usarlo su più computer.',
    articles: [
      {
        id: 'creare-account',
        title: 'Creare un account',
        body: `<p>Per registrarti servono uno <strong>username</strong>, una
          <strong>password</strong> di almeno 8 caratteri, un indirizzo email che deve terminare in
          <code>@gmail.com</code> e la tua data di nascita.</p>
          <p>Subito dopo la registrazione l'account esiste ma non è ancora attivo:
          ricevi per email un codice di verifica a 6 cifre e vieni portato alla
          schermata dove inserirlo. Finché non lo inserisci non è possibile accedere.</p>
          <p>La registrazione si fa <a href="registrati.html">dal sito</a> o dall'applicazione,
          indifferentemente: l'account è lo stesso e vale per entrambi. L'applicazione è solo per
          Windows, quindi da Mac o Linux si passa dal sito; il Centro assistenza e i ticket
          funzionano da qualsiasi computer.</p>`,
      },
      {
        id: 'modificare-dati',
        title: 'Modificare username, email o password',
        body: `<p>Apri il pannello <strong>Profilo</strong> dell'applicazione facendo clic
          sul tuo nome utente nella barra laterale. Da lì puoi cambiare username, email e
          password. Se lasci vuoto il campo della nuova password, la password non viene toccata.</p>
          <p>Al salvataggio viene chiesta la <strong>password attuale</strong> come conferma:
          senza quella la modifica non viene applicata. A modifica avvenuta ricevi un'email
          di notifica all'indirizzo che l'account aveva <em>prima</em> del cambiamento.</p>
          <p>Se cambi l'<strong>email</strong>, dopo la password compare una schermata che chiede
          due codici di 6 cifre: uno arriva all'indirizzo attuale, l'altro a quello nuovo. Valgono
          15 minuti; l'email cambia solo quando li inserisci entrambi. Serve l'app 1.0.4 o
          successiva. Se non hai più accesso al vecchio indirizzo, apri un ticket.</p>
          <p>Se cambi la password, gli altri computer collegati a quell'account vengono
          disconnessi; resta collegato solo quello da cui hai fatto la modifica.</p>`,
      },
      {
        id: 'piu-computer',
        title: 'Usare lo stesso account su più computer',
        body: `<p>L'account non è legato al computer su cui l'hai creato. Installa
          l'applicazione su un altro computer e accedi con le stesse credenziali.</p>
          <p>Ritrovi anche la <strong>cronologia</strong> dei giochi che hai aperto, perché è
          salvata insieme all'account e non nel singolo computer.</p>`,
      },
    ],
  },
  {
    id: 'accesso',
    icon: 'key',
    title: 'Accesso',
    summary: 'Problemi in fase di login, credenziali rifiutate, tentativi bloccati.',
    articles: [
      {
        id: 'credenziali-errate',
        title: '"Username o password errati"',
        body: `<p>Questo messaggio compare sia quando l'username non esiste sia quando la
          password è sbagliata. È volutamente generico: distinguere i due casi permetterebbe a
          chiunque di scoprire quali username sono registrati.</p>
          <p>Controlla eventuali maiuscole e spazi iniziali o finali. Se non ricordi la
          password, usa il recupero password dalla schermata di accesso.</p>`,
      },
      {
        id: 'troppi-tentativi',
        title: '"Troppi tentativi falliti"',
        body: `<p>Dopo diversi tentativi di accesso falliti ravvicinati sullo stesso username,
          l'accesso viene bloccato temporaneamente. È una protezione contro chi prova molte
          password di seguito per indovinare quella giusta.</p>
          <p>Il messaggio indica fra quanto tempo puoi riprovare. Non serve fare nulla:
          trascorsa l'attesa, l'accesso torna disponibile. Un accesso riuscito azzera il conteggio.</p>`,
      },
      {
        id: 'accesso-automatico',
        title: 'Perché non mi viene richiesto il login ogni volta',
        body: `<p>Quando accedi, l'applicazione conserva sul computer un token della sessione.
          Al riavvio successivo controlla che sia ancora valido e, se lo è, apre direttamente la
          schermata di ricerca.</p>
          <p>Usando <strong>Esci dal profilo</strong> la sessione viene annullata sul server e al
          riavvio successivo l'accesso viene richiesto di nuovo.</p>`,
      },
    ],
  },
  {
    id: 'recupero-password',
    icon: 'lock',
    title: 'Recupero password',
    summary: 'Reimpostare la password quando non riesci più ad accedere.',
    articles: [
      {
        id: 'reimpostare-password',
        title: 'Reimpostare la password dimenticata',
        body: `<p>Dalla schermata di accesso apri il recupero password e inserisci il tuo
          username. Se l'account esiste, all'indirizzo email registrato viene inviato un codice a
          6 cifre.</p>
          <p>Inserisci il codice insieme alla nuova password. Il codice è valido per
          <strong>15 minuti</strong>: scaduto, va richiesto di nuovo.</p>
          <p>A password reimpostata, <strong>tutti</strong> i computer collegati a quell'account
          vengono disconnessi e ricevi un'email di conferma.</p>`,
      },
      {
        id: 'messaggio-generico-recupero',
        title: 'Perché la risposta è sempre la stessa',
        body: `<p>Il recupero password risponde sempre con lo stesso messaggio, anche se lo
          username inserito non esiste.</p>
          <p>Il motivo è di sicurezza: una risposta diversa nei due casi trasformerebbe questa
          funzione in un modo per scoprire quali username sono registrati, provandone molti di
          seguito.</p>`,
      },
    ],
  },
  {
    id: 'verifica-email',
    icon: 'mail',
    title: 'Verifica email',
    summary: 'Il codice a 6 cifre, la sua scadenza e come richiederne uno nuovo.',
    articles: [
      {
        id: 'come-funziona-codice',
        title: 'Come funziona il codice di verifica',
        body: `<p>Dopo la registrazione ricevi per email un codice numerico di 6 cifre, valido
          per <strong>15 minuti</strong>. Inserendolo nella schermata di verifica, l'account
          viene attivato.</p>
          <p>Il codice viene generato in modo casuale dal server e confrontato con una tecnica
          che non rivela informazioni sul valore corretto in base al tempo di risposta.</p>`,
      },
      {
        id: 'codice-non-arrivato',
        title: 'Il codice non è arrivato o è scaduto',
        body: `<p>Dalla schermata di verifica puoi chiedere l'invio di un nuovo codice: quello
          precedente viene sostituito.</p>
          <p>Controlla anche la cartella spam o promozioni della casella di posta, e verifica che
          l'indirizzo inserito in registrazione fosse scritto correttamente.</p>
          <p>Se l'indirizzo era sbagliato, il codice non potrà mai arrivare: crea un nuovo account
          con l'indirizzo giusto e un username diverso.</p>
          <p>Nota: i ticket di assistenza richiedono l'accesso, che è possibile solo dopo la
          verifica dell'email.</p>`,
      },
      {
        id: 'login-non-verificato',
        title: 'Accesso con account non ancora verificato',
        body: `<p>Se provi ad accedere con credenziali corrette ma l'email non è ancora
          confermata, l'applicazione richiede automaticamente un nuovo codice e ti riporta alla
          schermata di verifica, invece di mostrare un errore generico.</p>`,
      },
    ],
  },
  {
    id: 'applicazione',
    icon: 'windows',
    title: 'Applicazione',
    summary: 'Avvio, requisiti e messaggi di errore dell\'applicazione desktop.',
    articles: [
      {
        id: 'requisiti',
        title: 'Cosa serve per usare l\'applicazione',
        body: `<p>Discount Searcher è un'applicazione desktop per <strong>Windows</strong>,
          distribuita come eseguibile autonomo: non è necessario installare Python.</p>
          <p>Serve una connessione a internet attiva, perché offerte, generi e account vengono
          richiesti a servizi remoti ogni volta.</p>`,
      },
      {
        id: 'errore-connessione',
        title: '"Errore di connessione" durante la ricerca',
        body: `<p>Compare quando l'applicazione non riesce a raggiungere il servizio delle
          offerte. Verifica la connessione a internet e riprova.</p>
          <p>Se la connessione funziona e l'errore continua, il servizio remoto potrebbe essere
          momentaneamente non disponibile: riprova più tardi o apri un ticket indicando l'orario
          in cui è successo.</p>`,
      },
      {
        id: 'app-lenta',
        title: 'L\'applicazione sembra bloccata durante la ricerca',
        body: `<p>Durante una ricerca l'applicazione mostra "Ricerca in corso...". Con il filtro
          per genere attivo l'attesa è più lunga, perché il genere di ogni gioco va richiesto
          separatamente a Steam.</p>
          <p>I generi già richiesti restano in memoria per la sessione, quindi le ricerche
          successive sugli stessi giochi sono più rapide.</p>`,
      },
    ],
  },
  {
    id: 'offerte',
    icon: 'tag',
    title: 'Offerte e ricerca',
    summary: 'Da dove arrivano i prezzi, quali negozi sono coperti, come si apre un\'offerta.',
    articles: [
      {
        id: 'origine-dati',
        title: 'Da dove arrivano i prezzi',
        body: `<p>Le offerte provengono dall'<strong>API pubblica di CheapShark</strong>, un
          servizio che raccoglie gli sconti di più negozi digitali. I generi dei giochi arrivano
          dall'<strong>API pubblica di Steam</strong>.</p>
          <p>Discount Searcher non fissa i prezzi e non vende nulla: mostra quello che queste
          fonti riportano. Prezzi e disponibilità possono cambiare, e il valore corretto resta
          sempre quello indicato dal negozio.</p>`,
      },
      {
        id: 'aprire-offerta',
        title: 'Aprire un\'offerta',
        body: `<p>Ogni risultato ha un collegamento che apre l'offerta nel browser predefinito,
          sulla pagina del negozio corrispondente.</p>
          <p>L'acquisto avviene sempre sul sito del negozio. L'applicazione non gestisce
          pagamenti e non chiede mai dati di pagamento.</p>`,
      },
      {
        id: 'risultati-mancanti',
        title: 'Un gioco che mi aspettavo non compare',
        body: `<p>La ricerca non scorre tutto il catalogo del negozio: mostra le sue offerte
          <strong>più recenti</strong>, cioè quelle cambiate negli ultimi 7 giorni, fino a 50 per
          negozio. Un gioco in sconto da più tempo, o fuori da quelle 50, non compare anche se
          l'offerta è ancora valida.</p>
          <p>Se pensi che il gioco rientri fra le offerte recenti, prova a portare lo sconto
          minimo su "Tutti", il genere su "Tutti" e a svuotare il campo di ricerca.</p>
          <p>Un gioco senza uno sconto nel negozio scelto non compare fra i risultati.</p>`,
      },
    ],
  },
  {
    id: 'filtri',
    icon: 'filter',
    title: 'Filtri',
    summary: 'Negozio, genere, sconto minimo e titolo: come si combinano.',
    articles: [
      {
        id: 'come-combinare',
        title: 'Come si combinano i filtri',
        body: `<p>I filtri si applicano tutti insieme: il risultato mostra i giochi che
          rispettano contemporaneamente negozio, genere, sconto minimo e testo cercato.</p>
          <p>Impostare "Tutti" su genere o sconto significa non filtrare per quel criterio.
          Il campo di testo cerca all'interno del titolo del gioco, fra le offerte recenti del
          negozio scelto: non è una ricerca in tutto il catalogo.</p>`,
      },
      {
        id: 'filtro-genere',
        title: 'Perché il filtro per genere è più lento',
        body: `<p>Il genere non fa parte dei dati delle offerte: va chiesto a Steam gioco per
          gioco. Con il filtro attivo servono quindi più richieste di rete rispetto a una
          ricerca senza genere.</p>
          <p>Per ridurre l'attesa, il filtro sul titolo viene applicato prima di quello sul
          genere: i giochi già esclusi dal testo non vengono nemmeno richiesti a Steam.</p>`,
      },
    ],
  },
  {
    id: 'cronologia',
    icon: 'history',
    title: 'Cronologia',
    summary: 'I giochi che hai aperto e dove vengono conservati.',
    articles: [
      {
        id: 'cosa-registra',
        title: 'Cosa finisce in cronologia',
        body: `<p>Quando apri il collegamento di un'offerta, quel gioco viene aggiunto alla
          cronologia, visibile nella barra laterale dell'applicazione. Da lì puoi riaprirlo
          senza doverlo cercare di nuovo.</p>
          <p>La cronologia è legata all'account, non al computer: la ritrovi anche accedendo da
          un altro computer.</p>`,
      },
      {
        id: 'cronologia-vuota',
        title: 'La cronologia appare vuota',
        body: `<p>Se non si carica, l'elenco resta semplicemente vuoto: è una scelta voluta,
          per non bloccare l'uso dell'applicazione a causa di un problema secondario.</p>
          <p>Verifica la connessione e riapri l'applicazione. Se il problema resta, apri un
          ticket indicando quando è iniziato.</p>`,
      },
    ],
  },
  {
    id: 'bug',
    icon: 'bug',
    title: 'Segnalare un bug',
    summary: 'Cosa includere in una segnalazione perché sia utile.',
    articles: [
      {
        id: 'cosa-includere',
        title: 'Cosa includere nella segnalazione',
        body: `<p>Una segnalazione utile contiene:</p>
          <ul>
            <li>cosa stavi facendo quando è successo;</li>
            <li>cosa ti aspettavi e cosa è successo invece;</li>
            <li>il testo esatto di eventuali messaggi di errore, o uno screenshot allegato al ticket;</li>
            <li>se il problema si ripete ogni volta o è capitato una volta sola;</li>
            <li>i filtri impostati, se riguarda la ricerca.</li>
          </ul>
          <p>Non inserire mai la tua password in un ticket: non serve a chi ti assiste.</p>`,
      },
    ],
  },
  {
    id: 'altro',
    icon: 'help',
    title: 'Altro',
    summary: 'Domande che non rientrano nelle altre categorie.',
    articles: [
      {
        id: 'nessuna-categoria',
        title: 'La mia domanda non rientra in nessuna categoria',
        body: `<p>Apri un ticket scegliendo la categoria "Altro" e descrivi la situazione con le
          tue parole: il team legge tutti i ticket, qualunque sia la categoria.</p>`,
      },
    ],
  },
];

/** Argomenti messi in evidenza nella pagina iniziale dell'assistenza. */
export const POPULAR_TOPICS = [
  { label: 'Non ricevo il codice di verifica', href: 'assistenza-categoria.html?c=verifica-email#codice-non-arrivato' },
  { label: 'Ho dimenticato la password',       href: 'assistenza-categoria.html?c=recupero-password#reimpostare-password' },
  { label: 'Usare l\'account su due computer', href: 'assistenza-categoria.html?c=account#piu-computer' },
  { label: 'Da dove arrivano i prezzi',        href: 'assistenza-categoria.html?c=offerte#origine-dati' },
  { label: 'Il filtro per genere è lento',     href: 'assistenza-categoria.html?c=filtri#filtro-genere' },
  { label: 'Cambiare email o password',        href: 'assistenza-categoria.html?c=account#modificare-dati' },
];

/** Trova una categoria dal suo identificativo. */
export const findCategory = (id) => CATEGORIES.find((c) => c.id === id) || null;

/**
 * Elenco piatto di tutti gli articoli, con il riferimento alla categoria.
 * Usato dalla ricerca del Centro assistenza.
 */
export const allArticles = () =>
  CATEGORIES.flatMap((category) =>
    category.articles.map((article) => ({
      ...article,
      categoryId: category.id,
      categoryTitle: category.title,
      href: `assistenza-categoria.html?c=${category.id}#${article.id}`,
    })),
  );
