# Discount Searcher — procedure del team

🇬🇧 [English version](DOCUMENTAZIONE-TEAM.en.md)

Come si gestisce il progetto giorno per giorno: i ticket di assistenza, l'area staff, la
pubblicazione di una versione nuova e la modalità manutenzione. Sono le procedure di chi ci
lavora; chi vuole capire com'è fatto il progetto trova tutto nel
**[README](README.md)** (o nella [English version](README.en.md)).

## Ticket di assistenza

Il Centro assistenza del sito permette agli utenti (collegati con lo stesso account dell'app) di aprire ticket. Lo staff riceve ogni ticket via email e **risponde direttamente a quella email**: il backend legge la casella Gmail del server tramite IMAP, riconosce le risposte dal codice `[DS-<numero>]` nell'oggetto e le aggiunge al ticket, avvisando l'utente.

Lo staff può rispondere in due modi, anche insieme:

- **Dall'account dell'app** (lo stesso di `GMAIL_ADDRESS`, da mettere in `SUPPORT_STAFF`): si accede a quella casella e si risponde alla notifica. Il server legge le risposte dalla cartella **Posta inviata**, dove può scrivere solo chi ha accesso all'account, ed esclude le proprie notifiche (contrassegnate con l'intestazione `X-DS-Notification`).
- **Da indirizzi diversi** elencati in `SUPPORT_STAFF`: le risposte arrivano nella Posta in arrivo del server e sono accettate solo se superano i controlli DMARC/DKIM registrati da Gmail, così nessuno può fingersi lo staff falsificando il mittente.

Le **candidature** della pagina "Lavora con noi" del sito usano lo stesso sistema: sono ticket con categoria `candidatura` e oggetto `Candidatura — <ruolo>`, quindi lo staff le riceve e risponde esattamente come per un ticket di assistenza. L'unica differenza è nell'email di conferma all'utente, che la chiama candidatura e non richiesta di assistenza. Ai ticket e alle candidature si possono allegare fino a 3 file (PDF o immagini, 10 MB in tutto), per esempio uno screenshot dell'errore: il server li controlla (`api/attachments.py`) e li allega all'email per lo staff, **senza salvarli** né sul server né nel database; nel ticket resta solo l'elenco dei nomi. I file che lo staff allega alle proprie risposte, invece, non arrivano all'utente: le istruzioni per la prova vanno scritte nel testo della risposta, o messe come link.

Gli indirizzi dello staff non vengono mai mostrati agli utenti: nel ticket compare solo il nome indicato in `SUPPORT_STAFF`. Come prima riga della risposta si può scrivere `#inlavorazione`, `#risolto` o `#chiuso` per cambiare lo stato del ticket.

**Area staff del sito** (`staff.html`, server `api/staff.py`): in alternativa all'email, il team vede tutti i ticket e le candidature con chi li ha aperti, risponde e cambia lo stato dal sito; l'utente riceve lo stesso avviso via email. Chi ne fa parte si decide con la variabile `STAFF_ACCOUNTS` su Render, con il **numero dell'account** e il nome da mostrare nelle risposte, per esempio `STAFF_ACCOUNTS=12:Marco, 15:Vittorio`. Il numero si trova nel SQL Editor di Supabase con `SELECT id, username FROM users WHERE username = '...';`. Si usa il numero e non l'email perché dal profilo l'email si può cambiare senza verificarla di nuovo: chiunque potrebbe scriversi quella del team. Per tutti gli altri gli indirizzi `/staff` rispondono 404. Nelle email di notifica allo staff c'è anche il link al ticket nell'area staff, e chi è dello staff trova il pulsante "Area staff" nella pagina "I miei ticket".

## Avviso di versione nuova

L'app **non si aggiorna da sola**, ma da sé sa dire quando è uscita una versione nuova. A
ogni avvio chiede `GET /status` (la stessa chiamata della manutenzione) e il server, oltre
allo stato, risponde con l'ultima versione pubblicata e le sue novità nella lingua della
richiesta (`api/release.py`, contenuto in `api/release.json`). Se la versione dell'app
(`version.py`) è più vecchia, compare un riquadro con l'elenco delle novità, il pulsante per
scaricare, "Più tardi" e "Non ricordarmelo per questa versione" (scelta salvata in
`settings.json`).

Niente email e nessun dato personale: l'avviso lo vede chi apre l'app, cioè proprio chi deve
aggiornare. Un'email a tutti gli utenti sarebbe un'altra cosa: l'informativa privacy dichiara
che non si inviano newsletter, e l'account Gmail del progetto ha un tetto giornaliero che
serve ai codici di verifica e di accesso.

**Per pubblicare una versione nuova**: alzare `APP_VERSION` in `version.py` (lo usano anche
l'eseguibile e lo User-Agent), scrivere versione e novità in `api/release.json`, ricompilare,
pubblicare il server e il sito con lo zip nuovo. Chi ha una versione precedente alla 1.0.8
non vede l'avviso: quella funzione non c'era ancora.

## Aggiornamenti: la modalità manutenzione

Quando il team aggiorna il progetto, sito e app si possono fermare insieme con un avviso
"Aggiornamento in corso", da **un solo interruttore** sul server.

**Accendere**: su Render, nelle variabili d'ambiente del servizio, aggiungi
`MAINTENANCE_MODE` con valore `1` e salva. Render riavvia il server (circa un minuto).
**Spegnere**: togli la variabile, o mettila a `0`.

Con la manutenzione accesa:

- **il sito** copre ogni pagina con l'avviso e non si può usare; se una pagina era già
  aperta, l'avviso compare alla prima richiesta al server;
- **l'app** all'avvio mostra l'avviso a tutta finestra; se era già aperta, lo mostra alla
  prima richiesta (ricerca nella cronologia, profilo, accesso). "Riprova" richiede lo stato e,
  a manutenzione finita, riprende da dove si era;
- **le versioni dell'app già installate** prima di questa funzione non conoscono l'avviso,
  ma il server risponde comunque "aggiornamento in corso" a ogni loro richiesta;
- `/health` continua a rispondere, perché Render lo usa per sapere se il server è vivo.

L'interruttore sta sul server di proposito: accenderlo e spegnerlo non richiede di
ripubblicare il sito né di ricompilare l'app. Se il server non risponde affatto (rete assente,
riavvio in corso), sito e app **non** mostrano l'avviso: un problema di rete non è una
manutenzione.

Ordine consigliato per un aggiornamento:

1. accendi `MAINTENANCE_MODE=1` su Render e aspetta il riavvio;
2. pubblica le modifiche (server, sito, app);
3. verifica che tutto funzioni;
4. spegni la manutenzione.

Il codice sta in `api/maintenance.py` (server), `web/assets/js/components/maintenance.js`
(sito) e nei metodi `_check_service_at_startup` / `_show_maintenance` di `main.py` (app).
