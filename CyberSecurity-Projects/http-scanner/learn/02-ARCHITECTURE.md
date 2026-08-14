# Architecture

## The pipeline

```
        ┌────────────────┐
        │   URL input     │
        └────────┬────────┘
                 │
                 ▼
        ┌────────────────┐
        │  fetch_headers   │   makes the actual HTTP request,
        │      (url)       │   returns a dict of response headers
        └────────┬────────┘
                 │
                 ▼
        ┌────────────────┐
        │    analyze       │   compares the fetched headers against
        │   (headers)      │   SECURITY_HEADERS, one Finding per check
        └────────┬────────┘
                 │
                 ▼
        ┌────────────────┐
        │     render       │   turns Findings into a colored table
        │ (url, findings)  │   + a "why this matters" explanation
        └────────────────┘
```

Three clean stages, each with a single job — this mirrors the same separation-of-concerns pattern from `hash-identifier` (`identify()` does pure logic, `render()` does pure presentation).

## Why `fetch_headers` and `analyze` are separate functions

This is a deliberate design choice for **testability**. `analyze()` takes a plain dictionary and has no network dependency at all — it can be tested instantly and deterministically with fake data, no internet connection required (see `test_analyze_all_headers_present` and friends in the test file). `fetch_headers()` is the only function that touches the network, and it's tested separately using a **mock** that fakes what `requests.get()` would return, without actually sending a request.

If these were combined into one function, every single test would need real network access — making the test suite slow, flaky (dependent on the target site being up), and impossible to run offline.

## Data model

- **`HeaderCheck`** — a static "fact card" about one security header: its name, what it protects against, its severity if missing, and a suggested fix. Immutable (`frozen=True`) for the same reason `HashType` was — these facts don't change at runtime.
- **`Finding`** — built fresh per scan: pairs one `HeaderCheck` with whether it was actually found in this particular response, and what its actual value was (if present).

## Why severity is tracked per-header

Not all missing headers are equally bad. HSTS and CSP are marked `"high"` because their absence enables direct, well-known attack classes (protocol downgrade, XSS). Permissions-Policy is marked `"low"` because its absence is more of a defense-in-depth gap than an active vulnerability by itself. Surfacing severity lets a user triage — fix the high-severity gaps first.

## Error handling boundary

Network requests can fail in many ways — DNS failure, timeout, connection refused, TLS errors. Rather than letting any of these produce a raw Python traceback (which would be confusing and look like the tool itself is broken), `main()` catches `requests.RequestException` — the common base class for all of `requests`' own errors — and prints a clean, human-readable message instead. This is the boundary where "internal implementation detail" gets translated into "something a user can actually understand and act on."
