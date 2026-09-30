/**
 * Rivelazione degli elementi allo scroll.
 *
 * Gli elementi marcati [data-reveal] partono trasparenti (vedi base.css) e
 * ricevono la classe .is-revealed quando entrano nella finestra.
 *
 * Due cautele importanti:
 * - se l'utente ha chiesto meno animazioni al sistema operativo, rendiamo
 *   tutto visibile subito senza osservare nulla;
 * - se IntersectionObserver non è disponibile, stesso comportamento: meglio
 *   nessuna animazione che contenuto invisibile per sempre.
 */

export function initReveal(root = document) {
  const items = root.querySelectorAll('[data-reveal]');
  if (!items.length) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduced || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-revealed'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-revealed');
        //Una volta mostrato, l'elemento non ci serve più: smettere di
        //osservarlo evita di ripetere l'animazione scrollando su e giù.
        observer.unobserve(entry.target);
      });
    },
    //rootMargin negativo in basso: l'elemento si rivela quando è entrato
    //davvero nella vista, non appena sfiora il bordo inferiore.
    { threshold: 0.1, rootMargin: '0px 0px -8% 0px' },
  );

  items.forEach((el, index) => {
    //Ritardo a cascata all'interno dello stesso gruppo, letto dal CSS.
    const step = Number(el.dataset.revealStep || 0);
    if (step > 0) el.style.setProperty('--reveal-delay', `${Math.min(index, 6) * step}ms`);
    observer.observe(el);
  });
}
