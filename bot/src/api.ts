/**
 * Le chiamate all'API di Discount Searcher (api/main.py).
 *
 * Il bot parla SOLO con l'API, mai direttamente col database: il token del bot
 * sta su un server Discord pubblico, le credenziali del database no. Se un giorno
 * il token esce, si rigenera e finisce li'; gli account degli utenti non c'entrano.
 *
 * Ogni chiamata ha un tempo massimo: se l'API e' lenta o ferma, il comando risponde
 * lo stesso con il link al sito invece di lasciare l'utente a guardare "sta pensando".
 */
import { configurazione } from "./configurazione.js";

const ATTESA_MASSIMA_MS = 8000;

/** Quello che GET /status restituisce nella parte "app" (api/release.py). */
export interface VersioneApp {
  version: string;
  url: string;
  notes: string[];
}

export interface StatoServizio {
  maintenance: boolean;
  message: string | null;
  app: VersioneApp | null;
}

/**
 * Stato del servizio e ultima versione pubblicata, nella lingua richiesta.
 * Restituisce null se l'API non risponde: chi chiama decide come ripiegare.
 */
export async function statoServizio(lingua: string): Promise<StatoServizio | null> {
  try {
    const risposta = await fetch(`${configurazione.api}/status`, {
      headers: { "Accept-Language": lingua },
      signal: AbortSignal.timeout(ATTESA_MASSIMA_MS),
    });
    if (!risposta.ok) {
      console.warn(`GET /status ha risposto ${risposta.status}`);
      return null;
    }
    return (await risposta.json()) as StatoServizio;
  } catch (errore) {
    console.warn("GET /status non raggiungibile:", (errore as Error).message);
    return null;
  }
}
