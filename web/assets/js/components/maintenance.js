/**
 * Avviso "aggiornamento in corso".
 *
 * Quando il team aggiorna il progetto accende la manutenzione dal server
 * (MAINTENANCE_MODE=1 su Render, vedi api/maintenance.py). Ogni pagina, appena
 * aperta, chiede al server se è accesa (GET /status): se sì, copre tutto con un
 * avviso e blocca l'uso del sito finché l'aggiornamento non è finito.
 *
 * L'interruttore sta sul server e non qui di proposito: accenderlo e spegnerlo
 * non richiede di ripubblicare il sito, e vale insieme per sito e app.
 *
 * Se il server non risponde (rete assente, riavvio in corso) il sito resta
 * utilizzabile: un problema di rete non è una manutenzione, e le pagine che
 * hanno bisogno del server mostrano già il loro messaggio d'errore.
 */

import * as api from '../services/api.js';
import { MAINTENANCE_EVENT } from '../services/api.js';
import { t } from '../services/i18n.js';
import { logoMark } from './icons.js';
import { escapeHtml } from '../services/utils.js';

/** Quanto aspettare il server prima di lasciar perdere, in millisecondi. */
const TIMEOUT = 5000;

function mostra(messaggio) {
  if (document.querySelector('.ds-maintenance')) return; //Già mostrato
  const velo = document.createElement('div');
  velo.className = 'ds-maintenance';
  velo.setAttribute('role', 'alertdialog');
  velo.setAttribute('aria-modal', 'true');
  velo.setAttribute('aria-labelledby', 'ds-maintenance-title');
  velo.innerHTML = `
    <div class="ds-maintenance__box">
      ${logoMark(64, 'ds-maintenance__logo')}
      <h1 class="ds-maintenance__title" id="ds-maintenance-title">${t('maintenance.title')}</h1>
      <p class="ds-maintenance__text">${escapeHtml(messaggio || t('maintenance.text'))}</p>
      <button class="ds-btn ds-btn--primary" type="button" data-maintenance-retry>${t('maintenance.retry')}</button>
    </div>`;

  //Il resto della pagina resta nel documento ma non si può più usare
  document.body.classList.add('ds-is-maintenance');
  for (const figlio of document.body.children) figlio.setAttribute('inert', '');
  document.body.append(velo);
  //Anche quello che la pagina aggiunge dopo (per esempio caricato in ritardo) resta bloccato
  new MutationObserver((cambi) => {
    for (const cambio of cambi) {
      for (const nodo of cambio.addedNodes) {
        if (nodo.nodeType === Node.ELEMENT_NODE && nodo !== velo) nodo.setAttribute('inert', '');
      }
    }
  }).observe(document.body, { childList: true });

  velo.querySelector('[data-maintenance-retry]').addEventListener('click', () => window.location.reload());
  velo.querySelector('[data-maintenance-retry]').focus();
}

//Una richiesta qualsiasi ha ricevuto "manutenzione" (pagina aperta prima che iniziasse)
window.addEventListener(MAINTENANCE_EVENT, (evento) => mostra(evento.detail));

/** Chiede al server se c'è una manutenzione in corso. Chiamata da boot() su ogni pagina. */
export async function checkMaintenance() {
  const controllo = new AbortController();
  const timer = window.setTimeout(() => controllo.abort(), TIMEOUT);
  try {
    const stato = await api.status(controllo.signal);
    if (stato?.maintenance) mostra(stato.message);
  } catch {
    //Server irraggiungibile o risposta inattesa: il sito resta com'è
  } finally {
    window.clearTimeout(timer);
  }
}
