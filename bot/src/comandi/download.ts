/**
 * /download - manda il link per scaricare l'app, con l'ultima versione pubblicata.
 *
 * La versione non e' scritta qui dentro: la chiede all'API, che la legge da
 * api/release.json. Cosi' quando pubblichi una versione nuova il bot lo sa da solo
 * e nessuno deve ricordarsi di aggiornarlo.
 *
 * Se l'API non risponde il comando manda comunque il link al sito: un bot che dice
 * "errore" quando qualcuno vuole scaricare l'app e' peggio di nessun bot.
 */
import { EmbedBuilder, SlashCommandBuilder } from "discord.js";
import { statoServizio } from "../api.js";
import { configurazione } from "../configurazione.js";
import { linguaDa, testo } from "../lingua.js";
import type { Comando } from "./tipi.js";

export const download: Comando = {
  definizione: new SlashCommandBuilder()
    .setName("download")
    .setDescription("Il link per scaricare Discount Searcher")
    .setDescriptionLocalizations({
      it: "Il link per scaricare Discount Searcher",
      "en-US": "The link to download Discount Searcher",
      "en-GB": "The link to download Discount Searcher",
    }),

  async esegui(interazione) {
    const lingua = linguaDa(interazione.locale);
    //L'API puo' metterci qualche secondo: Discord vuole una risposta entro tre
    await interazione.deferReply();

    const stato = await statoServizio(lingua);
    const app = stato?.app ?? null;
    const indirizzo =
      app?.url ?? (lingua === "it" ? `${configurazione.sito}/#download` : `${configurazione.sito}/en/#download`);

    const embed = new EmbedBuilder()
      .setColor(configurazione.colore)
      .setTitle(
        testo({ it: "Scarica Discount Searcher", en: "Download Discount Searcher" }, lingua)
      )
      .setDescription(
        testo(
          {
            it: `Gratis, per Windows.\n\n**[Vai al download](${indirizzo})**`,
            en: `Free, for Windows.\n\n**[Go to the download](${indirizzo})**`,
          },
          lingua
        )
      );

    if (app) {
      embed.addFields({
        name: testo({ it: "Ultima versione", en: "Latest version" }, lingua),
        value: `\`${app.version}\``,
        inline: true,
      });
      const novita = app.notes.slice(0, 4);
      if (novita.length > 0) {
        embed.addFields({
          name: testo({ it: "Cosa cambia", en: "What's new" }, lingua),
          value: novita.map((n) => `• ${n}`).join("\n").slice(0, 1024),
        });
      }
    }

    if (stato?.maintenance) {
      embed.addFields({
        name: testo({ it: "Avviso", en: "Notice" }, lingua),
        value:
          stato.message ??
          testo(
            {
              it: "Il servizio e' in manutenzione: l'app si scarica, ma l'accesso potrebbe non funzionare.",
              en: "The service is under maintenance: the app downloads, but signing in may not work.",
            },
            lingua
          ),
      });
    }

    embed.setFooter({
      text: testo(
        { it: "discountsearcher.it", en: "discountsearcher.it" },
        lingua
      ),
    });

    await interazione.editReply({ embeds: [embed] });
  },
};
