/** Tutti i comandi del bot. Per aggiungerne uno: crealo qui accanto e mettilo in lista. */
import { download } from "./download.js";
import type { Comando } from "./tipi.js";

export const comandi: Comando[] = [download];

export const comandiPerNome = new Map<string, Comando>(
  comandi.map((c) => [c.definizione.name, c])
);
