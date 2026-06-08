# ChainMind Phase 5B Token Profile Boundary Plan

Date: 2026-06-08

## 1. Scope

Phase 5B adds a lightweight token-profile boundary layer.

The goal is to distinguish interpretation contexts before reports, AI
explanations, or Hermes push logic consume ChainMind scores.

## 2. Profile Values

Initial profiles:

```text
meme_candidate
mainstream_control
infrastructure
```

## 3. Design Boundary

This phase does not change core scoring math.

It only adds context:

```text
snapshot.token_profile
TokenSnapshot.token_profile
TokenSnapshot.profile_type
report Interpretation Context section
```

## 4. Inference Priority

Profile inference order:

```text
1. explicit token_profile
2. sample_meta.sample_type
3. known BNB control / infrastructure addresses
4. market or token symbol heuristics
5. default meme_candidate
```

## 5. Acceptance Criteria

Phase 5B is complete when:

```text
token_profile is present on Dune-backed snapshots
token_profile is present on quick-screen snapshots
reports display interpretation context
mainstream / infrastructure profiles include a non-meme boundary warning
python -m pytest passes
```
