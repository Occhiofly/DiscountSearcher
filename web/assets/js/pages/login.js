/**
 * Pagina di accesso: accedi.html?next=<pagina>
 *
 * Accesso in due passaggi (api/site_login.py): username e password, poi il codice
 * di 6 cifre che il server manda via email. Per la password valgono le stesse
 * regole dell'app: messaggio generico per credenziali errate, blocco temporaneo
 * dopo troppi tentativi, account da verificare prima di poter accedere.
 * Registrazione e recupero password restano nell'app.
 */

import { boot, hydrateIcons } from '../app.js';
import * as api from '../services/api.js';
import { ApiError, NetworkError } from '../services/api.js';
import { getSession, logout, safeNext, saveSession } from '../services/session.js';
import { icon } from '../components/icons.js';
import { escapeHtml, queryParam } from '../services/utils.js';
import { t } from '../services/i18n.js';

const next = safeNext(queryParam('next'));
const view = document.querySelector('[data-login-view]');
//Il modulo com'è nell'HTML, per tornarci dal passaggio del codice
const FORM_VIEW = view.innerHTML;

function showForm() {
  view.innerHTML = FORM_VIEW;
  hydrateIcons(view);
  initForm();
}

function renderAlreadyLoggedIn(session) {
  view.innerHTML = `
    <div class="ds-panel ds-stack ds-stack--5" style="text-align:center;align-items:center">
      <span class="ds-icon-box ds-icon-box--lg">${icon('user')}</span>
      <div class="ds-stack ds-stack--2">
        <h1 style="font-size:var(--ds-fs-h3)">${t('login.alreadyTitle')}</h1>
        <p class="ds-card__text">${t('login.alreadyText', { username: escapeHtml(session.username) })}</p>
      </div>
      <div class="ds-row" style="justify-content:center">
        <a class="ds-btn ds-btn--primary" href="${next}">${t('login.continue')}</a>
        <button class="ds-btn ds-btn--ghost" type="button" data-switch>${t('login.switchAccount')}</button>
      </div>
    </div>`;
  view.querySelector('[data-switch]').addEventListener('click', async () => {
    await logout();
    window.location.reload();
  });
}

/** Traduce la risposta del server in un messaggio per l'utente. */
function errorMessage(err) {
  if (err instanceof NetworkError) {
    return t('login.slowServer');
  }
  if (err instanceof ApiError) {
    if (err.status === 401) return t('login.wrongCredentials');
    if (err.status === 403 && err.detail?.error === 'email_not_verified') {
      return t('login.notVerified');
    }
    if (err.status === 429) return err.message; //Contiene già i minuti di attesa
    if (err.status === 422) return t('login.missingFields');
  }
  return t('login.serverError');
}

function initForm() {
  const form = document.getElementById('login-form');
  const username = form.elements.username;
  const password = form.elements.password;
  const btn = form.querySelector('[type="submit"]');
  const errorBox = document.getElementById('login-error');
  const slowHint = document.getElementById('login-slow');

  //Mostra/nascondi password: utile soprattutto da telefono
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

    if (!username.value.trim() || !password.value) {
      errorBox.hidden = false;
      errorBox.querySelector('[data-msg]').textContent = t('login.missingFields');
      (username.value.trim() ? password : username).focus();
      return;
    }

    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    //Se il server non era in uso da tempo può impiegare parecchi secondi a
    //rispondere (avvio a freddo): lo diciamo, invece di lasciare un'attesa muta.
    const slowTimer = window.setTimeout(() => { slowHint.hidden = false; }, 5000);

    try {
      //Primo passaggio: con la password giusta non si entra ancora, arriva un codice via email
      const challenge = await api.siteLogin({
        username: username.value.trim(),
        password: password.value,
        device_info: t('login.device'),
      });
      renderCodeStep(challenge);
    } catch (err) {
      errorBox.hidden = false;
      errorBox.querySelector('[data-msg]').textContent = errorMessage(err);
      password.value = '';
      password.focus();
    } finally {
      window.clearTimeout(slowTimer);
      slowHint.hidden = true;
      btn.classList.remove('is-loading');
      btn.removeAttribute('aria-busy');
    }
  });

  username.focus();
}

/**
 * Secondo passaggio: il codice di 6 cifre arrivato via email. Solo con il codice
 * giusto il server apre la sessione del sito (api/site_login.py): ticket e area
 * staff non accettano un accesso fatto con la sola password.
 */
const RESEND_SECONDS = 60; //come il limite del server fra due invii

function renderCodeStep(challenge) {
  view.innerHTML = `
    <header class="ds-stack ds-stack--3" style="text-align:center;align-items:center">
      <span class="ds-icon-box ds-icon-box--lg">${icon('mail')}</span>
      <h1 style="font-size:var(--ds-fs-h2)">${t('login.codeTitle')}</h1>
      <p class="ds-muted">${t('login.codeText', { email: escapeHtml(challenge.email_hint), minutes: challenge.minutes })}</p>
    </header>
    <form class="ds-panel ds-form" id="code-form" novalidate>
      <div class="ds-notice ds-notice--warn" id="code-notsent" role="alert" ${challenge.email_sent ? 'hidden' : ''}>
        <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
        <p>${t('login.codeNotSent')}</p>
      </div>
      <div class="ds-field">
        <label class="ds-label" for="f-code">${t('login.codeLabel')}</label>
        <input class="ds-input ds-mono" id="f-code" name="code" type="text" inputmode="numeric"
               autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required
               style="font-size:1.5rem;letter-spacing:.5em;text-align:center">
      </div>
      <div class="ds-notice ds-notice--warn" id="code-error" role="alert" hidden>
        <span class="ds-notice__icon">${icon('alert', { size: 17 })}</span>
        <p data-msg></p>
      </div>
      <p class="ds-hint" id="code-info" role="status"></p>
      <button class="ds-btn ds-btn--primary ds-btn--block" type="submit"><span>${t('login.codeSubmit')}</span></button>
      <div class="ds-row" style="justify-content:space-between">
        <button class="ds-btn ds-btn--ghost" type="button" data-back>${t('login.codeBack')}</button>
        <button class="ds-btn ds-btn--secondary" type="button" data-resend></button>
      </div>
      <p class="ds-hint">${t('login.codeSpam')}</p>
    </form>`;

  const form = view.querySelector('#code-form');
  const input = form.elements.code;
  const btn = form.querySelector('[type="submit"]');
  const resend = form.querySelector('[data-resend]');
  const errorBox = view.querySelector('#code-error');
  const info = view.querySelector('#code-info');
  const showError = (text) => {
    errorBox.hidden = false;
    errorBox.querySelector('[data-msg]').textContent = text;
  };

  //Pulsante "Invia un nuovo codice" con il conto alla rovescia
  let timer = null;
  const countdown = (seconds) => {
    window.clearInterval(timer);
    let left = seconds;
    const tick = () => {
      resend.disabled = left > 0;
      resend.textContent = left > 0 ? t('login.codeResendIn', { seconds: left }) : t('login.codeResend');
      left -= 1;
      if (left < -1) window.clearInterval(timer);
    };
    tick();
    timer = window.setInterval(tick, 1000);
  };
  countdown(challenge.email_sent ? RESEND_SECONDS : 0);

  //Un codice scaduto o bruciato: si torna alla password
  const restart = (message) => {
    window.clearInterval(timer);
    showForm();
    const box = document.getElementById('login-error');
    box.hidden = false;
    box.querySelector('[data-msg]').textContent = message;
  };

  //Solo cifre; incollando un codice con spazi li togliamo
  input.addEventListener('input', () => {
    input.value = input.value.replace(/\D/g, '').slice(0, 6);
    errorBox.hidden = true;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.hidden = true;
    if (!/^\d{6}$/.test(input.value)) { showError(t('login.codeInvalid')); input.focus(); return; }
    btn.classList.add('is-loading');
    btn.setAttribute('aria-busy', 'true');
    try {
      const result = await api.siteLoginVerify({ challenge: challenge.challenge, code: input.value });
      window.clearInterval(timer);
      saveSession({ token: result.access_token, username: result.username });
      window.location.href = next;
      return;
    } catch (err) {
      if (err instanceof ApiError && err.status === 410) { restart(err.detail?.message || t('login.serverError')); return; }
      if (err instanceof ApiError && err.status === 400) showError(err.message);
      else showError(errorMessage(err));
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
      const result = await api.siteLoginResend({ challenge: challenge.challenge });
      view.querySelector('#code-notsent').hidden = result.email_sent;
      if (result.email_sent) info.textContent = t('login.codeResent');
      countdown(result.email_sent ? RESEND_SECONDS : 0);
      input.value = '';
      input.focus();
    } catch (err) {
      if (err instanceof ApiError && err.status === 410) { restart(err.detail?.message || t('login.serverError')); return; }
      //429: troppi invii, il messaggio del server dice quanti minuti aspettare
      const tooMany = err instanceof ApiError && err.status === 429;
      showError(tooMany ? err.message : errorMessage(err));
      countdown(tooMany ? RESEND_SECONDS : 0);
    }
  });

  form.querySelector('[data-back]').addEventListener('click', () => {
    window.clearInterval(timer);
    showForm();
  });

  input.focus();
}

const session = getSession();
if (session) renderAlreadyLoggedIn(session); else initForm();
boot();
