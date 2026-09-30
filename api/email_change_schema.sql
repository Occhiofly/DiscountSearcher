-- ============================================================================
-- Cambio dell'email con due codici (api/email_change.py).
--
-- Da eseguire UNA VOLTA nel SQL Editor di Supabase, PRIMA di pubblicare il
-- backend che la usa. È sicuro rieseguirlo.
--
-- Se il backend nuovo va online senza questa tabella, tutto il resto funziona,
-- ma dal Profilo dell'app non si riesce a cambiare l'email.
-- ============================================================================

-- Una richiesta di cambio in corso per account: il nuovo indirizzo e gli hash
-- dei due codici (uno inviato all'indirizzo attuale, uno al nuovo). La riga si
-- cancella quando il cambio è fatto, dopo 5 codici sbagliati, o dalla pulizia
-- automatica il giorno dopo.
CREATE TABLE IF NOT EXISTS email_changes (
    user_id       BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    new_email     TEXT NOT NULL,
    old_code_hash TEXT NOT NULL,
    new_code_hash TEXT NOT NULL,
    attempts      INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Niente accesso diretto dall'API REST di Supabase (il backend ignora RLS).
ALTER TABLE email_changes ENABLE ROW LEVEL SECURITY;
