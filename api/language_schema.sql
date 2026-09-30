-- ============================================================================
-- Lingua dell'utente, per le email.
--
-- Le risposte immediate del server usano la lingua della richiesta
-- (Accept-Language), ma un'email parte anche molto dopo — per esempio quando
-- lo staff risponde a un ticket — quindi la lingua va ricordata nell'account.
--
-- Da eseguire UNA VOLTA nel SQL Editor di Supabase, PRIMA di pubblicare il
-- backend che la usa: il server legge questa colonna a ogni accesso, e senza
-- risponderebbe con un errore. È sicuro rieseguirlo.
--
-- Gli account già esistenti restano in italiano finché non accedono da un'app
-- o da un sito in inglese: a quel punto la lingua si aggiorna da sola.
-- ============================================================================

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT 'it'
    CHECK (language IN ('it', 'en'));
