/**
 * La lingua da usare rispondendo a chi ha scritto il comando.
 *
 * Discord manda la lingua del client (it, en-US, en-GB, fr...). L'API conosce
 * solo italiano e inglese, quindi tutto cio' che non e' italiano diventa inglese:
 * meglio una risposta in inglese che una in una lingua che non abbiamo tradotto.
 */
export type Lingua = "it" | "en";

export function linguaDa(localeDiscord: string | null | undefined): Lingua {
  return localeDiscord?.toLowerCase().startsWith("it") ? "it" : "en";
}

type Testi = Record<Lingua, string>;

export function testo(testi: Testi, lingua: Lingua): string {
  return testi[lingua];
}
