/**
 * Selettore degli allegati dei ticket (assistenza e candidature).
 *
 * Il vero <input type="file"> è trasparente e copre tutta l'area tratteggiata:
 * cliccarla, attivarla da tastiera o trascinarci sopra dei file usa sempre il
 * comportamento nativo del browser, senza reimplementarlo. I file scelti
 * finiscono in un elenco nostro, così si possono aggiungere in più volte e
 * togliere uno per uno.
 *
 * I limiti sono gli stessi del server (api/attachments.py), che comunque
 * ricontrolla tutto, compreso il contenuto vero dei file: questi controlli
 * servono solo a dirlo subito, prima di un invio che fallirebbe.
 */

import { icon } from './icons.js';
import { escapeHtml } from '../services/utils.js';
import { t } from '../services/i18n.js';

export const ATTACHMENT_LIMITS = {
  maxFiles: 3,
  maxFileBytes: 4 * 1024 * 1024,
  maxTotalBytes: 10 * 1024 * 1024,
};

/** Tipi accettati: tipo MIME -> estensioni. Gli stessi di api/attachments.py. */
const TYPES = {
  'application/pdf': ['pdf'],
  'image/png': ['png'],
  'image/jpeg': ['jpg', 'jpeg'],
  'image/gif': ['gif'],
  'image/webp': ['webp'],
};

/** Stesso formato del server: "310 KB", "2,1 MB". */
export function formatSize(n) {
  if (n < 1024) return t('files.bytes', { n });
  if (n < 1024 * 1024) return `${Math.round(n / 1024)} KB`;
  //I decimali si scrivono con la virgola in italiano e con il punto in inglese
  return `${(n / (1024 * 1024)).toFixed(1).replace('.', t('files.decimalSep'))} MB`;
}

/**
 * Tipo del file, o null se non è fra quelli accettati. Si guarda prima il tipo
 * dichiarato dal browser e poi l'estensione (alcuni sistemi non dichiarano nulla).
 */
function typeOf(file) {
  if (TYPES[file.type]) return file.type;
  const ext = file.name.split('.').pop().toLowerCase();
  return Object.keys(TYPES).find((t) => TYPES[t].includes(ext)) || null;
}

/** Motivo per cui un singolo file non va bene, o null. */
function fileProblem(file) {
  if (!typeOf(file)) return t('files.notAllowed');
  if (file.size === 0) return t('files.empty');
  if (file.size > ATTACHMENT_LIMITS.maxFileBytes) return t('files.tooBig', { limit: formatSize(ATTACHMENT_LIMITS.maxFileBytes) });
  return null;
}

/** Contenuto del file in base64, come lo vuole il server. */
function readBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    //readAsDataURL dà "data:<tipo>;base64,<dati>": serve solo la parte dopo la virgola
    reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

/**
 * Collega il selettore a un campo del modulo.
 *
 * @param {HTMLElement} wrap il .ds-field che contiene [data-dropzone] e [data-file-list]
 * @param {() => void} onChange chiamata dopo ogni aggiunta o rimozione
 */
export function createFilePicker(wrap, onChange = () => {}) {
  const input = wrap.querySelector('input[type="file"]');
  const zone = wrap.querySelector('[data-dropzone]');
  const list = wrap.querySelector('[data-file-list]');
  const count = wrap.querySelector('[data-file-count]');
  let files = [];

  function render() {
    count.textContent = `${files.length} / ${ATTACHMENT_LIMITS.maxFiles}`;
    count.classList.toggle('is-over', files.length > ATTACHMENT_LIMITS.maxFiles);
    list.hidden = !files.length;
    list.innerHTML = files.map((file, i) => {
      const problem = fileProblem(file);
      return `
        <li class="ds-file${problem ? ' is-invalid' : ''}">
          <span class="ds-file__icon">${icon(typeOf(file)?.startsWith('image/') ? 'image' : 'file', { size: 16 })}</span>
          <span class="ds-file__main">
            <span class="ds-file__name">${escapeHtml(file.name)}</span>
            <span class="ds-file__meta">${formatSize(file.size)}${problem ? ` · ${escapeHtml(problem)}` : ''}</span>
          </span>
          <button class="ds-btn ds-btn--ghost ds-btn--sm" type="button" data-remove="${i}"
                  aria-label="${t('files.removeAria', { name: escapeHtml(file.name) })}">${t('files.remove')}</button>
        </li>`;
    }).join('');
  }

  input.addEventListener('change', () => {
    //Lo stesso file scelto due volte non va aggiunto due volte. Nome e dimensione
    //bastano: la data di modifica cambia fra browser e fra trascinamento e scelta.
    const key = (f) => `${f.name}|${f.size}`;
    const known = new Set(files.map(key));
    [...input.files].forEach((f) => {
      if (!known.has(key(f))) { files.push(f); known.add(key(f)); }
    });
    //Svuotato: così si può scegliere di nuovo anche un file appena tolto
    input.value = '';
    render();
    onChange();
  });

  list.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-remove]');
    if (!btn) return;
    const i = Number(btn.dataset.remove);
    files.splice(i, 1);
    render();
    onChange();
    //Il pulsante premuto non esiste più: il focus va al successivo o all'area di scelta
    (list.querySelectorAll('[data-remove]')[Math.min(i, files.length - 1)] || input).focus();
  });

  //Solo l'aspetto durante il trascinamento: il rilascio lo gestisce l'input nativo
  ['dragenter', 'dragover'].forEach((type) => zone.addEventListener(type, () => zone.classList.add('is-dragover')));
  ['dragleave', 'drop'].forEach((type) => zone.addEventListener(type, () => zone.classList.remove('is-dragover')));

  render();

  return {
    get files() { return files; },

    /** Messaggio d'errore per il riepilogo del modulo, o null se va tutto bene. */
    validate() {
      if (files.length > ATTACHMENT_LIMITS.maxFiles) {
        return t('files.tooMany', {
          limit: ATTACHMENT_LIMITS.maxFiles,
          extra: files.length - ATTACHMENT_LIMITS.maxFiles,
        });
      }
      const bad = files.find(fileProblem);
      if (bad) return t('files.problem', { name: bad.name, problem: fileProblem(bad) });
      const total = files.reduce((sum, f) => sum + f.size, 0);
      if (total > ATTACHMENT_LIMITS.maxTotalBytes) {
        return t('files.totalTooBig', { limit: formatSize(ATTACHMENT_LIMITS.maxTotalBytes) });
      }
      return null;
    },

    /** Gli allegati nel formato della richiesta al server. */
    async toPayload() {
      return Promise.all(files.map(async (file) => ({
        name: file.name,
        content_type: typeOf(file),
        data: await readBase64(file),
      })));
    },
  };
}
