# HTTP Headers Scanner — Overview

## What this is

A CLI tool that fetches a URL and inspects its HTTP response headers — specifically, whether six well-known **security headers** are present. These headers are instructions a web server sends to the browser, telling it to enforce extra protections (force HTTPS, block certain script sources, prevent the page from being framed by another site, and so on).

The tool doesn't scan for bugs in a site's code — it only checks what the server *announces about itself*. That's still valuable: missing security headers are one of the most common, easiest-to-spot misconfigurations, and adding them is usually a small server config change with a real security payoff.

## Why this matters

A huge portion of real-world web attacks — cross-site scripting (XSS), clickjacking, protocol downgrade attacks — have a **cheap, well-known mitigation**: a single response header. Yet a large fraction of live websites are still missing some or all of them, often just because nobody thought to check. Security auditors and bug bounty hunters run tools exactly like this one as a first, fast pass before digging into anything more involved.

## What you'll learn

**Security concepts:**
- What each of six major security headers actually protects against
- Why "the server told the browser to do X" is a legitimate, useful line of defense, distinct from "the code has no bugs"
- Why header names are case-insensitive over HTTP, and why real-world tools have to account for that

**Python concepts:**
- Making an actual outbound HTTP request with the `requests` library
- Handling network failures gracefully instead of letting the program crash
- Writing tests that **mock** network calls, so a test suite runs fast and doesn't depend on the internet being reachable
- The same `dataclass` / `Literal` / type-hint patterns from the hash-identifier project, reused in a new context

**Tools:**
- [`requests`](https://requests.readthedocs.io) — the standard Python library for making HTTP requests
- `unittest.mock` — Python's built-in tool for faking a function's behavior during tests

## Before you start

Same prerequisites as `hash-identifier`: Python 3.10+, basic terminal use. No prior networking knowledge required — the concepts are explained as they come up.

## Quick start

```bash
./install.sh
```

Then try it:

```bash
python3 http_headers_scanner.py https://example.com
```

You can leave off `https://` — the tool adds it automatically if you just type a bare domain:

```bash
python3 http_headers_scanner.py example.com
```

## Project layout

```
http-headers-scanner/
├── http_headers_scanner.py        the whole tool
├── test_http_headers_scanner.py   its test suite (uses mocked network calls)
├── install.sh
├── justfile
├── pyproject.toml
├── README.md
├── learn/
│   ├── 00-OVERVIEW.md              you are here
│   ├── 01-CONCEPTS.md              what each header does, why it matters
│   ├── 02-ARCHITECTURE.md          the fetch → analyze → render pipeline
│   ├── 03-IMPLEMENTATION.md        the code, explained section by section
│   └── 04-CHALLENGES.md            extension ideas
└── assets/
```

## Where to go next

1. [01-CONCEPTS.md](./01-CONCEPTS.md) — what each security header actually does
2. [02-ARCHITECTURE.md](./02-ARCHITECTURE.md) — how the tool is structured
3. [03-IMPLEMENTATION.md](./03-IMPLEMENTATION.md) — the code, walked through
4. [04-CHALLENGES.md](./04-CHALLENGES.md) — extend it yourself

## Troubleshooting

**`ModuleNotFoundError: No module named 'requests'`** — run `pip install requests rich pytest` (or re-run `./install.sh`).

**`Could not reach <url>`** — check your internet connection, or the URL might be down/blocking automated requests. Try a well-known site like `https://example.com` first to confirm the tool itself works.

**Externally-managed-environment error on `pip install`** — same fix as `hash-identifier`: use a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`) before installing.
