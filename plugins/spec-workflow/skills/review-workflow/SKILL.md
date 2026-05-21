---
name: review-workflow
description: Review spec documents before implementation — lightweight 4-point design spec review or heavyweight 7-dimension dev plan review. Use when reviewing design specs, implementation plans, or any document before engineering execution.
---

# Review Workflow

Routes to the appropriate review sub-skill based on document type and review depth needed.

## Decision Matrix

| Your Need | Route To | When |
|-----------|----------|------|
| Review a design spec (lightweight) | `design-spec-review` | Early-stage design specs — check for placeholders, consistency, scope, ambiguity |
| Review an implementation plan (rigorous) | `dev-plan-review` | Pre-execution technical plans — 7-dimension audit with severity levels |

## How to Use

1. Identify the document type and review depth from context
2. Invoke the appropriate sub-skill directly
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **design-spec-review** — 4-point checklist: placeholder scan, internal consistency, scope boundary, ambiguity check. Fast, lightweight, catches spec-level issues before they reach implementation.
- **dev-plan-review** — 7-dimension framework: consistency, correctness, completeness, executability, security, verifiability, operability. Rigorous audit with severity levels (Severe/High/Medium/Low), multi-subagent orchestration, formal archival output.