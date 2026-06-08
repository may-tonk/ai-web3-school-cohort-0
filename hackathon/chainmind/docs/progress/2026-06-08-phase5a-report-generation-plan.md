# ChainMind Phase 5A Report Generation Plan

Date: 2026-06-08

## 1. Scope

Phase 5A implements deterministic Markdown report generation.

The goal is to turn existing structured analysis output into a readable report:

```text
snapshot + AnalysisResult -> Markdown report
```

This phase does not add AI generation, Hermes push, automated scanning, database
storage, or trading execution.

## 2. Design Boundary

The report layer must not call data sources directly.

Allowed input:

```text
snapshot
analysis
evidence fields
```

Disallowed in this phase:

```text
Dune calls
DexScreener calls
GoPlus calls
Honeypot calls
GMGN calls
Nansen calls
BNB RPC calls
AI-generated facts
execution instructions
```

## 3. Deliverables

Code:

```text
src/chainmind/reports/__init__.py
src/chainmind/reports/token_report.py
```

CLI:

```text
scripts/analyze_dune_token.py --report-output PATH
```

Tests:

```text
tests/unit/test_token_report.py
```

Docs:

```text
docs/progress/2026-06-08-phase5a-report-generation-plan.md
docs/progress/2026-06-08-phase5a-report-generation-check-report.md
docs/engineering/11-phase-file-map.md
```

## 4. Report Sections

The first deterministic report should include:

```text
Summary
Decision
Market Snapshot
Opportunity Signals
Main Risks
Copyability
Wallet Intelligence
Data Quality And Uncertainty
Follow-up Watch Conditions
Evidence Appendix
```

## 5. Acceptance Criteria

Phase 5A is complete when:

```text
python -m pytest passes
generate_token_report() renders stable Markdown
reports include scores, evidence, GMGN summary, and API warnings
analyze_dune_token supports --report-output
the report remains evidence-only and avoids trading instructions
```
