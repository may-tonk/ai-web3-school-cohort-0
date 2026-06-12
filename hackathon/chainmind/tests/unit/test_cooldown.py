from datetime import UTC, datetime, timedelta

from chainmind.alerts.cooldown import (
    apply_cooldown,
    empty_cooldown_state,
    load_cooldown_state,
    save_cooldown_state,
)


def _payload(delivery_level="immediate", should_send=True):
    return {
        "should_send": should_send,
        "delivery_level": delivery_level,
        "summary": {
            "chain": "bnb",
            "token_address": "0xToken",
        },
        "analysis": {
            "chain": "bnb",
            "token_address": "0xToken",
        },
    }


def test_apply_cooldown_records_first_send_and_suppresses_repeat():
    now = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    state = empty_cooldown_state()

    first_payload, state = apply_cooldown(_payload(), state, now=now)

    assert first_payload["should_send"] is True
    assert first_payload["delivery_level"] == "immediate"
    assert first_payload["cooldown"]["suppressed"] is False
    assert "bnb:0xtoken:immediate" in state["items"]

    repeated_payload, repeated_state = apply_cooldown(
        _payload(),
        state,
        now=now + timedelta(minutes=30),
    )

    assert repeated_payload["should_send"] is False
    assert repeated_payload["delivery_level"] == "suppressed"
    assert repeated_payload["cooldown"]["suppressed"] is True
    assert repeated_payload["cooldown"]["original_delivery_level"] == "immediate"
    assert repeated_state == state


def test_apply_cooldown_allows_send_after_window_expires():
    now = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    _, state = apply_cooldown(_payload(), empty_cooldown_state(), now=now)

    allowed_payload, _ = apply_cooldown(
        _payload(),
        state,
        now=now + timedelta(hours=1, seconds=1),
    )

    assert allowed_payload["should_send"] is True
    assert allowed_payload["cooldown"]["suppressed"] is False


def test_apply_cooldown_uses_digest_window_and_ignores_unsendable_payloads():
    now = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    _, state = apply_cooldown(_payload("digest"), empty_cooldown_state(), now=now)

    suppressed_payload, _ = apply_cooldown(
        _payload("digest"),
        state,
        now=now + timedelta(hours=2),
    )

    assert suppressed_payload["should_send"] is False
    assert suppressed_payload["cooldown"]["original_delivery_level"] == "digest"

    store_payload, store_state = apply_cooldown(
        _payload("store_only", should_send=False),
        state,
        now=now,
    )

    assert store_payload["cooldown"]["suppressed"] is False
    assert store_state == state


def test_load_and_save_cooldown_state_roundtrip(tmp_path):
    state_path = tmp_path / "cooldown.json"
    state = empty_cooldown_state()
    _, state = apply_cooldown(
        _payload(),
        state,
        now=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    save_cooldown_state(state_path, state)

    assert load_cooldown_state(state_path) == state


def test_apply_cooldown_can_skip_state_update():
    payload, state = apply_cooldown(
        _payload(),
        empty_cooldown_state(),
        now=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        update_state=False,
    )

    assert payload["cooldown"]["suppressed"] is False
    assert state["items"] == {}
