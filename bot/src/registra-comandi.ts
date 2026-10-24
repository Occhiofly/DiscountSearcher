/**
 * Registra i comandi slash su Discord. Da lanciare a mano, con "npm run comandi",
 * la prima volta e ogni volta che cambi nome, descrizione o opzioni di un comando.
 * Non serve a ogni avvio del bot: Discord se li ricorda.
 *
 * Con DISCORD_GUILD_ID impostato i comandi vanno solo su quel server e compaiono
 * subito: e' il modo giusto per provare. Senza, vanno su tutti i server dove il bot
 * e' presente, ma Discord puo' metterci fino a un'ora a mostrarli.
 */
import { REST, Routes } from "discord.js";
import { comandi } from "./comandi/index.js";
import { configurazione } from "./configurazione.js";

const corpo = comandi.map((c) => c.definizione.toJSON());
const rest = new REST().setToken(configurazione.token);

const destinazione = configurazione.idServer
  ? Routes.applicationGuildCommands(configurazione.idApplicazione, configurazione.idServer)
  : Routes.applicationCommands(configurazione.idApplicazione);

try {
  await rest.put(destinazione, { body: corpo });
  const dove = configurazione.idServer ? `sul server ${configurazione.idServer}` : "su tutti i server";
  console.log(`Registrati ${corpo.length} comandi ${dove}: ${comandi.map((c) => "/" + c.definizione.name).join(", ")}`);
} catch (errore) {
  console.error("Registrazione non riuscita:", errore);
  process.exit(1);
}
