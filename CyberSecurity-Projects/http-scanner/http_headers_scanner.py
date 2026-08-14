"""
http_headers_scanner.py

A small CLI tool that fetches a URL's HTTP response headers and checks
them against a list of well-known security headers. It tells you which
protective headers are present, which are missing, and why each one
matters.

This does NOT scan for vulnerabilities in the site's code — it only
looks at what the *server* announces about itself in its headers. That
still matters a lot: missing security headers are one of the easiest,
most common misconfigurations to find, and fixing them is usually a
one-line server config change with an outsized security benefit.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Literal

import requests
from rich.console import Console
from rich.table import Table

Severity = Literal["high", "medium", "low", "info"]


@dataclass(frozen=True)
class HeaderCheck:
    """One security header we know how to check for."""

    name: str                # the actual HTTP header name, e.g. "Strict-Transport-Security"
    description: str         # what this header protects against
    severity: Severity       # how bad it is if this header is missing
    recommendation: str      # a short suggested value/fix


# Ordered roughly by how commonly they're misconfigured / how much
# impact a fix has.
SECURITY_HEADERS: list[HeaderCheck] = [
    HeaderCheck(
        name="Strict-Transport-Security",
        description="Forces browsers to only ever connect over HTTPS, even if a "
        "user types http:// or clicks an old http:// link. Without it, "
        "the very first request to a site can be intercepted before it "
        "gets upgraded to HTTPS.",
        severity="high",
        recommendation="Strict-Transport-Security: max-age=63072000; includeSubDomains; preload",
    ),
    HeaderCheck(
        name="Content-Security-Policy",
        description="Restricts which sources of scripts, styles, images, etc. the "
        "browser is allowed to load. The single strongest defense against "
        "cross-site scripting (XSS).",
        severity="high",
        recommendation="Content-Security-Policy: default-src 'self'",
    ),
    HeaderCheck(
        name="X-Frame-Options",
        description="Prevents the page from being loaded inside an <iframe> on "
        "another site — stops clickjacking attacks where a malicious "
        "site invisibly overlays your page to trick users into clicking "
        "something they didn't mean to.",
        severity="medium",
        recommendation="X-Frame-Options: DENY",
    ),
    HeaderCheck(
        name="X-Content-Type-Options",
        description="Stops the browser from trying to 'guess' a file's type "
        "(MIME sniffing). Without it, a file uploaded as an image could "
        "potentially be executed as a script in some older browsers.",
        severity="medium",
        recommendation="X-Content-Type-Options: nosniff",
    ),
    HeaderCheck(
        name="Referrer-Policy",
        description="Controls how much of the current page's URL gets sent along "
        "in the Referer header when a user clicks a link to another "
        "site. Without it, sensitive info in URLs (like session tokens "
        "in query strings) can leak to third parties.",
        severity="low",
        recommendation="Referrer-Policy: strict-origin-when-cross-origin",
    ),
    HeaderCheck(
        name="Permissions-Policy",
        description="Lets a site explicitly disable browser features it doesn't "
        "need (camera, microphone, geolocation, etc.), reducing what an "
        "attacker could abuse via injected code.",
        severity="low",
        recommendation="Permissions-Policy: geolocation=(), camera=(), microphone=()",
    ),
]


@dataclass
class Finding:
    check: HeaderCheck
    present: bool
    actual_value: str | None


def fetch_headers(url: str, timeout: float = 10.0) -> dict[str, str]:
    """Fetch a URL and return its response headers.

    Raises requests.RequestException on network failure — callers should
    handle that rather than letting a stack trace leak to the user.
    """
    response = requests.get(url, timeout=timeout, allow_redirects=True)
    return dict(response.headers)


def analyze(headers: dict[str, str]) -> list[Finding]:
    """Check a dict of response headers against SECURITY_HEADERS.

    Header name matching is case-insensitive, since HTTP header names
    are not case-sensitive per the HTTP spec, but different servers
    capitalize them differently.
    """
    lowercase_headers = {k.lower(): v for k, v in headers.items()}

    findings: list[Finding] = []
    for check in SECURITY_HEADERS:
        key = check.name.lower()
        present = key in lowercase_headers
        findings.append(
            Finding(
                check=check,
                present=present,
                actual_value=lowercase_headers.get(key),
            )
        )
    return findings


def render(url: str, findings: list[Finding]) -> None:
    console = Console()

    missing_count = sum(1 for f in findings if not f.present)
    if missing_count == 0:
        console.print(f"[bold green]All checked security headers are present[/] for {url}")
    else:
        console.print(
            f"[bold]{missing_count} of {len(findings)}[/] security headers missing for {url}"
        )

    table = Table(title=f"Header audit: {url}")
    table.add_column("Header", style="cyan", no_wrap=True)
    table.add_column("Status")
    table.add_column("Severity if missing")
    table.add_column("Value / Recommendation")

    severity_style = {"high": "bold red", "medium": "yellow", "low": "dim", "info": "dim"}

    for f in findings:
        if f.present:
            status = "[bold green]present[/]"
            value = f.actual_value or ""
        else:
            status = "[bold red]MISSING[/]"
            value = f.check.recommendation

        sev = f.check.severity
        table.add_row(
            f.check.name,
            status,
            f"[{severity_style.get(sev, '')}]{sev}[/]",
            value,
        )

    console.print(table)

    missing = [f for f in findings if not f.present]
    if missing:
        console.print("\n[bold]Why these matter:[/]")
        for f in missing:
            console.print(f"  [cyan]{f.check.name}[/]: {f.check.description}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="http-headers-scanner",
        description="Audit a URL's HTTP response headers for missing security headers.",
    )
    parser.add_argument("url", help="the URL to scan, e.g. https://example.com")
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="request timeout in seconds (default: 10)"
    )
    args = parser.parse_args(argv)

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    console = Console()
    try:
        headers = fetch_headers(url, timeout=args.timeout)
    except requests.RequestException as exc:
        console.print(f"[bold red]Could not reach {url}[/]: {exc}")
        return 1

    findings = analyze(headers)
    render(url, findings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
