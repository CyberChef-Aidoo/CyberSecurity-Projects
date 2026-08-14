"""Tests for http_headers_scanner.py

These tests use unittest.mock to avoid making real network requests —
tests should be fast, deterministic, and runnable offline.
"""

from unittest.mock import patch, MagicMock

from http_headers_scanner import analyze, fetch_headers, SECURITY_HEADERS


def test_analyze_all_headers_present():
    headers = {check.name: "some-value" for check in SECURITY_HEADERS}
    findings = analyze(headers)
    assert all(f.present for f in findings)
    assert len(findings) == len(SECURITY_HEADERS)


def test_analyze_all_headers_missing():
    findings = analyze({})
    assert all(not f.present for f in findings)
    assert all(f.actual_value is None for f in findings)


def test_analyze_is_case_insensitive():
    headers = {"strict-transport-security": "max-age=63072000"}
    findings = analyze(headers)
    hsts = next(f for f in findings if f.check.name == "Strict-Transport-Security")
    assert hsts.present is True
    assert hsts.actual_value == "max-age=63072000"


def test_analyze_mixed_present_and_missing():
    headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
    }
    findings = analyze(headers)
    present_names = {f.check.name for f in findings if f.present}
    missing_names = {f.check.name for f in findings if not f.present}

    assert present_names == {"X-Frame-Options", "X-Content-Type-Options"}
    assert "Content-Security-Policy" in missing_names
    assert "Strict-Transport-Security" in missing_names


def test_fetch_headers_returns_dict():
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html", "X-Frame-Options": "DENY"}

    with patch("http_headers_scanner.requests.get", return_value=mock_response) as mock_get:
        result = fetch_headers("https://example.com")

    mock_get.assert_called_once_with(
        "https://example.com", timeout=10.0, allow_redirects=True
    )
    assert result == {"Content-Type": "text/html", "X-Frame-Options": "DENY"}


def test_every_security_header_has_a_recommendation():
    # Every check should have a non-empty recommendation string —
    # this is what gets shown to the user when a header is missing,
    # so an empty one would be a real (if quiet) bug.
    for check in SECURITY_HEADERS:
        assert check.recommendation.strip() != ""
        assert check.name in check.recommendation
