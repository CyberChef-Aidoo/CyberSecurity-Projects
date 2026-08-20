#These are the necessary imports for the program to function correctly. 

#This is for parsing command-line arguments.
import argparse
#This is for regular expression
import re
#This is for system interaction
import sys
#This is for data classes default boilerplate
from dataclasses import dataclass
#This is for typing hints.
from typing import Literal
#this is for making HTTP requests.
import requests
#this is for rich text formatting or colorful output in the terminal.
from rich.console import Console
#this is for creating panels in the terminal output.
from rich.panel import Panel
#This is for creating tables in the terminal output.
from rich.table import Table

'''This indicates that the Severity type can only take one of the four specified 
string values: "high "medium", "low", or "info". This is useful for type checking and 
ensuring that only valid severity levels are used in the code.'''
Severity = Literal["high", "medium", "low", "info"]

@dataclass(frozen=True)
class HeaderCheck:
    name: str
    description: str
    severity: Severity
    recommendation: str


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