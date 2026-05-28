"""Unit tests for Telegram bind URL tg_* query prefill helpers."""

from chainup_agent.application.telegram_inbound import (
    _telegram_query_prefill_from_envelope,
    merge_bind_url_with_tg_prefill,
)


def test_merge_preserves_existing_query_and_adds_prefill() -> None:
    u = merge_bind_url_with_tg_prefill("https://x.example/agent?foo=1", {"tg_id": "9"})
    assert "foo=1" in u
    assert "tg_id=9" in u


def test_merge_overwrites_same_key() -> None:
    u = merge_bind_url_with_tg_prefill("https://x.example/a?tg_id=1", {"tg_id": "2"})
    assert u.count("tg_id=") == 1
    assert "tg_id=2" in u


def test_merge_skips_empty_prefill_values() -> None:
    u = merge_bind_url_with_tg_prefill("https://x.example/a", {"tg_id": "", "tg_username": "bob"})
    assert "tg_username=bob" in u
    assert "tg_id=" not in u


def test_prefill_from_user_and_private_chat_fallback() -> None:
    env = {
        "from": {"id": 7, "username": "bob", "first_name": "Bo", "language_code": "zh-hans"},
        "chat": {"id": 42, "type": "private"},
    }
    q = _telegram_query_prefill_from_envelope(env, 42)
    assert q["tg_id"] == "7"
    assert q["tg_username"] == "bob"
    assert q["tg_first_name"] == "Bo"
    assert q["tg_lang"] == "zh-hans"


def test_prefill_private_chat_id_when_no_from_id() -> None:
    env = {"chat": {"id": 55, "type": "private"}, "text": "x"}
    q = _telegram_query_prefill_from_envelope(env, 55)
    assert q["tg_id"] == "55"
    assert "tg_username" not in q
