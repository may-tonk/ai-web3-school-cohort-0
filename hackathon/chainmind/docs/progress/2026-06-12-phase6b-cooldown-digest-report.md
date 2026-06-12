# ChainMind Phase 6B Cooldown And Digest Report

Date: 2026-06-12

## 1. Status

Current status:

```text
Phase 6B: completed
```

Phase 6B extends the Hermes output layer with file-backed cooldown state and
multi-payload digest composition.

## 2. Completed Capabilities

Phase 6B added:

```text
file-backed cooldown state
cooldown suppression for repeated immediate and digest alerts
digest payload composition from multiple Hermes token payloads
build_hermes_digest.py script
analyze_dune_token --cooldown-state PATH --cooldown-write
```

## 3. Cooldown Policy v1

```text
immediate -> 1 hour cooldown by token and chain
digest    -> 8 hour cooldown by token and chain
store_only / filter -> no cooldown state is written
```

Cooldown state is JSON-only in Phase 6B:

```text
runtime/alerts/cooldown.json
```

The database version should preserve the same key fields:

```text
chain
token_address
delivery_level
last_sent_at
next_allowed_at
```

## 4. Digest Payload

The digest builder reads multiple Hermes token payloads and includes only:

```text
should_send=true
delivery_level=digest
```

The digest payload includes:

```text
version
channel
candidate_count
send_count
items
digest_markdown
```

## 5. Safety Boundary

Phase 6B does not:

```text
write to a database
call Telegram or Hermes APIs directly
call AI providers
change scoring rules
perform trading
```

The cooldown and digest layers preserve the evidence-only research boundary.

## 6. Main Files

```text
src/chainmind/alerts/cooldown.py
src/chainmind/alerts/digest_builder.py
scripts/analyze_dune_token.py
scripts/build_hermes_digest.py
tests/unit/test_cooldown.py
tests/unit/test_digest_builder.py
tests/unit/test_build_hermes_digest_script.py
```

## 7. Validation

Full test suite:

```text
python -m pytest
```

Result after Phase 6B:

```text
109 passed
```

## 8. Next Recommended Phase

Recommended next phase:

```text
Phase 6C: database foundation
```

Reason:

```text
Before radar scan and watchlist automation, ChainMind needs a durable storage
layer for tokens, analysis runs, snapshots, scores, alert events, cooldown
state, and future dashboard queries.
```
