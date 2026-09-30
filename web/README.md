# Sito web di Discount Searcher

Sito statico ufficiale del progetto: presentazione del prodotto e Centro assistenza.
HTML + CSS + moduli JavaScript nativi: **nessuna dipendenza, nessun passaggio di build**.

## Avvio in locale

I moduli ES non funzionano aprendo i file con doppio clic (`file://`): serve un server.

```bash
cd web
python server.py
```

Poi apri <http://127.0.0.1:5510/>.

Usa `server.py` e non `python -m http.server`, per due motivi:

- invia `Cache-Control: no-cache`: senza, Chrome può continuare a mostrare la versione
  vecchia di un file JS o CSS appena modificato (se succede comunque: **Ctrl+F5**);
- serve le pagine anche senza `.html` (`/assistenza` → `assistenza.html`), come Netlify.
  Così in locale il sito si comporta come quello pubblicato;
- applica le intestazioni di sicurezza del file `_headers` (vedi sotto), come Netlify.

## Pubblicazione

Il sito è pubblicato su **Netlify** con il dominio <https://discountsearcher.it> (registrato su
Aruba, con i record DNS che puntano a Netlify; `www` e l'indirizzo `discountsearcher.netlify.app`
rimandano lì), con la cartella
`web` come directory di pubblicazione.

Netlify modifica l'HTML servito ("Pretty URLs"): i link `assistenza.html` diventano
`/assistenza`. Entrambe le forme funzionano, e il codice (`currentPage()` in
`services/utils.js`) le tratta come la stessa pagina.

Il server dell'API su Render accetta chiamate dal browser solo dai siti in `CORS_ORIGINS`:
lì deve esserci `https://discountsearcher.it`.

### Intestazioni di sicurezza (`_headers`)

Netlify applica a ogni pagina le intestazioni scritte in `_headers`: una
Content-Security-Policy (il browser carica ed esegue solo gli script del sito e parla solo
con il server dell'API), il divieto di mostrare il sito dentro pagine altrui e poche altre
regole. È una difesa in più per il token di sessione salvato nel browser.

**Se cambia l'indirizzo dell'API** (`API_BASE_URL` in `assets/js/services/config.js`),
va aggiornato anche `connect-src` in `_headers`, altrimenti il browser blocca login e
ticket. Lo stesso vale se si aggiungono script, font o immagini da altri siti.

### Anteprime e motori di ricerca

- `assets/img/og-image.png` e `og-image-en.png` (1200×630): l'immagine mostrata quando un
  link al sito viene condiviso, con il testo nella lingua della pagina. I meta tag `og:`
  sono nelle pagine pubbliche, italiane e inglesi, con indirizzi assoluti. Cambiando una
  delle due, cambia anche l'altra: stessa impaginazione, stesso logo, solo il testo
  diverso.
- `hreflang`: ogni pagina pubblica dichiara sé stessa e la gemella nell'altra lingua
  (`it`, `en`, `x-default` sull'italiano). Aggiungendo una pagina vanno messi in
  entrambe le versioni.
- `sitemap.xml`: elenco delle pagine pubbliche nelle due lingue. **Aggiungendo una
  categoria** in `assets/js/data/it/support.js` (e in `data/en/support.js`), aggiungi
  anche le sue due righe qui.
- `robots.txt`: consente tutto e indica la sitemap. Le pagine dei ticket non sono bloccate
  apposta: hanno già `noindex`, che un `Disallow` renderebbe illeggibile.

Cambiando dominio vanno aggiornati: `canonical` e `og:url`/`og:image` nelle pagine,
`sitemap.xml`, `robots.txt` e `CORS_ORIGINS` su Render.

## Pagine

| Italiano | Inglese (`en/`) | Contenuto |
|---|---|---|
| `index.html` | `en/index.html` | Home: hero, vetrina del prodotto, funzioni, come funziona, negozi, account e sicurezza, team e crediti, download |
| `assistenza.html` | `en/support.html` | Centro assistenza: ricerca, argomenti popolari, categorie, anteprima FAQ, ticket recenti |
| `assistenza-categoria.html?c=<id>` | `en/support-category.html?c=<id>` | Articoli di una categoria (gli `id` sono gli stessi nelle due lingue) |
| `faq.html` | `en/faq.html` | Domande frequenti con filtro e ancore (`faq.html#faq-verifica`) |
| `lavora-con-noi.html` | `en/jobs.html` | Lavora con noi: come funziona il provino, ruoli aperti, team, cosa sapere prima |
| `privacy.html` | `en/privacy.html` | Informativa privacy, collegata dal footer. Descrive quello che il software fa davvero: se cambiano dati raccolti, servizi esterni o tempi di conservazione (es. `api/session_cleanup.py`), va aggiornata insieme alla data in fondo, **in entrambe le lingue** |
| `candidatura.html?r=<ruolo>` | `en/apply.html?r=<ruolo>` | Invio della candidatura (apre un ticket) — richiede l'accesso |
| `accedi.html?next=<pagina>` | `en/login.html?next=<pagina>` | Accesso con l'account dell'app; dopo il login torna a `next` (solo pagine del sito) |
| `ticket-nuovo.html` | `en/ticket-new.html` | Apertura ticket (`?c=<id>` preimposta la categoria) — richiede l'accesso |
| `ticket-lista.html` | `en/tickets.html` | I miei ticket — richiede l'accesso |
| `ticket-dettaglio.html?id=<ID>` | `en/ticket-detail.html?id=<ID>` | Conversazione di un ticket — richiede l'accesso |

Le pagine inglesi stanno nella cartella `en/` e richiamano gli stessi CSS e gli stessi
script con percorsi assoluti (`/assets/...`).

## Struttura

```
assets/
  css/
    tokens.css      colori, tipografia, spaziature, raggi, movimento (unica fonte di verità)
    base.css        reset, tipografia, layout, accessibilità
    components.css  bottoni, card, form, badge, header, footer, accordion, stati
    pages.css       sezioni della home, finestra dell'app, Centro assistenza, ticket
  js/
    app.js          avvio comune (header, footer, sottonavigazione, icone, animazioni)
    components/     header, footer, icone, accordion, ricostruzione dell'app, team, UI e moduli dei ticket, allegati, barra della lingua
    data/
      it/           contenuti in italiano: navigazione, team, categorie e articoli, FAQ, ruoli aperti
      en/           gli stessi contenuti in inglese (stessi id, stessi nomi di variabile)
    i18n/ui.js      testi dell'interfaccia generati dagli script, nelle due lingue
    services/       config, client del backend, servizio ticket, lingua (`i18n.js`), contenuti (`content.js`), utilità
    pages/          uno script per pagina (gli stessi per italiano e inglese)
  img/              logo ufficiale e sue varianti, favicon, loghi dei negozi
en/                 le stesse pagine in inglese
```

## Le due lingue

Il sito esiste in italiano (cartella principale) e in inglese (`en/`). La lingua **non**
si sceglie con JavaScript: la decide l'indirizzo della pagina, che la dichiara nel suo
`<html lang="...">`. Così ogni lingua ha i suoi indirizzi, i motori di ricerca le trovano
entrambe e chi condivide un link condivide la lingua giusta.

- `services/i18n.js`: `LANG` (lingua della pagina), `t('chiave')` per i testi
  dell'interfaccia, `url('pagina')` per gli indirizzi, `otherLangUrl()` per il selettore
  nell'intestazione. **Aggiungendo una pagina** va aggiunta alla mappa `PAGES`.
- `i18n/ui.js`: tutti i testi scritti dagli script, con la versione italiana e inglese.
- `services/content.js`: carica `data/it/` o `data/en/` secondo la lingua e ripubblica
  i contenuti con gli stessi nomi. Le pagine importano sempre da qui, mai da `data/`.
- `components/lang-banner.js`: a chi ha il browser nell'altra lingua propone la versione
  corrispondente, senza cambiare pagina da solo.
- Date e orari seguono la lingua della pagina (`services/utils.js`).
- Il server risponde e manda le email nella lingua della pagina: `services/api.js`
  aggiunge l'intestazione `Accept-Language`.

**Aggiungendo un contenuto** va aggiunto nelle due lingue, mantenendo gli stessi `id`:
gli id finiscono nei link (`?c=filtri`) e nelle categorie dei ticket.

## Modificare i contenuti

Ogni file esiste due volte: `data/it/...` e `data/en/...`. Vanno modificati insieme.

- **Team** → `assets/js/data/it/team.js` e `data/en/team.js` (una voce per persona; `photo` facoltativo).
- **Articoli di assistenza e categorie** → `data/it/support.js`, `data/en/support.js`.
- **Domande frequenti** → `data/it/faq.js`, `data/en/faq.js`.
- **Ruoli aperti e passi del provino** → `data/it/jobs.js`, `data/en/jobs.js`.
- **Voci di menu e footer** → `data/it/site.js`, `data/en/site.js`.
- **Testi dell'interfaccia** (pulsanti, errori, stati) → `assets/js/i18n/ui.js`.

## Integrazione con il backend

- `services/api.js` contiene **solo** gli endpoint realmente presenti nel backend
  (`api/main.py` e `api/tickets.py`). Le pagine non chiamano mai `fetch` direttamente.
  Il server accetta chiamate dal browser solo dai siti elencati in `CORS_ORIGINS` su Render.
- `services/session.js`: dopo il login il token di sessione (lo stesso tipo dell'app
  desktop) è salvato nel `localStorage`. "Esci" lo revoca anche sul server.
- `services/tickets.js`: sistema ticket collegato al backend. Ogni errore arriva alle
  pagine come `TicketsError` con un `kind` (`auth`, `notfound`, `closed`, `limit`,
  `network`, …): se la sessione è scaduta viene tolta dal browser e la pagina mostra
  l'invito ad accedere.

### Come funzionano i ticket

1. L'utente accede con l'account dell'app e apre un ticket.
2. Il server salva il ticket e manda un'email allo staff (`SUPPORT_STAFF` su Render) con
   oggetto `[DS-1001] …`, e una conferma all'utente.
3. Lo staff **risponde a quell'email**, accedendo alla casella dell'app (o da un indirizzo
   elencato in `SUPPORT_STAFF`). Il server legge la casella Gmail (ogni 2 minuti e ogni
   volta che un utente apre i suoi ticket), aggiunge la risposta al ticket e avvisa
   l'utente via email. Nel ticket compare il nome indicato in `SUPPORT_STAFF`, mai l'indirizzo.
4. Come prima riga della risposta lo staff può scrivere `#inlavorazione`, `#risolto` o
   `#chiuso` per cambiare lo stato.

Dettagli e sicurezza sono descritti in cima a `api/ticket_mail.py`.

### Lavora con noi (candidature)

`lavora-con-noi.html` (in inglese `en/jobs.html`) presenta i ruoli aperti;
`candidatura.html` (`en/apply.html`) è il modulo per candidarsi.
Non c'è un secondo sistema: la candidatura **apre un ticket**, quindi segue la stessa strada
(stesso account, stessa conversazione, stesse email dello staff). Il modulo compone il ticket
così:

| Campo del ticket | Contenuto |
|---|---|
| oggetto | `Candidatura — <ruolo>` |
| categoria | `candidatura` (unica per tutti i ruoli) |
| descrizione | la presentazione scritta dalla persona |
| informazioni aggiuntive | ruolo, disponibilità e link, una per riga |
| allegati (facoltativi) | fino a 3 file, PDF o immagini: vedi sotto |

Per aprire o chiudere un ruolo basta modificare `ROLES` in `assets/js/data/it/jobs.js` e
`data/en/jobs.js`: pagina,
menu a tendina del modulo e schede si aggiornano da soli. Aggiungere invece una nuova
*categoria* di ticket richiede anche una riga in `api/models.py` e in `api/tickets.py`,
altrimenti il server la rifiuta con un 422.

**Allegati.** Come il modulo "Apri un ticket", accetta fino a 3 file (PDF, PNG, JPG, GIF, WEBP), 4 MB l'uno e
10 MB in tutto (`components/file-picker.js`). Viaggiano in base64 dentro la stessa richiesta
e il server (`api/attachments.py`) li ricontrolla tutti, anche dal contenuto: un file
rinominato in `.pdf` che non è un PDF viene rifiutato. **I file non vengono salvati da
nessuna parte**: il server li allega all'email `[DS-…]` per lo staff e nel ticket resta solo
la riga "Allegati inviati al team: nome (dimensione)". Se quell'email non parte, la
candidatura non viene registrata e la persona vede il motivo, così nessun file va perso
senza che nessuno lo sappia.

Il modulo dell'assistenza e quello delle candidature condividono validazione, contatori e
invio (`components/ticket-form.js`): una correzione al comportamento dei moduli vale per
entrambi.

Limite noto: come i ticket, la candidatura richiede l'account dell'app. Chi non ce l'ha deve
prima scaricare l'applicazione e crearlo; la pagina lo dice prima di far scrivere qualcosa.

Limite noto: i ticket richiedono l'accesso, quindi chi non riesce ad accedere (email non
verificata, password dimenticata) non può aprirne uno. Per questi casi le guide
dell'assistenza rimandano alla verifica e al recupero password dall'app.

## Logo di Discount Searcher

| File | Uso |
|---|---|
| `assets/img/logo.png` | Logo a piena risoluzione (1254×1254). È la sorgente: da qui si generano gli altri. |
| `assets/img/logo-144.png` | Versione usata in header e footer (il logo si vede a 36 px; 144 copre gli schermi ad alta densità). |
| `assets/img/favicon.png` | Icona della scheda del browser, 64×64. |

Se il logo cambia, sostituisci `logo.png` e rigenera gli altri due:

```bash
python -c "from PIL import Image; s=Image.open('assets/img/logo.png').convert('RGBA'); s.resize((144,144), Image.LANCZOS).save('assets/img/logo-144.png', optimize=True); s.resize((64,64), Image.LANCZOS).save('assets/img/favicon.png', optimize=True)"
```

Non usare `logo.png` direttamente nelle pagine: pesa ~1,5 MB e verrebbe scaricato da
chiunque apra il sito, per mostrarlo a 36 px.

## Loghi dei negozi

I loghi in `assets/img/stores/` sono i tracciati SVG di
[Simple Icons](https://simpleicons.org) 16.31.0 (licenza CC0-1.0), ricolorati in un unico
colore chiaro. I marchi restano dei rispettivi proprietari e sono usati solo per indicare
dove sono disponibili le offerte: il footer lo dichiara insieme alla non affiliazione.
Per aggiornarli basta sostituire il file SVG con lo stesso nome.

## Download dell'applicazione

Il pulsante in `index.html#download` punta a `downloads/DiscountSearcher.zip`, servito dal
sito stesso. L'archivio contiene la cartella `DiscountSearcher/` con `DiscountSearcher.exe`.

Per pubblicare una nuova versione: dalla cartella principale lancia `python build_app.py`, che
compila l'app con Nuitka e sostituisce lo zip (vedi il README principale). Se la dimensione
cambia in modo evidente, aggiorna il testo "Archivio ZIP da 23 MB" in `index.html` e
"23 MB ZIP archive" in `en/index.html`.

Nota: l'archivio pesa ~23 MB e sta nel repository, quindi ogni versione pubblicata fa
crescere la cronologia git della stessa quantità. Se gli aggiornamenti diventano frequenti,
conviene spostare il file su un servizio di rilascio esterno e far puntare lì il pulsante.

## Segnaposto da completare
- **Screenshot**: la finestra mostrata nella home è una ricostruzione in HTML/CSS
  dell'interfaccia reale, con titoli e prezzi di esempio. Con screenshot veri si può
  sostituire, mantenendo la cornice.
