"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_verify_reference_finds_doi_and_formats_metadata(fake_http) -> None:
    calls = fake_http(FakeResponse({"message": {
        "DOI": "10.1234/example.1",
        "title": ["A Research Paper"],
        "author": [{"given": "Ada", "family": "Lovelace"}],
        "published": {"date-parts": [[2024, 5, 1]]},
        "publisher": "Example Press",
        "type": "journal-article",
    }}))

    result = TOOL_FUNCTIONS["verify_reference"](reference="doi:10.1234/example.1")

    assert result["found"] is True
    assert result["match_type"] == "doi"
    assert result["items"][0]["title"] == "A Research Paper"
    assert result["items"][0]["authors"] == ["Ada Lovelace"]
    assert result["items"][0]["year"] == 2024
    assert calls[0]["url"] == "https://api.crossref.org/works/10.1234/example.1"
    assert calls[0]["timeout"] > 0


def test_verify_reference_searches_title_and_returns_candidates(fake_http) -> None:
    calls = fake_http(FakeResponse({"message": {"items": [{
        "DOI": "10.1234/example.2",
        "title": ["Reliable Tool Evaluation"],
        "author": [{"given": "Grace", "family": "Hopper"}],
    }]}}))

    result = TOOL_FUNCTIONS["verify_reference"](reference="Reliable Tool Evaluation")

    assert result["found"] is True
    assert result["match_type"] == "title_search"
    assert result["items"][0]["doi"] == "10.1234/example.2"
    assert calls[0]["params"] == {"query.bibliographic": "Reliable Tool Evaluation", "rows": 3}


def test_verify_reference_rejects_empty_or_oversized_input(fake_http) -> None:
    verify_reference = TOOL_FUNCTIONS["verify_reference"]
    calls = fake_http(FakeResponse({}))

    empty_result = verify_reference(reference="  ")
    long_result = verify_reference(reference="x" * 501)

    assert empty_result["found"] is False
    assert empty_result["items"] == []
    assert long_result["error"] == "ValueError"
    assert calls == []


def test_verify_reference_returns_not_found_for_unknown_doi(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))

    result = TOOL_FUNCTIONS["verify_reference"](reference="10.1234/missing")

    assert result["found"] is False
    assert result["match_type"] == "doi"
    assert result["items"] == []


def test_verify_reference_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = TOOL_FUNCTIONS["verify_reference"](reference="10.1234/example.1")

    assert result["tool"] == "verify_reference"
    assert result["error"] == "HTTPError"
