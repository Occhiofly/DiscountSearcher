/**
 * Pagina "Crea un account": registrati.html e en/register.html
 *
 * Stessi endpoint dell'app desktop (api/main.py): POST /register crea l'account non
 * ancora verificato e manda il codice, POST /verify-email lo attiva, POST /resend-code
 * ne manda un altro. Le regole sono quelle del server: indirizzo @gmail.com, password
 * di almeno 8 caratteri, nome utente non già preso.
 *
 * Esiste perché l'app è solo per Windows: chi usa un Mac (per esempio chi fa assistenza
 * dal Centro assistenza) deve poter creare l'account lo stesso.
 */

import { boot } from '../app.js';
import * as api from '../services/api.js';
import { ApiError, NetworkError } from '../services/api.js';
import { getSession } from '../services/session.js';
import { icon } from '../components/icons.js';
import { escapeHtml } from '../services/utils.js';
import { t, url } from '../services/i18n.js';

const view = document.querySelector('[data-register-view]');

const RESEND_SECONDS = 60; //come il limite del server fra due invii

/** Traduce la risposta del server in un messaggio per chi sta leggendo. */
function errorMessage(err) {
  if (err instanceof NetworkError) return t('register.slowServer');
  if (err instanceof ApiError) {
    //409 = username o email già in uso, 422 = dati rifiutati (il server spiega quale),
    //429 = troppe email verso quell'indirizzo: in tutti e tre il testo del server è chiaro
    if ([400, 409, 422, 429].includes(err.status) && typeof err.detail === 'string') return err.message;
    if (err.status === 409) return t('register.taken');
  }
  return t('register.serverError');
}

function initForm() {
  const form = document.getElementById('register-form');
  const btn = form.querySelector('[type="submit"]');
  const errorBox = document.getElementById('register-error');
  const slowHint = document.getElementById('register-slow');
  const password = form.elements.password;

  const fail = (text) => {
    errorBox.hidden = false;
    errorBox.querySelector('[data-msg]').textContent = text;
  };

  const toggle = form.querySelector('[data-toggle-password]');
  toggle.addEventListener('click', () => {
    const show = password.type === 'password';
    password.type = show ? 'text' : 'password';
    toggle.textContent = show ? t('login.hidePassword') : t('login.showPassword');
    toggle.setAttribute('aria-pressed', String(show));
    password.focus();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.hidden = true;

    const username = form.elements.username.value.trim();
    const email = form.elements.email.value.trim();
    const birth = form.elements.birth_date.value;
    if (!username || !email || !password.value || !birth) {
      fail(t('register.missingFields'));
      return;
    }
    //Gli stessi due controlli del server, fatti qui per rispondere subito
    if (!/^[A-Za-z0-9._%+-]+@gmail\.com$/i.test(email)) { fail(t('register.gmailOnly')); return; }
    if (password.value.length < 8) { fail(t('register.shortPassword')); return; }

    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    const slowTimer = window.setTimeout(() => { slowHint.hidden = false; }, 5000);
    try {
      const esito = await api.register({ username, password: password.value, email, birth_date: birth });
      renderCodeStep(username, email, esito?.email_sent !== false);
      return;
    } catch (err) {
      //La password NON si svuota: l'errore riguarda quasi sempre un altro campo
      //(username già preso, email non valida), e riscriverla ogni volta è solo una seccatura.
      fail(errorMessage(err));
    } finally {
      window.clearTimeout(slowTimer);
      slowHint.hidden = true;
      btn.classList.remove('is-loading');
      btn.removeAttribute('aria-busy');
    }
  });

  form.elements.username.focus();
}

/**
 * Secondo passaggio: il codice di 6 cifre arrivato via email. Finché non viene
 * inserito l'account esiste ma non permette di accedere (il server risponde
 * "email non verificata").
 */
function renderCodeStep(username, email, inviata = true) {
  view.innerHTML = `
    <header class="ds-stack ds-stack--3" style="text-align:center;align-items:center">
      <span class="ds-icon-box ds-icon-box--lg">${icon('mail')}</span>
      <h1 style="font-size:var(--ds-fs-h2)">${t('register.codeTitle')}</h1>
      <p class="ds-muted">${t('register.codeText', { email: escapeHtml(email) })}</p>
    </header>
    <form class="ds-panel ds-form" id="code-form" novalidate>
      <div class="ds-notice ds-notice--warn" id="code-notsent" role="alert" ${inviata ? 'hidden' : ''}>
        <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
        <p>${t('register.codeNotSent')}</p>
      </div>
      <div class="ds-field">
        <label class="ds-label" for="f-code">${t('register.codeLabel')}</label>
        <input class="ds-input ds-mono" id="f-code" name="code" type="text" inputmode="numeric"
               autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required
               style="font-size:1.5rem;letter-spacing:.5em;text-align:center">
      </div>
      <div class="ds-notice ds-notice--warn" id="code-error" role="alert" hidden>
        <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
        <p data-msg></p>
      </div>
      <p class="ds-hint" id="code-info" role="status"></p>
      <button class="ds-btn ds-btn--primary ds-btn--block" type="submit"><span>${t('register.codeSubmit')}</span></button>
      <div class="ds-row" style="justify-content:flex-end">
        <button class="ds-btn ds-btn--secondary" type="button" data-resend></button>
      </div>
      <p class="ds-hint">${t('register.codeSpam')}</p>
      <p class="ds-hint">${t('register.codeWrongEmail', { url: url('support') })}</p>
    </form>`;

  const form = view.querySelector('#code-form');
  const input = form.elements.code;
  const btn = form.querySelector('[type="submit"]');
  const resend = form.querySelector('[data-resend]');
  const errorBox = view.querySelector('#code-error');
  const info = view.querySelector('#code-info');
  const fail = (text) => {
    errorBox.hidden = false;
    errorBox.querySelector('[data-msg]').textContent = text;
  };

  let timer = null;
  const countdown = (seconds) => {
    window.clearInterval(timer);
    let left = seconds;
    const tick = () => {
      resend.disabled = left > 0;
      resend.textContent = left > 0 ? t('register.codeResendIn', { seconds: left }) : t('register.codeResend');
      left -= 1;
      if (left < -1) window.clearInterval(timer);
    };
    tick();
    timer = window.setInterval(tick, 1000);
  };
  countdown(RESEND_SECONDS);

  input.addEventListener('input', () => {
    input.value = input.value.replace(/\D/g, '').slice(0, 6);
    errorBox.hidden = true;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.hidden = true;
    if (!/^\d{6}$/.test(input.value)) { fail(t('register.codeInvalid')); input.focus(); return; }
    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    try {
      await api.verifyEmail({ username, code: input.value });
      window.clearInterval(timer);
      renderDone(username);
      return;
    } catch (err) {
      fail(errorMessage(err));
      input.select();
    } finally {
      btn.classList.remove('is-loading');
      btn.removeAttribute('aria-busy');
    }
  });

  resend.addEventListener('click', async () => {
    errorBox.hidden = true;
    info.textContent = '';
    resend.disabled = true;
    try {
      const result = await api.resendCode({ username });
      //email_sent=false: il codice è stato rigenerato ma l'email non è partita
      view.querySelector('#code-notsent').hidden = result.email_sent;
      info.textContent = result.email_sent ? t('register.codeResent') : '';
      countdown(RESEND_SECONDS);
      input.value = '';
      input.focus();
    } catch (err) {
      //Solo un 429 ("troppi invii") giustifica l'attesa intera: se è caduta la rete
      //non è partito niente, e far aspettare un minuto sarebbe solo una seccatura.
      const troppi = err instanceof ApiError && err.status === 429;
      fail(errorMessage(err));
      countdown(troppi ? RESEND_SECONDS : 0);
    }
  });

  input.focus();
}

/** Account attivo: da qui si va all'accesso, dove arriva il codice di sicurezza del sito. */
function renderDone(username) {
  view.innerHTML = `
    <div class="ds-panel ds-stack ds-stack--5" style="text-align:center;align-items:center">
      <span class="ds-icon-box ds-icon-box--lg">${icon('check')}</span>
      <div class="ds-stack ds-stack--2">
        <h1 style="font-size:var(--ds-fs-h3)">${t('register.doneTitle')}</h1>
        <p class="ds-card__text">${t('register.doneText', { username: escapeHtml(username) })}</p>
      </div>
      <div class="ds-row" style="justify-content:center">
        <a class="ds-btn ds-btn--primary" href="${url('login')}">${t('register.goToLogin')}</a>
        <a class="ds-btn ds-btn--ghost" href="${url('home', '#download')}">${t('register.downloadApp')}</a>
      </div>
    </div>`;
}

//Chi è già collegato non ha bisogno di registrarsi: glielo diciamo invece di
//lasciargli compilare un modulo inutile.
const session = getSession();
if (session) {
  view.innerHTML = `
    <div class="ds-panel ds-stack ds-stack--5" style="text-align:center;align-items:center">
      <span class="ds-icon-box ds-icon-box--lg">${icon('user')}</span>
      <div class="ds-stack ds-stack--2">
        <h1 style="font-size:var(--ds-fs-h3)">${t('login.alreadyTitle')}</h1>
        <p class="ds-card__text">${t('login.alreadyText', { username: escapeHtml(session.username) })}</p>
      </div>
      <a class="ds-btn ds-btn--primary" href="${url('ticketList')}">${t('register.myTickets')}</a>
    </div>`;
} else {
  initForm();
}
boot();
