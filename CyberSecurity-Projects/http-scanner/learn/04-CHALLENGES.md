# Challenges

## 1. Grade header *quality*, not just presence
Right now a header counts as "present" no matter what its value is. Add logic to flag weak configurations — e.g. `Content-Security-Policy: default-src *` (too permissive) or `Strict-Transport-Security: max-age=60` (way too short to be useful).

## 2. Add more headers
Research and add checks for `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`, and `Cross-Origin-Resource-Policy` — newer headers focused on preventing cross-origin data leaks (Spectre-style attacks).

## 3. Batch mode
Accept a file of URLs (one per line) and scan all of them, printing a summary table showing how many headers each site is missing — useful for auditing multiple sites/subdomains at once.

## 4. JSON output mode
Add a `--json` flag that prints structured findings instead of a rich table, so results can be piped into other tools or saved for tracking changes over time.

## 5. Cookie security flags
Extend the tool to also inspect `Set-Cookie` headers for the `Secure`, `HttpOnly`, and `SameSite` attributes — a very common and impactful thing to check alongside the main security headers.

## 6. Compare against a baseline
Add a mode that saves a scan's results and, on a later run, diffs against the saved baseline — showing what changed (a header added, removed, or its value changed) since the last scan of the same URL.

## 7. Redirect chain inspection
Right now `allow_redirects=True` silently follows redirects to the final page. Add an option to show the full redirect chain and check headers at *each* hop, not just the final destination — useful since intermediate redirect responses are sometimes missing headers even when the final page has them.
