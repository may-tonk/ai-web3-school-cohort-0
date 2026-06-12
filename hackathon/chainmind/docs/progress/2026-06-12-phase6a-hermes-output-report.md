# ChainMind Phase 6A Hermes Output Report

Date: 2026-06-12

## 1. Status

Current status:

```text
Phase 6A: completed
```

Phase 6A adds a Hermes-friendly output package without connecting databases,
Telegram APIs, AI providers, or trading systems.

## 2. Completed Capabilities

Phase 6A added:

```text
Alert delivery policy
Telegram-oriented short Markdown builder
Hermes JSON payload builder
analyze_dune_token --hermes-output PATH
```

## 3. Hermes Payload Fields

The payload includes:

```text
version
channel
should_send
delivery_level
delivery_reason
grade
action
summary
telegram_markdown
report_markdown
ai_prompt
snapshot
analysis
```

## 4. Delivery Policy v1

```text
A / manual_review -> should_send=true, delivery_level=immediate
B / watchlist     -> should_send=true, delivery_level=digest
C / store_only    -> should_send=false, delivery_level=store_only
D / filter        -> should_send=false, delivery_level=filter
```

## 5. Safety Boundary

Phase 6A does not:

```text
write to a database
call Telegram or Hermes APIs directly
call AI providers
change scoring rules
create cooldown state
perform trading
```

The Hermes message remains an evidence-only research alert and preserves the
no-execution-instructions boundary.

## 6. Main Files

```text
src/chainmind/alerts/alert_policy.py
src/chainmind/alerts/digest_builder.py
src/chainmind/alerts/channels/hermes.py
scripts/analyze_dune_token.py
tests/unit/test_alert_policy.py
tests/unit/test_hermes_payload.py
tests/unit/test_analyze_dune_token_script.py
```

## 7. Validation

Full test suite:

```text
python -m pytest
```

Result after Phase 6A:

```text
98 passed
```

## 8. Next Recommended Phase

Recommended next phase:

```text
Phase 6B: cooldown and digest composition
```

Reason:

```text
Hermes can now consume a stable single-token payload. The next useful layer is
to prevent repeated alerts and compose multiple B-grade/watchlist candidates
into digest-friendly output.
```
