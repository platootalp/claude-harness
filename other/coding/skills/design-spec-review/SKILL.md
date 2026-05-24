---
name: meta-design-spec-review
description: |
  A 4-point checklist for reviewing design specs before implementation. Use this
  skill whenever the user has written a design spec, wants to review one, or asks
  "is my spec ready" or "check this design." Prevents placeholder bugs, internal
  contradictions, and scope creep from reaching implementation.
when_to_use: |
  After writing any design spec (from brainstorming, feature planning, or any design
  work). Run before committing, presenting to stakeholders, or handing off to
  implementation.

  Example trigger phrases:
  - "I've written the design spec for X"
  - "Review this design before we implement"
  - "Is this spec ready for planning?"
  - "Check the design doc for placeholders"
paths: ["**/*"]
allowed-tools: Read Grep
version: "1.0.0"
---

# Design Spec Self-Review

A systematic 4-point checklist for validating design specs before they reach
implementation. Catches placeholder bugs, internal contradictions, scope issues,
and ambiguity early — when they're cheap to fix.

## When to use

After writing a design spec from brainstorming or any feature planning session.
Before committing the spec, presenting it to stakeholders, or handing it off for
implementation.

**Not for**: reading existing codebases, debugging runtime issues, or reviewing
implementation details. This is a spec-level review only.

## Steps

### 1. Placeholder Scan

Search for incomplete markers that indicate unfinished work:

```
TBD, TODO, FIXME, XXX, ..., [PLACEHOLDER], [INSERT], [FILL IN], ???
```

Use `Grep` with case-insensitive flag across the entire spec file.

**Action**: Complete every placeholder, or explicitly mark it as deferred with
a `**Deferred to implementation:**` note and a specific reason.

### 2. Internal Consistency

Cross-check the spec's own parts for contradictions:

- Do the acceptance criteria match the feature descriptions?
- Are all referenced config keys defined in the Config interface?
- Are interface changes consistent with usage throughout?
- Is every feature in the spec fully described (not just named)?
- Are there any features referenced but not defined?

**Action**: Fix contradictions immediately. Document unresolved trade-offs with
a `**Trade-off noted:**` prefix so they don't get lost.

### 3. Scope Boundary

Verify the spec clearly delimits what is and isn't included:

- Is there an explicit "Out of Scope" section?
- Are there implicit dependencies on P0/P1/P2 features that aren't in scope?
- Are edge cases addressed or explicitly deferred?
- Does the acceptance criteria scope match the feature scope?

**Action**: Add or expand the "Out of Scope" section. If edge cases are deferred,
mark each with `**Deferred to [phase]:**` and the specific phase name.

### 4. Ambiguity Check

Replace vague language with specific, measurable criteria:

Replace vague terms with concrete definitions:
- "appropriate" → specific threshold or rule
- "reasonable" → exact bound or documented justification
- "some" / "few" → actual count or percentage
- Technology choices without rationale → add one line of trade-off reasoning

Check for:
- Numeric values (e.g. timeout, max retries) without justification
- "should" / "may" / "might" without explicit fallback behavior
- Any `...` in code examples

**Action**: For every ambiguous phrase, either replace it with a specific rule
or add a one-line rationale for why it was left open.

## Example

**Scenario**: A user has written a design spec for a new API endpoint and asks
you to review it before implementation.

**Walkthrough**:
1. Grep for `TBD`, `TODO`, `XXX` → none found. Placeholder scan: pass.
2. Notice the spec references `max_retries` config but it's not in the Config
   interface. Add it or mark as deferred.
3. The spec mentions "we'll handle rate limiting" but has no Out of Scope section.
   Add one explicitly excluding rate limiting for this iteration.
4. The spec says "use an appropriate timeout." Replace with "60 second timeout"
   and note the justification: "matches the existing downstream service SLA."

**Outcome**: Spec is clean, consistent, and ready to hand off to implementation
planning. No surprises in code review.

## Common pitfalls

- **Skipping the review "because the spec looks good"**: Spec bugs are cheap to
  fix at this stage, expensive to fix in implementation. Treat the checklist
  as mandatory.

- **Fixing style issues instead of substance**: The checklist is about
  correctness, not prose quality. Don't rewrite sentences — verify the content.

- **Treating it as optional**: Every spec should go through this before
  implementation. Even small, obvious features benefit from a consistency check.
