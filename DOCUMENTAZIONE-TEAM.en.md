# Discount Searcher — team procedures

🇮🇹 [Versione italiana](DOCUMENTAZIONE-TEAM.md)

How the project is run day to day: support tickets, the staff area, publishing a new version
and maintenance mode. These are the procedures for the people working on it; if you want to
understand how the project is built, that is in the **[README](README.en.md)**.

## Support tickets

The help centre on the website lets users (signed in with the same account as the app) open
tickets. The team receives every ticket by email and **replies to that email directly**: the
server reads the project's Gmail mailbox over IMAP, recognises replies by the `[DS-<number>]`
code in the subject, adds them to the ticket and notifies the user.

The team can reply in two ways, and both at once:

- **From the project's own account** (the same as `GMAIL_ADDRESS`, listed in `SUPPORT_STAFF`):
  open that mailbox and reply to the notification. The server reads those replies from the
  **Sent** folder, which only someone with access to the account can write to, and skips its
  own notifications (marked with the `X-DS-Notification` header).
- **From other addresses** listed in `SUPPORT_STAFF`: those replies land in the server's
  Inbox and are accepted only if they pass the DMARC/DKIM checks recorded by Gmail, so nobody
  can impersonate the team by forging the sender.

**Job applications** from the website's "Work with us" page use the same system: they are
tickets with category `candidatura` and subject `Candidatura — <role>`, so the team receives
and answers them exactly like a support ticket. The only difference is the confirmation email
to the applicant, which calls it an application and not a support request. Tickets and
applications can carry up to 3 attachments (PDFs or images, 10 MB in total), for example a
screenshot of the error: the server checks them (`api/attachments.py`) and attaches them to
the email for the team **without storing them**, neither on the server nor in the database;
only the file names stay in the ticket. Files the team attaches to its own replies, on the
other hand, do not reach the user: instructions for a test have to be written in the reply
itself, or linked.

Staff addresses are never shown to users: the ticket only shows the name given in
`SUPPORT_STAFF`. Writing `#inlavorazione`, `#risolto` or `#chiuso` as the first line of a
reply changes the ticket's status.

**Staff area on the website** (`staff.html`, server side `api/staff.py`): instead of using
email, the team can see every ticket and application together with who opened it, reply and
change the status from the website; the user gets the same email notice either way.
Membership is decided by the `STAFF_ACCOUNTS` variable on Render, with the **account number**
and the name to show in replies, for example `STAFF_ACCOUNTS=12:Marco, 15:Vittorio`. The
number comes from Supabase's SQL Editor with `SELECT id, username FROM users WHERE username =
'...';`. It is the number and not the email address because the email can be changed from the
profile without verifying it again: anyone could set it to the team's. For everybody else the
`/staff` addresses answer 404. The notification emails to the team also carry a link to the
ticket in the staff area, and staff members find a "Staff area" button on the "My tickets"
page.

## New-version notice

The app **does not update itself**, but it does know when a new version is out. At every
start it calls `GET /status` (the same call as maintenance mode) and the server answers,
along with its status, with the latest published version and its release notes in the
language of the request (`api/release.py`, content in `api/release.json`). If the app's own
version (`version.py`) is older, a panel appears with the list of what changed, the download
button, "Later" and "Don't remind me for this version" (the choice is saved in
`settings.json`).

No email and no personal data: the notice is seen by whoever opens the app, which is exactly
who needs to update. Emailing every user would be a different matter: the privacy policy
states that no newsletters are sent, and the project's Gmail account has a daily cap that is
needed for verification and sign-in codes.

**To publish a new version**: raise `APP_VERSION` in `version.py` (it is used by the
executable and the User-Agent too), write the version and the notes in `api/release.json`,
rebuild, then publish the server and the website with the new zip. Anyone on a version older
than 1.0.8 does not see the notice: the feature did not exist yet.

## Database backups

Supabase's free plan keeps **no copies at all**: no daily backups, no point-in-time recovery.
If the project were deleted, or a query emptied a table, accounts, histories and tickets would
be gone. The only copy is the one we make.

**How**, from the project folder, with `api/.env` up to date:

```bash
python strumenti/db.py backup
```

It writes `backup/discountsearcher-<date>-<time>.zip`, holding `schema.sql` (the structure),
one CSV per table and a `LEGGIMI.txt` file with the row counts and the restore steps. It needs
only Python — no `pg_dump` to install.

**How often**: once a week, and **always before** running SQL that changes or deletes data.
Keep the zip off the working computer (external drive or private cloud). It holds real
people's data: it does not belong in the repository — `backup/` is git-ignored — and must not
be shared in the team chat.

**To restore into an empty database**: run `schema.sql` in Supabase's SQL Editor, then load the
CSVs in the order `LEGGIMI.txt` lists them (`users` first: the other tables reference it).

**Whenever a table changes** on Supabase, run `python strumenti/db.py schema` again and commit
`schema.sql`, or the repository describes a different database from the real one.

## Updates: maintenance mode

While the team updates the project, the website and the app can be stopped together with an
"Update in progress" notice, from **a single switch** on the server.

**Turning it on**: on Render, in the service's environment variables, add `MAINTENANCE_MODE`
with the value `1` and save. Render restarts the server (about a minute).
**Turning it off**: remove the variable, or set it to `0`.

With maintenance on:

- **the website** covers every page with the notice and cannot be used; if a page was already
  open, the notice appears on the first request to the server;
- **the app** shows the notice full-window at start-up; if it was already open, it shows it
  on the first request (history search, profile, sign-in). "Try again" asks for the status
  and, once maintenance is over, carries on from where it was;
- **app versions installed before this feature** do not know about the notice, but the server
  answers "update in progress" to all of their requests anyway;
- `/health` keeps answering, because Render uses it to tell whether the server is alive.

The switch is on the server on purpose: turning it on and off needs neither republishing the
website nor rebuilding the app. If the server does not answer at all (no network, restart in
progress), the website and the app do **not** show the notice: a network problem is not
maintenance.

Recommended order for an update:

1. turn on `MAINTENANCE_MODE=1` on Render and wait for the restart;
2. publish the changes (server, website, app);
3. check that everything works;
4. turn maintenance off.

The code lives in `api/maintenance.py` (server), `web/assets/js/components/maintenance.js`
(website) and in the `_check_service_at_startup` / `_show_maintenance` methods of `main.py`
(app).
