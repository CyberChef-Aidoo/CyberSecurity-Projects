# HTTP Headers Scanner

A CLI tool that fetches a URL and checks its response headers against six well-known security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy), reporting what's present, what's missing, and why each one matters.

NOTE: This does NOT scan for vulnerabilities in the site's code — it only
looks at what the *server* announces about itself in its headers. That
still matters a lot: missing security headers are one of the easiest,
most common misconfigurations to find, and fixing them is usually a
one-line server config change with an outsized security benefit.

Full write-up and setup instructions live in [`learn/00-OVERVIEW.md`](./learn/00-OVERVIEW.md).

Quick start:

```bash
./install.sh
python3 http_headers_scanner.py https://example.com
```

---
[⬅ Back to main repo README](../../../README.md)
