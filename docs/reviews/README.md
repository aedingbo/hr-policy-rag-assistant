# Independent Review Records

This directory stores DeepSeek/Qwen independent review records for
Project 1, as required by `docs/reference/2026 Final AI Bridge Portfolio.pdf`
and `CLAUDE.md` Section 5.

## When a review is required

- At least at each stage milestone: Core implementation, Production
  hardening, Evaluation & optimization, Final benchmark.
- On any change touching authorization, data deletion, evaluation code or
  CI gates.
- On every hand-written core file listed in `HANDWRITTEN.md`.

The reviewer runs locally or through Bedrock, not through a third-party
public API. Never include credentials, secrets or private data in material
sent for review; use sanitized samples when needed.

## Record template

One file per review. Copy this template.

```
# Review: <short title>

- Date:
- Checklist step(s):
- Trigger: stage milestone (<stage>) | authorization | data deletion |
  evaluation code | CI gate | hand-written file
- Reviewer model and version:
- Hosting: local | Bedrock
- Scope reviewed (files/functions, diff reference):
- Sanitized before sending: yes/no (describe)

## Findings

| ID | Severity | File/function | Failure mechanism | Proposed correction | Reproducible test | Classification | Verification evidence | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|---|

Classification: confirmed defect | potential risk | optional improvement
Decision: accepted | rejected | not confirmed

Verification rules:
- Efficiency findings: profiler, EXPLAIN ANALYZE, benchmark or load test
  before and after the fix.
- Missing-test findings: add the test; record whether it failed on the old
  code.
- Findings that cannot be reproduced are recorded as "not confirmed".

## Fixes applied

## Test and eval evidence

## Residual risks

## Summary

- Accepted:
- Rejected:
- Not confirmed:
- Most important caught defect:
```
