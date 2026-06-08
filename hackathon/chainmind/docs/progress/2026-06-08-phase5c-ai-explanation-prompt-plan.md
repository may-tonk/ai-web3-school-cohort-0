# ChainMind Phase 5C AI Explanation Prompt Plan

Date: 2026-06-08

## 1. Scope

Phase 5C adds an AI-ready prompt packet for explaining ChainMind reports.

The goal is to prepare structured evidence for an AI explanation layer without
calling a model provider inside the core analysis workflow.

## 2. Design Boundary

This phase generates prompts only.

It does not:

```text
call OpenAI or another model provider
invent token facts
replace scoring
produce execution instructions
push to Hermes
```

## 3. Deliverables

Code:

```text
src/chainmind/reports/report_prompt.py
```

Config:

```text
config/prompts.yaml
```

CLI:

```text
scripts/analyze_dune_token.py --ai-prompt-output PATH
```

Tests:

```text
tests/unit/test_report_prompt.py
```

## 4. Acceptance Criteria

Phase 5C is complete when:

```text
generate_ai_explanation_prompt() returns a versioned prompt package
the package contains system_prompt, user_prompt, structured_context, and report_markdown
the system prompt forbids invented facts and execution instructions
analyze_dune_token can write the prompt JSON
python -m pytest passes
```
