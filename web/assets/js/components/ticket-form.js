/**
 * Comportamento condiviso dei moduli che aprono un ticket: quello
 * dell'assistenza (ticket-nuovo.html) e quello delle candidature
 * (candidatura.html). Cambiano i campi e il testo, non il funzionamento.
 *
 * Validazione in due momenti:
 *  - all'uscita da un campo (blur), solo se l'utente l'ha già toccato, così
 *    non compaiono errori su campi che non ha ancora raggiunto;
 *  - all'invio, su tutti i campi, con un riepilogo in cima al modulo e il
 *    focus portato sul primo campo sbagliato.
 *
 * Il modulo deve contenere: un <fieldset>, un riepilogo errori con
 * id="form-errors" e un avviso di invio non riuscito con id="submit-error"
 * (dentro, un elemento [data-msg]). Ogni campo sta in un .ds-field con il
 * proprio .ds-error.
 */

import { loginUrl } from '../services/session.js';
import { escapeHtml } from '../services/utils.js';
import { t } from '../services/i18n.js';

/**
 * Contatori di caratteri sotto i campi di testo lunghi.
 * Ogni contatore è un elemento [data-counter-for="nomeCampo"][data-max="N"].
 */
export function initCounters(form) {
  form.querySelectorAll('[data-counter-for]').forEach((counter) => {
    const input = form.elements[counter.dataset.counterFor];
    const max = Number(counter.dataset.max);
    const update = () => {
      const n = input.value.length;
      counter.textContent = `${n} / ${max}`;
      counter.classList.toggle('is-over', n > max);
    };
    input.addEventListener('input', update);
    update();
  });
}

/**
 * Collega validazione e invio a un modulo.
 *
 * @param {object} options
 * @param {HTMLFormElement} options.form
 * @param {Object<string, (value: string) => (string|null)>} options.rules
 *        una regola per campo: restituisce il messaggio d'errore, o null.
 * @param {Object<string, string>} options.labels nomi dei campi nel riepilogo.
 * @param {(values: Object<string, string>) => Promise<void>} options.onSubmit
 *        invia i dati (valori già ripuliti dagli spazi). Se solleva un errore,
 *        il modulo torna utilizzabile e mostra il motivo.
 * @returns {{field: Function, wrapper: Function, validateField: Function}}
 */
export function setupTicketForm({ form, rules, labels, onSubmit }) {
  const field = (name) => form.elements[name];
  const wrapper = (name) => field(name).closest('.ds-field');

  /** Mostra o toglie l'errore di un campo. Restituisce true se è valido. */
  function validateField(name) {
    const message = rules[name](field(name).value);
    const wrap = wrapper(name);
    //Il primo <span> dell'errore contiene l'icona, il secondo il testo
    const errorEl = wrap.querySelector('.ds-error > span:last-child');
    wrap.classList.toggle('is-invalid', Boolean(message));
    field(name).setAttribute('aria-invalid', String(Boolean(message)));
    if (errorEl) errorEl.textContent = message || '';
    return !message;
  }

  function showSummary(invalid) {
    const box = form.querySelector('#form-errors');
    if (!invalid.length) { box.hidden = true; box.innerHTML = ''; return; }
    box.hidden = false;
    box.innerHTML = `
      <p class="ds-form-errors__title">${t(invalid.length === 1 ? 'form.checkOne' : 'form.checkMany', { n: invalid.length })}</p>
      <ul>${invalid.map((n) => `<li><a href="#f-${n}">${labels[n]}: ${escapeHtml(rules[n](field(n).value))}</a></li>`).join('')}</ul>`;
    box.focus();
  }

  function setSubmitting(on) {
    const btn = form.querySelector('[type="submit"]');
    btn.classList.toggle('is-loading', on);
    btn.setAttribute('aria-busy', String(on));
    form.querySelector('fieldset').disabled = on;
  }

  function showSubmitError(err) {
    const box = form.querySelector('#submit-error');
    const msg = box.querySelector('[data-msg]');
    box.hidden = false;
    if (err.kind === 'auth') {
      //Il testo scritto resta nel modulo: non reindirizziamo in automatico
      msg.innerHTML = `${escapeHtml(err.message)} ` + t('form.copyThenLogin', { url: loginUrl() });
    } else {
      const reason = err.message || t('form.sendFailed');
      //Per un limite giornaliero riprovare subito non serve: niente invito a riprovare
      msg.textContent = err.kind === 'limit'
        ? reason
        : `${reason} ${t('form.dataKept')}`;
    }
    box.focus();
  }

  Object.keys(rules).forEach((name) => {
    const el = field(name);
    el.addEventListener('blur', () => {
      //Un campo lasciato vuoto senza averci scritto nulla non è ancora un errore
      if (!el.value && !wrapper(name).dataset.touched) return;
      wrapper(name).dataset.touched = 'true';
      validateField(name);
    });
    //Una volta segnalato l'errore, lo togliamo non appena il valore è corretto
    el.addEventListener('input', () => {
      if (wrapper(name).classList.contains('is-invalid')) validateField(name);
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    form.querySelector('#submit-error').hidden = true;

    const invalid = Object.keys(rules).filter((name) => {
      wrapper(name).dataset.touched = 'true';
      return !validateField(name);
    });
    showSummary(invalid);
    if (invalid.length) return;

    const values = {};
    Object.keys(rules).forEach((name) => { values[name] = field(name).value.trim(); });

    setSubmitting(true);
    try {
      await onSubmit(values);
    } catch (err) {
      setSubmitting(false);
      showSubmitError(err);
    }
  });

  return { field, wrapper, validateField };
}

/**
 * "Annulla" con conferma in pagina (niente finestre di dialogo del browser):
 * al primo clic, se nel modulo c'è del testo, compare l'avviso invece di
 * uscire; al secondo il link fa il suo lavoro.
 *
 * @param {HTMLFormElement} form
 * @param {string[]} watched campi il cui contenuto va protetto
 * @param {string} focusField campo su cui tornare scegliendo "Continua"
 * @param {() => boolean} [hasOtherInput] altro contenuto da proteggere (es. file scelti)
 */
export function setupCancelConfirm(form, watched, focusField, hasOtherInput = () => false) {
  const link = document.querySelector('[data-cancel]');
  const confirmBox = document.getElementById('cancel-confirm');
  if (!link || !confirmBox) return;

  link.addEventListener('click', (e) => {
    const dirty = watched.some((n) => form.elements[n].value.trim()) || hasOtherInput();
    if (dirty && confirmBox.hidden) {
      e.preventDefault();
      confirmBox.hidden = false;
      confirmBox.querySelector('a').focus();
    }
  });
  document.querySelector('[data-cancel-keep]').addEventListener('click', () => {
    confirmBox.hidden = true;
    form.elements[focusField].focus();
  });
}
