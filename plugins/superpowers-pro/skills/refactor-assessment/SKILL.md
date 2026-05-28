---
name: refactor-assessment
description: Use when evaluating code for refactoring — assessing structure, maintainability, performance, or testability. Triggers include "refactor X", "restructure Y", "clean up Z", or starting the /refactor workflow.
---

# Refactor Assessment

## Overview

Evaluate a code area for refactoring potential. Produces a structured refactor document with current problems, target state, and invariants — not a list of code changes.

**Assess first, refactor later.** You are defining what to change and why, not making changes.

## When to Use

- User asks to refactor/restructure/clean up a module or code area
- /refactor workflow Step 1 (ASSESS)
- Any request about "improve the structure of X" or "make Y more maintainable"

## When NOT to Use

- Bug scanning → use `superpowers-pro:issue-scanning`
- Single bug diagnosis → use `superpowers-pro:systematic-debugging`
- Code review of your own changes → use `superpowers-pro:requesting-code-review`

```dot
digraph when_to_use {
  "User request about code changes" [shape=box];
  "Looking for bugs?" [shape=diamond];
  "Use issue-scanning" [shape=box];
  "Single known bug?" [shape=diamond];
  "Use systematic-debugging" [shape=box];
  "Use refactor-assessment" [shape=box];

  "User request about code changes" -> "Looking for bugs?";
  "Looking for bugs?" -> "Use issue-scanning" [label="yes, multiple"];
  "Looking for bugs?" -> "Single known bug?" [label="no"];
  "Single known bug?" -> "Use systematic-debugging" [label="yes"];
  "Single known bug?" -> "Use refactor-assessment" [label="no"];
}
```

## Process

```dot
digraph refactor_assessment {
  rankdir=TB;
  "1. Confirm target" [shape=box];
  "2. Read current structure" [shape=box];
  "3. Evaluate by dimensions" [shape=box];
  "4. Define target state" [shape=box];
  "5. Identify invariants" [shape=box];
  "6. Assess impact & risk" [shape=box];
  "7. Write refactor document" [shape=box];

  "1. Confirm target" -> "2. Read current structure";
  "2. Read current structure" -> "3. Evaluate by dimensions";
  "3. Evaluate by dimensions" -> "4. Define target state";
  "4. Define target state" -> "5. Identify invariants";
  "5. Identify invariants" -> "6. Assess impact & risk";
  "6. Assess impact & risk" -> "7. Write refactor document";
}
```

### Step 1: Confirm Target

Before reading code, confirm with the user:
- **What** to refactor (module, feature, directory, code area)
- **Why** they want to refactor (pain points, goals)
- **Constraints** (timeline, backwards compatibility, team familiarity)

### Step 2: Read Current Structure

Read all relevant files — code, tests, types, imports. Map the current architecture: module boundaries, data flow, dependency graph. Use subagents for parallel reading when scope is large.

### Step 3: Evaluate by Dimensions

| Dimension | What to assess |
|-----------|---------------|
| Structure | Module boundaries, single responsibility, coupling, cohesion |
| Maintainability | Readability, cyclomatic complexity, duplication, naming |
| Performance | Bottlenecks, unnecessary computation, resource usage |
| Testability | Dependency injection, side-effect isolation, mockability |

Rate each dimension: **Healthy / Needs work / Critical**. Provide evidence, not opinions.

### Step 4: Define Target State

Describe what the code should look like after refactoring:
- New module boundaries and responsibilities
- Changed data flows or interfaces
- Simplified or removed abstractions

**Be specific.** "Improve readability" is not a target. "Extract validation logic into a separate module with a typed interface" is.

### Step 5: Identify Invariants

List behaviors that MUST NOT change during refactoring:
- Public API signatures and return types
- Observed runtime behavior (for untested code, document what it currently does)
- Performance characteristics that users depend on
- Integration points with other systems

**This is the safety net.** If you can't articulate invariants, you can't refactor safely.

### Step 6: Assess Impact & Risk

- **Impact scope**: Which files, modules, teams are affected
- **Risk points**: What could break, how likely, how detectable
- **Migration path**: Can this be done incrementally or is it big-bang

### Step 7: Write Refactor Document

Save to `docs/superpowers-pro/refactors/YYYY-MM-DD-<target>.md`:

```markdown
# 重构评估: <target>

## 当前问题
<why refactor is needed, per dimension>

## 重构目标
<specific target state>

## 行为不变性
<behaviors that must not change>

## 影响范围
<affected files/modules/teams>

## 风险点
<what could break, likelihood, detection>
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Starting to refactor immediately | Assess first. Produce document. Get approval. |
| Vague target state | Be specific about new structure, not just "cleaner" |
| Skipping invariants | No invariants = unsafe refactor. Always list them. |
| Ignoring risk assessment | Every refactor can break things. Assess risk. |
| Scope creep | Stick to the confirmed target. Don't refactor adjacent code. |
| Only listing problems | Problems without a target state leave direction unclear |
