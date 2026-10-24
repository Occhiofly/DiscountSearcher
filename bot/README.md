# Bot Discord — Discount Searcher

Bot del server Discord, scritto in TypeScript con [discord.js](https://discord.js.org/).
Sta nella stessa repository del sito e dell'app perché legge le stesse cose: la versione
pubblicata, i link del sito, e in futuro i ticket e i punti delle partnership.

## Regola di sicurezza, prima di tutto

Il bot parla **solo con l'API** (`api/main.py`), mai direttamente con il database.

La repository è pubblica e il bot gira su un server Discord dove entra gente che non
conosciamo. Se un giorno il suo token esce, si rigenera dal Developer Portal e il danno
finisce lì. Se invece il bot avesse la stringa di Supabase, con lo stesso incidente
perderemmo gli account, le email e i ticket di tutti. Per lo stesso motivo il bot chiede
a Discord i soli intenti `Guilds`: non legge i messaggi delle persone.

Il token sta in `bot/.env`, che non è nella repository. Il gancio pre-commit
(`strumenti/controllo_segreti.py`) riconosce i token e i webhook di Discord e ferma il
commit se ne trova uno: per attivarlo, una volta sola nella tua copia,
`git config core.hooksPath .githooks`.

## Avviarlo in locale

Serve Node 20.12 o più recente (`node -v`).

```bash
cd bot
npm install
cp .env.example .env     # poi compila .env con i tuoi valori
npm run comandi          # registra i comandi slash: una volta, e a ogni modifica
npm run dev              # avvia il bot e lo riavvia quando cambi un file
```

Per le prove metti `DISCORD_GUILD_ID` in `.env`: i comandi compaiono subito sul tuo
server. Senza, vanno su tutti i server ma Discord può metterci fino a un'ora.

In produzione:

```bash
npm run build && npm start
```

## Comandi

| Comando | Cosa fa |
|---|---|
| `/download` | Manda il link per scaricare l'app con l'ultima versione e le novità, chieste a `GET /status`. Risponde in italiano o in inglese secondo la lingua di chi lo scrive. Se l'API non risponde manda comunque il link al sito |

## File

| File | Descrizione |
|---|---|
| `src/index.ts` | Avvio del bot: connessione, smistamento dei comandi, gestione degli errori |
| `src/registra-comandi.ts` | Registra i comandi slash su Discord (`npm run comandi`) |
| `src/configurazione.ts` | Legge `.env` e le variabili d'ambiente, si ferma subito se ne manca una |
| `src/api.ts` | Le chiamate all'API di Discount Searcher, con tempo massimo di attesa |
| `src/lingua.ts` | Italiano o inglese a partire dalla lingua del client Discord |
| `src/comandi/` | Un file per comando, più l'elenco in `index.ts` |
| `.env.example` | Modello da copiare in `.env` (il vero `.env` non va mai committato) |

Per aggiungere un comando: un file in `src/comandi/`, che esporta un oggetto `Comando`
(`definizione` + `esegui`), aggiunto alla lista in `src/comandi/index.ts`. Poi
`npm run comandi`.

## Dove farlo girare: ancora da decidere

Un bot con connessione gateway deve restare acceso sempre. Le possibilità:

- **Sul PC del developer**: gratis, va bene per provare, non per un server pubblico — il bot
  si spegne quando si spegne il computer.
- **Render, background worker**: circa 7 $ al mese. Il piano gratuito di Render **non va bene**:
  spegne il servizio dopo un quarto d'ora di inattività e il bot si disconnette.
- **Una VM gratuita** (per esempio Oracle Cloud Always Free): gratis, ma la macchina te la gestisci.

C'è una scorciatoia se al bot bastano i comandi slash: Discord può consegnarli via HTTP a un
indirizzo pubblico, senza connessione permanente, e in quel caso potrebbero vivere accanto
all'API che è già ospitata. Non va bene invece per il benvenuto automatico, i ruoli, i log di
moderazione o il conteggio automatico delle partnership, che hanno bisogno del gateway.
