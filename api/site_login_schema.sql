-- ============================================================================
-- Accesso al sito con codice via email (api/site_login.py).
--
-- Da eseguire UNA VOLTA nel SQL Editor di Supabase, PRIMA di pubblicare il
-- backend che le usa. È sicuro rieseguirlo: IF NOT EXISTS non tocca tabelle
-- già create.
--
-- Se il backend nuovo va online senza queste tabelle, l'app continua a
-- funzionare (non le usa), ma dal sito non si riesce ad accedere e i ticket
-- danno errore.
-- ============================================================================

-- Richieste di accesso in corso: password già giusta, si aspetta il codice.
-- Il codice non è salvato in chiaro, solo il suo hash. Una riga per account al
-- massimo (il server cancella la precedente), e si cancella appena usata.
CREATE TABLE IF NOT EXISTS login_challenges (
    id          TEXT PRIMARY KEY,           -- valore casuale lungo, lo tiene la pagina
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash   TEXT NOT NULL,
    attempts    INTEGER NOT NULL DEFAULT 0, -- codici sbagliati: al quinto si ricomincia
    device_info TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS login_challenges_user_idx ON login_challenges (user_id);

-- Sessioni aperte dal sito DOPO il codice. Ticket e area staff accettano solo
-- queste: un token ottenuto con la sola password (come fa l'app) non basta.
-- Quando la sessione viene cancellata, la riga se ne va con lei.
CREATE TABLE IF NOT EXISTS site_sessions (
    session_id UUID PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE
);

-- Come per le altre tabelle: niente accesso diretto dall'API REST di Supabase.
-- Il backend si collega con l'utente del database, che ignora RLS.
ALTER TABLE login_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_sessions ENABLE ROW LEVEL SECURITY;
