"""
Strumenti per il database (Supabase/PostgreSQL). Due comandi:

    python strumenti/db.py schema     scrive schema.sql leggendo la struttura vera
    python strumenti/db.py backup     salva struttura e dati in un unico file .zip

Servono a due cose diverse:

- `schema` tiene la **struttura** nel repository. Senza, il progetto non si può
  rifare da zero e nessuno sa com'è fatto il database se non aprendo Supabase.
  Va rilanciato ogni volta che si cambia una tabella, e il file va committato.
- `backup` porta via i **dati** (account, cronologie, ticket). Il piano gratuito
  di Supabase non conserva nessuna copia: se il progetto viene cancellato o
  rovinato, l'unica copia è quella che abbiamo fatto noi.

Il collegamento si legge da api/.env (DATABASE_URL), oppure dalla variabile
d'ambiente DATABASE_URL se c'è. La password non viene mai stampata né salvata
dentro i file prodotti.

Lo stesso lavoro lo farebbe `pg_dump`, che però va installato; qui basta Python
e asyncpg, che il progetto usa già.
"""
import asyncio
import csv
import io
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import asyncpg

RADICE = Path(__file__).resolve().parent.parent
CARTELLA_BACKUP = RADICE / "backup"        #esclusa da git: contiene dati di persone vere
FILE_SCHEMA = RADICE / "schema.sql"


def leggi_dsn():
    """DATABASE_URL dall'ambiente o da api/.env. Errore chiaro se manca o è vecchia."""
    dsn = os.environ.get("DATABASE_URL")
    if dsn:
        return dsn.strip()
    env = RADICE / "api" / ".env"
    if not env.exists():
        sys.exit("Manca api/.env (o la variabile DATABASE_URL): non so a quale database collegarmi.")
    for riga in io.open(env, encoding="utf-8"):
        if riga.strip().startswith("DATABASE_URL="):
            return riga.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("In api/.env non c'è DATABASE_URL.")


async def collega():
    try:
        return await asyncpg.connect(leggi_dsn(), timeout=30)
    except asyncpg.InvalidPasswordError:
        sys.exit("Password rifiutata: api/.env ha una password diversa da quella di Supabase.\n"
                 "Se contiene @ / ? # o $, vanno codificati (per esempio @ diventa %40).")
    except Exception as errore:
        sys.exit(f"Collegamento non riuscito: {errore}")


#--- struttura --------------------------------------------------------------------------

async def elenco_tabelle(conn):
    """Le tabelle di `public`, ordinate in modo che le referenziate vengano prima."""
    nomi = [r["relname"] for r in await conn.fetch("""
        SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'public' AND c.relkind = 'r' ORDER BY c.relname""")]
    dipendenze = {n: set() for n in nomi}
    for r in await conn.fetch("""
        SELECT conrelid::regclass::text AS figlia, confrelid::regclass::text AS madre
          FROM pg_constraint WHERE contype = 'f' AND connamespace = 'public'::regnamespace"""):
        figlia, madre = r["figlia"].replace("public.", ""), r["madre"].replace("public.", "")
        if figlia in dipendenze and madre != figlia:
            dipendenze[figlia].add(madre)
    ordinate, rimaste = [], list(nomi)
    while rimaste:
        libere = [n for n in rimaste if not (dipendenze[n] - set(ordinate))]
        if not libere:                      #dipendenze circolari: si prosegue com'è
            libere = rimaste[:]
        for n in libere:
            ordinate.append(n)
            rimaste.remove(n)
    return ordinate


async def ddl_tabella(conn, tabella):
    """Il CREATE TABLE di una tabella, ricostruito dal catalogo di PostgreSQL."""
    colonne = await conn.fetch("""
        SELECT a.attname AS nome, format_type(a.atttypid, a.atttypmod) AS tipo,
               a.attnotnull AS obbligatoria, a.attidentity AS identita,
               pg_get_expr(d.adbin, d.adrelid) AS predefinito
          FROM pg_attribute a
          LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
         WHERE a.attrelid = $1::regclass AND a.attnum > 0 AND NOT a.attisdropped
         ORDER BY a.attnum""", f"public.{tabella}")
    #Le colonne che contano da sé (id) nel database vero hanno DEFAULT
    #nextval('<tabella>_id_seq'), ma quella sequenza questo file non la crea: scritta
    #così, su un database vuoto il CREATE TABLE fallirebbe. Si riscrive come
    #serial/bigserial, che crea la sequenza insieme alla tabella.
    contatore = {"integer": "serial", "bigint": "bigserial", "smallint": "smallserial"}
    pezzi = []
    for c in colonne:
        tipo, predefinito = c["tipo"], c["predefinito"]
        if predefinito and predefinito.startswith("nextval(") and tipo in contatore:
            tipo, predefinito = contatore[tipo], None
        riga = f'    {c["nome"]} {tipo}'
        if c["identita"] in ("a", "d"):
            sempre = "ALWAYS" if c["identita"] == "a" else "BY DEFAULT"
            riga += f" GENERATED {sempre} AS IDENTITY"
        elif predefinito:
            riga += f' DEFAULT {predefinito}'
        if c["obbligatoria"] and not tipo.endswith("serial"):
            riga += " NOT NULL"    #serial comprende già NOT NULL
        pezzi.append(riga)
    for v in await conn.fetch("""
        SELECT pg_get_constraintdef(oid) AS definizione, contype
          FROM pg_constraint WHERE conrelid = $1::regclass AND contype IN ('p','u','c','f')
         ORDER BY CASE contype WHEN 'p' THEN 1 WHEN 'u' THEN 2 WHEN 'c' THEN 3 ELSE 4 END,
                  conname""", f"public.{tabella}"):
        pezzi.append(f'    {v["definizione"]}')
    testo = f"CREATE TABLE IF NOT EXISTS {tabella} (\n" + ",\n".join(pezzi) + "\n);\n"

    for i in await conn.fetch("""
        SELECT indexdef FROM pg_indexes
         WHERE schemaname = 'public' AND tablename = $1
           AND indexname NOT IN (SELECT conname FROM pg_constraint WHERE conrelid = $2::regclass)
         ORDER BY indexname""", tabella, f"public.{tabella}"):
        #senza il prefisso "public.": così il file si può provare in uno schema a parte
        definizione = i["indexdef"].replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", 1) \
                                   .replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ", 1)
        testo += definizione.replace(" ON public.", " ON ") + ";\n"
    if await conn.fetchval("SELECT relrowsecurity FROM pg_class WHERE oid = $1::regclass", f"public.{tabella}"):
        testo += f"ALTER TABLE {tabella} ENABLE ROW LEVEL SECURITY;\n"
    return testo


async def scrivi_schema(conn, percorso=FILE_SCHEMA):
    tabelle = await elenco_tabelle(conn)
    testata = f"""-- ============================================================================
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
-- Tabelle ({len(tabelle)}): {", ".join(tabelle)}
-- ============================================================================

"""
    corpo = "\n".join([await ddl_tabella(conn, t) for t in tabelle])
    io.open(percorso, "w", encoding="utf-8", newline="\n").write(testata + corpo)
    return tabelle


#--- dati -------------------------------------------------------------------------------

async def scrivi_backup(conn):
    CARTELLA_BACKUP.mkdir(exist_ok=True)
    momento = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    destinazione = CARTELLA_BACKUP / f"discountsearcher-{momento}.zip"
    tabelle = await elenco_tabelle(conn)
    riepilogo = [f"Copia del database di Discount Searcher",
                 f"Momento (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
                 f"PostgreSQL:    {await conn.fetchval('SHOW server_version')}",
                 f"Spazio:        {await conn.fetchval('SELECT pg_size_pretty(pg_database_size(current_database()))')}",
                 "", "Tabella                      Righe", "-" * 40]

    with zipfile.ZipFile(destinazione, "w", zipfile.ZIP_DEFLATED) as zip_:
        schema_temporaneo = CARTELLA_BACKUP / "_schema_temporaneo.sql"
        await scrivi_schema(conn, schema_temporaneo)
        zip_.write(schema_temporaneo, "schema.sql")
        schema_temporaneo.unlink()
        for t in tabelle:
            buffer = io.BytesIO()
            await conn.copy_from_table(t, output=buffer, format="csv", header=True)
            dati = buffer.getvalue()
            zip_.writestr(f"dati/{t}.csv", dati)
            righe = max(0, dati.count(b"\n") - 1)
            riepilogo.append(f"{t:<28}{righe:>7}")
            print(f"   {t:<28}{righe:>7} righe")
        riepilogo += ["", "Per rimettere tutto in un database vuoto:",
                      "1. esegui schema.sql nel SQL Editor di Supabase;",
                      "2. carica ogni CSV nella sua tabella, nell'ordine in cui sono elencati qui",
                      "   sopra (le tabelle che ne referenziano altre vengono dopo).",
                      "",
                      "Questi file contengono dati di persone vere: non vanno messi nel repository",
                      "né condivisi. La cartella backup/ è esclusa da git apposta."]
        zip_.writestr("LEGGIMI.txt", "\n".join(riepilogo) + "\n")
    return destinazione


#--- avvio ------------------------------------------------------------------------------

async def principale(comando):
    conn = await collega()
    try:
        if comando == "schema":
            tabelle = await scrivi_schema(conn)
            print(f"schema.sql aggiornato: {len(tabelle)} tabelle ({', '.join(tabelle)}).")
            print("Ricordati di committarlo.")
        else:
            print("Copia in corso...")
            destinazione = await scrivi_backup(conn)
            mb = destinazione.stat().st_size / 1_048_576
            print(f"\nFatto: {destinazione}  ({mb:.1f} MB)")
            print("Tienila fuori dal computer di lavoro (disco esterno o cloud privato).")
    finally:
        await conn.close()


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    if comando not in ("schema", "backup"):
        sys.exit(__doc__)
    asyncio.run(principale(comando))
