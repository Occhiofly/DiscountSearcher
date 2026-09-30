# Discount Searcher

🇮🇹 [Versione italiana](README.md) — the full documentation is in Italian.

**Video game deals from four stores, in a single window.** A free application for Windows:
no ads, no trackers, no data selling.

➡ **[Download the latest version](https://github.com/Occhiofly/DiscountSearcher/releases/latest/download/DiscountSearcher.zip)**
· Website: **[discountsearcher.it/en](https://discountsearcher.it/en/)**
· [Help centre](https://discountsearcher.it/en/support)

![Discount Searcher](press/immagini-en/04-risultati.png)

> **The code is readable, not reusable.** This project is **not open source**: the
> proprietary licence in [LICENSE](LICENSE) applies, all rights reserved. You may read and
> study the code; copying it, redistributing it or making your own version of it is not
> allowed. The application itself stays free for everyone.

## What it does

- Shows the most recent deals from **Steam, Epic Games Store, GOG and Humble Store** on one screen.
- Filters by **store, genre, minimum discount and title**, all at the same time.
- Opens a deal in the store **with one click**.
- Keeps the games you opened in a **history tied to your account**, so you find them again
  from another computer.
- Italian and English interface, chosen the first time you start the app.

## What it does not do

Worth knowing before you download:

- It is **not a catalogue search**: it shows the deals of the last 7 days, up to 50 per store.
- It does **not track prices over time** and sends **no notifications**.
- Prices are **in US dollars**, exactly as the CheapShark API provides them.
- **Windows only.** You can still create an account and use the help centre from any computer
  at [discountsearcher.it/en/register](https://discountsearcher.it/en/register).
- The executable is **not code-signed yet**, so Windows may show an "Unknown publisher"
  warning the first time: *More info* → *Run anyway*. We are working on it.

## How to install

1. Download `DiscountSearcher.zip` from the [latest release](https://github.com/Occhiofly/DiscountSearcher/releases/latest) (23 MB).
2. Extract the folder anywhere you like.
3. Run `DiscountSearcher.exe`. Python is not required.

Updating from an older version: replace the folder. Your account and history stay, because
they live on the server.

## How it is built

| Part | Technology |
|---|---|
| Desktop interface | CustomTkinter (Tkinter), dark theme |
| Deal data | Public [CheapShark](https://www.cheapshark.com/) API |
| Game genres | Public Steam API |
| Backend | FastAPI (Python), hosted separately from the app |
| Database | PostgreSQL on [Supabase](https://supabase.com/) |
| Password storage | PBKDF2-HMAC-SHA256, random per-user salt, 260,000 iterations |
| Sessions | Server-side session tokens verified on every request, revocable at any time |
| Website sign-in | Password plus a 6-digit code sent by email |
| Email | Sent by the server over SMTP; the desktop app never sends email |
| Packaging | Standalone Windows executable built with Nuitka |

The project is split in two halves that can run on different machines: the desktop app
(`main.py`, `backend.py`, `api_client.py`) and the server (`api/`). The website lives in
`web/` and is plain HTML, CSS and JavaScript, with no framework.

## Repository layout

| Folder | What is in it |
|---|---|
| `api/` | The FastAPI server: accounts, sessions, history, support tickets, staff area |
| `web/` | The website, Italian in the root and English in `web/en/` |
| `press/` | Screenshots and material for posts, in both languages |
| root | The desktop application and the build script |

The application zip is **not** in the repository: it is published with each
[release](https://github.com/Occhiofly/DiscountSearcher/releases).

## Credits

Deal data from the public [CheapShark](https://www.cheapshark.com/) API, game genres from
Steam's public API. Discount Searcher is an independent project: it is not affiliated with,
sponsored by or approved by Valve / Steam, Epic Games, GOG, Humble Bundle or CheapShark. All
store names and trademarks belong to their respective owners.
