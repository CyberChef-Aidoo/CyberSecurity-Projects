# Concepts

## What is an HTTP response header, really?

When your browser requests a web page, the server sends back two things: the actual content (HTML, images, etc.) and a set of **headers** — short key-value lines of metadata about the response, sent before the content itself. Headers cover all sorts of things (content type, caching rules, cookies) — this tool focuses specifically on the subset that exist purely for **security enforcement**.

## The six headers this tool checks

### Strict-Transport-Security (HSTS)
**The problem it solves:** the very first time you visit a site, if you type `example.com` (no `https://`) or click an old plain-`http://` link, your browser's *first* request goes out over unencrypted HTTP — even if the site immediately redirects to HTTPS. That brief unencrypted moment can be intercepted by an attacker on the same network (a classic move on public WiFi).

**What HSTS does:** tells the browser "remember: always use HTTPS for this site from now on, for the next N seconds" — so on your *second* visit onward, your browser refuses to even attempt plain HTTP.

### Content-Security-Policy (CSP)
**The problem it solves:** cross-site scripting (XSS) — where an attacker manages to inject malicious JavaScript into a page (through a comment field, a URL parameter, etc.), and that script then runs with full access to the page, able to steal cookies or session tokens.

**What CSP does:** tells the browser exactly which sources scripts, styles, images, and other resources are allowed to load from. Even if an attacker injects a `<script src="evil.com/steal.js">` tag, a well-configured CSP will make the browser simply refuse to load or run it.

### X-Frame-Options
**The problem it solves:** clickjacking — an attacker embeds your site inside an invisible `<iframe>` on their own malicious page, positions it precisely, and tricks a user into clicking what looks like an innocent button but is actually a hidden button on *your* site (like "confirm transfer" or "delete account").

**What it does:** tells the browser "never allow this page to be loaded inside a frame on another site," making that whole attack impossible.

### X-Content-Type-Options
**The problem it solves:** MIME sniffing. Older browsers would sometimes try to guess a file's real type by peeking at its content rather than trusting the server's declared `Content-Type`. This could occasionally be abused to get a browser to execute a file as a script when it was supposed to be treated as an inert image.

**What it does:** the single value `nosniff` tells the browser "trust the declared Content-Type exactly, don't try to guess."

### Referrer-Policy
**The problem it solves:** when a user clicks a link from your page to another site, the browser normally sends a `Referer` header showing the full URL of the page they came from — including any sensitive info baked into your URL (session tokens, search queries, internal page paths).

**What it does:** controls how much of that URL gets shared. A common safe setting sends only the origin (`https://yoursite.com`) to other sites, while sending the full path only to pages on your own site.

### Permissions-Policy
**The problem it solves:** browsers expose powerful APIs (camera, microphone, geolocation) to any script running on the page — including a malicious one that got injected some other way. Without restriction, an attacker's script could try to access these.

**What it does:** lets a site explicitly disable features it doesn't need, shrinking what an attacker could abuse even if they get code execution some other way.

## Why "present" isn't automatically "safe"

This tool checks whether a header **exists** — it doesn't deeply validate whether the *value* is actually secure. A site could technically have `Content-Security-Policy: default-src *`, which is present but essentially useless (it allows loading from anywhere). Real auditing tools go further and grade the *quality* of each header's value, not just its presence — see `04-CHALLENGES.md` for an extension idea along these lines.

## Why header name matching has to be case-insensitive

The HTTP specification treats header field names as case-insensitive — a server might send `content-security-policy`, `Content-Security-Policy`, or even `CONTENT-SECURITY-POLICY`, and all three are the same header. Different web servers and frameworks capitalize differently by convention, so any tool checking for a specific header by name has to normalize case before comparing, or it will report false negatives.
