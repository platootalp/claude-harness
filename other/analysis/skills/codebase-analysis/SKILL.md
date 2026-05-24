---
name: codebase-analysis
description: Analyze codebases using specialized analysis modes — full documentation generation, C4 architecture analysis, deep functional analysis, or functional point cataloging. Use when analyzing a codebase, generating docs, understanding architecture, or cataloging features.
---

# Codebase Analysis

Routes to specialized analysis sub-skills based on your analysis goal.

## Decision Matrix

| Your Need | Route To | What It Produces |
|-----------|----------|------------------|
| Generate full documentation site for a codebase | `codebase-to-docs` | Multi-page documentation site (architecture + workflows) |
| Analyze system/module architecture using C4 model | `system-architecture-analysis` | Single architecture document with C4 diagrams |
| Deep dive into a single mechanism/function | `deep-functional-analysis` | Single question-driven deep-analysis document |
| Catalog all features of a subsystem | `source-functional-analysis` | Single functional point catalog document |

## How to Use

1. Identify which sub-skill matches your need from the decision matrix above
2. Invoke that sub-skill directly — it has its own detailed workflow
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **codebase-to-docs** — Full codebase → multi-page documentation site with dual-axis (architecture + workflows), evidence-backed, depth levels L1/L2/L3
- **system-architecture-analysis** — System/module → C4 model architecture document with Context/Container/Component diagrams
- **deep-functional-analysis** — Single mechanism → question-driven progressive deepening from phenomenon to principle to tradeoff
- **source-functional-analysis** — Subsystem → breadth-first functional point inventory grouped by module