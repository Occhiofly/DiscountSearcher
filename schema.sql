-- ============================================================================
-- Struttura del database di Discount Searcher.
--
-- Generato da `python strumenti/db.py schema` leggendo il database vero: non si
-- scrive a mano. Cambiando una tabella su Supabase, rilancia il comando e
-- committa il file, altrimenti il repository dice una cosa e il database un'altra.
--
-- Per creare il database da zero: esegui tutto questo file nel SQL Editor di
-- Supabase. È sicuro rieseguirlo, non tocca le tabelle che esistono già.
-- I dati NON stanno qui: per quelli c'è `python strumenti/db.py backup`.
--
-- Tabelle (9): users, email_changes, history, login_challenges, sessions, tickets, site_sessions, ticket_inbound_emails, ticket_messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id serial,
    username text NOT NULL,
    password_hash text NOT NULL,
    email text NOT NULL,
    email_verified boolean DEFAULT false NOT NULL,
    verification_code text,
    code_created_at timestamp with time zone,
    birth_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    reset_code text,
    reset_code_created_at timestamp with time zone,
    language text DEFAULT 'it'::text NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username),
    CHECK ((language = ANY (ARRAY['it'::text, 'en'::text])))
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users USING btree (email);
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS email_changes (
    user_id bigint NOT NULL,
    new_email text NOT NULL,
    old_code_hash text NOT NULL,
    new_code_hash text NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
ALTER TABLE email_changes ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS history (
    id serial,
    user_id integer NOT NULL,
    title text NOT NULL,
    deal_id text NOT NULL,
    viewed_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_history_user_id ON history USING btree (user_id);
ALTER TABLE history ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS login_challenges (
    id text NOT NULL,
    user_id bigint NOT NULL,
    code_hash text NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    device_info text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS login_challenges_user_idx ON login_challenges USING btree (user_id);
ALTER TABLE login_challenges ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id integer NOT NULL,
    token_hash text NOT NULL,
    device_info text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_used_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked boolean DEFAULT false NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (token_hash),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions USING btree (token_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions USING btree (user_id);
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS tickets (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    subject text NOT NULL,
    category text NOT NULL,
    extra text,
    status text DEFAULT 'open'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    CHECK (((extra IS NULL) OR (char_length(extra) <= 1000))),
    CHECK ((status = ANY (ARRAY['open'::text, 'progress'::text, 'waiting'::text, 'resolved'::text, 'closed'::text]))),
    CHECK (((char_length(subject) >= 8) AND (char_length(subject) <= 120))),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS tickets_user_updated_idx ON tickets USING btree (user_id, updated_at DESC);
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS site_sessions (
    session_id uuid NOT NULL,
    PRIMARY KEY (session_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
ALTER TABLE site_sessions ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS ticket_inbound_emails (
    message_id text NOT NULL,
    ticket_id bigint,
    outcome text NOT NULL,
    processed_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (message_id),
    CHECK ((outcome = ANY (ARRAY['reply'::text, 'status'::text, 'ignored'::text]))),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE SET NULL
);
ALTER TABLE ticket_inbound_emails ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS ticket_messages (
    id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    author_role text NOT NULL,
    author_name text NOT NULL,
    body text NOT NULL,
    email_message_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (email_message_id),
    CHECK ((author_role = ANY (ARRAY['user'::text, 'staff'::text]))),
    CHECK (((char_length(body) >= 1) AND (char_length(body) <= 20000))),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ticket_messages_ticket_idx ON ticket_messages USING btree (ticket_id, created_at);
ALTER TABLE ticket_messages ENABLE ROW LEVEL SECURITY;
