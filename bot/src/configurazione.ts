/**
 * Valori di configurazione del bot, letti da bot/.env (vedi .env.example).
 *
 * Il file .env viene caricato da Node senza librerie esterne. Se manca, i valori
 * si prendono comunque dalle variabili d'ambiente: e' il caso del server, dove
 * il token si imposta nel pannello dell'hosting e nessun file .env esiste.
 *
 * Se manca un valore obbligatorio il bot si ferma subito con un messaggio chiaro,
 * invece di partire e fallire piu' tardi con un errore di Discord.
 */
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const cartellaBot = join(dirname(fileURLToPath(import.meta.url)), "..");
const percorsoEnv = join(cartellaBot, ".env");

if (existsSync(percorsoEnv) && typeof process.loadEnvFile === "function") {
  process.loadEnvFile(percorsoEnv);
}

function obbligatorio(nome: string): string {
  const valore = process.env[nome]?.trim();
  if (!valore) {
    console.error(
      `Manca ${nome}. Copia bot/.env.example in bot/.env e compilalo,\n` +
        "oppure imposta la variabile d'ambiente sull'hosting."
    );
    process.exit(1);
  }
  return valore;
}

function facoltativo(nome: string, predefinito: string): string {
  return process.env[nome]?.trim() || predefinito;
}

export const configurazione = {
  token: obbligatorio("DISCORD_TOKEN"),
  idApplicazione: obbligatorio("DISCORD_APP_ID"),
  //Vuoto = comandi registrati su tutti i server (piu' lenti ad apparire)
  idServer: facoltativo("DISCORD_GUILD_ID", ""),
  api: facoltativo("API_URL", "https://api.discountsearcher.it").replace(/\/+$/, ""),
  sito: facoltativo("SITO_URL", "https://discountsearcher.it").replace(/\/+$/, ""),
  //Colore della barra laterale degli embed: lo stesso del sito e del regolamento
  colore: 5988006,
};
