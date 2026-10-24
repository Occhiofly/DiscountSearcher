/** Forma di un comando: come si chiama per Discord e cosa fa quando lo usano. */
import type { ChatInputCommandInteraction, SlashCommandOptionsOnlyBuilder, SlashCommandBuilder } from "discord.js";

export interface Comando {
  definizione: SlashCommandBuilder | SlashCommandOptionsOnlyBuilder;
  esegui(interazione: ChatInputCommandInteraction): Promise<void>;
}
