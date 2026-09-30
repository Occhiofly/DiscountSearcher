-- ============================================================================
-- Ticket di assistenza — tabelle per il Centro assistenza del sito.
--
-- Da eseguire UNA VOLTA nel SQL Editor di Supabase, PRIMA di pubblicare il
-- backend che usa i ticket. È sicuro rieseguirlo: IF NOT EXISTS non tocca
-- tabelle già create.
-- ============================================================================

CREATE TABLE IF NOT EXISTS tickets (
    -- Numero progressivo. Sul sito e nelle email compare come "DS-1001":
    -- si parte da 1001 perché un "DS-1" sembrerebbe un ticket di prova.
    id          BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1001) PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject     TEXT NOT NULL CHECK (char_length(subject) BETWEEN 8 AND 120),
    category    TEXT NOT NULL,
    extra       TEXT CHECK (extra IS NULL OR char_length(extra) <= 1000),
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'progress', 'waiting', 'resolved', 'closed')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- "I miei ticket": tutti i ticket di un utente, dal più recentemente aggiornato
CREATE INDEX IF NOT EXISTS tickets_user_updated_idx ON tickets (user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS ticket_messages (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id        BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_role      TEXT NOT NULL CHECK (author_role IN ('user', 'staff')),
    author_name      TEXT NOT NULL,
    body             TEXT NOT NULL CHECK (char_length(body) BETWEEN 1 AND 20000),
    -- Message-ID dell'email da cui arriva una risposta dello staff. UNIQUE: se la
    -- stessa email venisse letta due volte, la seconda non crea un doppione.
    email_message_id TEXT UNIQUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ticket_messages_ticket_idx ON ticket_messages (ticket_id, created_at);

-- Registro delle email lette dalla casella del server (risposte dello staff).
-- Ogni email viene elaborata UNA sola volta, qualunque sia l'esito: così non
-- dipendiamo dal flag "letto" di Gmail, che cambia anche solo aprendo la
-- casella dal browser.
CREATE TABLE IF NOT EXISTS ticket_inbound_emails (
    message_id   TEXT PRIMARY KEY,
    ticket_id    BIGINT REFERENCES tickets(id) ON DELETE SET NULL,
    -- reply = risposta aggiunta · status = solo cambio di stato · ignored = scartata
    -- (mittente non dello staff, verifica fallita, ticket inesistente)
    outcome      TEXT NOT NULL CHECK (outcome IN ('reply', 'status', 'ignored')),
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row Level Security: Supabase espone automaticamente le tabelle dello schema
-- "public" anche tramite la sua API REST. Attivando RLS senza definire nessuna
-- policy, quell'accesso diretto viene negato a tutti. Il backend non ne è
-- influenzato: si collega con l'utente del database (DATABASE_URL), che
-- ignora RLS.
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_inbound_emails ENABLE ROW LEVEL SECURITY;
