/**
 * Avvio del bot Discord di Discount Searcher.
 *
 * Intenti: solo Guilds. Non legge i messaggi delle persone e non chiede gli intenti
 * "privilegiati" di Discord: per i comandi slash non servono, e meno permessi ha il
 * bot meno danni fa se qualcuno gli mette le mani addosso.
 *
 * Avvio in sviluppo:  npm run dev
 * Avvio in produzione: npm run build && npm start
 * I comandi vanno registrati una volta (e a ogni modifica): npm run comandi
 */
import { Client, Events, GatewayIntentBits, MessageFlags } from "discord.js";
import { comandiPerNome } from "./comandi/index.js";
import { configurazione } from "./configurazione.js";

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once(Events.ClientReady, (pronto) => {
  console.log(`Bot acceso come ${pronto.user.tag} su ${pronto.guilds.cache.size} server.`);
});

client.on(Events.InteractionCreate, async (interazione) => {
  if (!interazione.isChatInputCommand()) return;

  const comando = comandiPerNome.get(interazione.commandName);
  if (!comando) {
    console.warn(`Comando sconosciuto: ${interazione.commandName}`);
    return;
  }

  try {
    await comando.esegui(interazione);
  } catch (errore) {
    //Un comando che si rompe non deve spegnere il bot ne' lasciare l'utente senza risposta
    console.error(`Errore nel comando /${interazione.commandName}:`, errore);
    const avviso = {
      content: "Qualcosa non ha funzionato. Riprova tra poco.",
      flags: MessageFlags.Ephemeral as const,
    };
    if (interazione.deferred || interazione.replied) {
      await interazione.followUp(avviso).catch(() => {});
    } else {
      await interazione.reply(avviso).catch(() => {});
    }
  }
});

client.login(configurazione.token);
