# Implementation Walkthrough

## `HeaderCheck` and `SECURITY_HEADERS`

Same pattern as `HashType`/`KNOWN_HASHES` from the hash-identifier project: an immutable dataclass describing one known thing, collected into a plain list that acts as the tool's "database." Adding support for a new header (e.g. `Cross-Origin-Resource-Policy`) means adding one more `HeaderCheck(...)` entry — nothing else in the code needs to change.

## `fetch_headers`

```python
def fetch_headers(url: str, timeout: float = 10.0) -> dict[str, str]:
    response = requests.get(url, timeout=timeout, allow_redirects=True)
    return dict(response.headers)
```

`requests.get(url, ...)` sends an actual HTTP GET request and waits for a response. Two arguments matter here:

- `timeout=timeout` — without this, a request to an unresponsive server could hang **forever**. Always set a timeout on real network calls.
- `allow_redirects=True` — many sites redirect `http://` to `https://`, or redirect a bare domain to `www.`. Following redirects means we end up checking the headers of the page the user would *actually* land on, not an intermediate redirect response (which often has few headers of its own).

`response.headers` is technically a special case-insensitive dictionary-like object provided by `requests` — we convert it to a plain `dict` so the rest of the code works with an ordinary, predictable type.

## `analyze`

```python
def analyze(headers: dict[str, str]) -> list[Finding]:
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
```

`{k.lower(): v for k, v in headers.items()}` is a **dict comprehension** — builds a new dictionary in one line, with every key lowercased. This handles the case-insensitivity issue described in `01-CONCEPTS.md` in one clean step, rather than lowercasing on every comparison inside the loop.

The loop then walks the reference list (`SECURITY_HEADERS`) — not the fetched headers — which is an important direction choice: we're asking "for each header *we care about*, is it present?" rather than "for each header the server *sent*, do we recognize it?" This means the output always has a predictable, consistent shape (exactly `len(SECURITY_HEADERS)` findings every time), regardless of how many other unrelated headers the server happens to send.

`lowercase_headers.get(key)` returns the actual value if present, or `None` if not — used directly as `Finding.actual_value`.

## `render`

```python
missing_count = sum(1 for f in findings if not f.present)
```

`sum(1 for f in findings if not f.present)` is a common Python idiom for counting how many items in a list match a condition — a generator expression producing a `1` for each match, summed up. Equivalent to, but more compact than, writing a manual loop with a counter variable.

The rest of `render()` follows the same table-building pattern as `hash-identifier`'s `render()` — build a `rich.Table`, add a row per item, color-code by severity.

```python
missing = [f for f in findings if not f.present]
if missing:
    console.print("\n[bold]Why these matter:[/]")
    for f in missing:
        console.print(f"  [cyan]{f.check.name}[/]: {f.check.description}")
```

A **list comprehension** builds the list of only-missing findings, then prints an extra explanation section — but only if there's at least one missing header, avoiding an empty "Why these matter:" heading when everything already passed.

## `main` — the error handling boundary

```python
try:
    headers = fetch_headers(url, timeout=args.timeout)
except requests.RequestException as exc:
    console.print(f"[bold red]Could not reach {url}[/]: {exc}")
    return 1
```

`requests.RequestException` is the parent class of every error `requests` can raise — connection errors, timeouts, too many redirects, invalid URLs, and more. Catching this one broad type (rather than several specific ones) is intentional here: at the CLI level, the user doesn't need to know the exact failure mode, just that the request didn't succeed and why, in plain language. `return 1` signals failure to the shell (by convention, non-zero exit codes mean "something went wrong").

## The tests — why mocking matters here

```python
def test_fetch_headers_returns_dict():
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html", "X-Frame-Options": "DENY"}

    with patch("http_headers_scanner.requests.get", return_value=mock_response) as mock_get:
        result = fetch_headers("https://example.com")

    mock_get.assert_called_once_with(
        "https://example.com", timeout=10.0, allow_redirects=True
    )
    assert result == {"Content-Type": "text/html", "X-Frame-Options": "DENY"}
```

`MagicMock()` creates a fake object that can stand in for anything — here, a fake HTTP response. `patch("http_headers_scanner.requests.get", ...)` temporarily replaces the real `requests.get` function with one that just returns our fake response, for the duration of the `with` block only.

This lets the test verify two separate things without ever touching the network:
1. `fetch_headers` calls `requests.get` with the correct arguments (`mock_get.assert_called_once_with(...)`)
2. `fetch_headers` correctly converts the response into a plain dict

All the other tests in the file target `analyze()` directly with hand-built dictionaries — no mocking needed there at all, since `analyze()` was deliberately designed to have zero network dependency (see `02-ARCHITECTURE.md` for why that separation matters).
