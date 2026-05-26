---
name: web-ui-ux-review-orchestrator
description: Review and fix UI/UX issues in web pages. Use whenever the user reports layout bugs, chart failures, or asks to improve page design.
when_to_use: |
  Use when the user asks to review, audit, or fix UI/UX issues in a web page or component.
  Common triggers: "this page looks bad", "the table is broken", "charts are not rendering",
  "fix the layout", "improve the UI", "button alignment is wrong", "find UI issues".
paths: ["**/*"]
version: "1.0.0"
trust: agent-created
---

# UI/UX Review Orchestrator

Helps systematically review and fix UI/UX issues in web pages or components.
Combines a UI review skill with parallel subagent remediation to efficiently
address multiple visual and interaction bugs in a single pass.

## When to use

- The user says a page "looks bad", has "many bugs", or asks to "fix the UI/UX"
- Specific complaints: misaligned buttons, wrong column widths, charts not rendering,
  pagination broken, poor visual hierarchy, dark mode issues
- The user wants both issue identification AND fixes applied (not just a report)
- **Avoid** when the user only wants a quick opinion or a single obvious fix —
  just edit directly instead

## Steps

1. **Invoke the UI review skill** (e.g. `ui-ux-pro-max`) on the target file to surface issues
2. **Read the target file** and explore related files — sibling components, parent layouts,
   shared style patterns, and third-party library setup (e.g. ECharts, Naive UI)
3. **Write a structured issues document** to `docs/<feature>-ui-issues.md` with severity
   levels (Critical/High/Medium) and specific fixes
4. **Create tracking tasks** for each fix category using `TaskCreate`, grouping related
   fixes to minimize agent count
5. **Dispatch parallel subagents** to fix the issues. Provide each agent with:
   - Exact file paths
   - The specific bug description and root cause
   - The exact code change required
6. **Verify changes** after agents complete by reading modified files to ensure consistency
7. **Mark tasks complete** and summarize the fixes in a table format

## Example

**Scenario**: The user says "the dashboard page is broken — buttons are misaligned,
charts do not show up, and the table looks wrong".

**Walkthrough**:
1. Invoke `ui-ux-pro-max` on `src/views/dashboard/index.vue`
2. Read the file and explore `src/components/charts/`, check ECharts registration,
   and inspect other dashboard pages for layout patterns
3. Write `docs/dashboard-ui-issues.md` listing 8 issues with severity and file locations
4. Create tasks: "Fix chart rendering", "Fix table pagination", "Fix layout and colors"
5. Dispatch 3 agents in parallel, each with precise file paths and fix instructions
6. Read the modified files to confirm changes are consistent and do not conflict
7. Mark all tasks complete and present a summary table

**Outcome**: All identified issues are documented and fixed in one coordinated pass,
with an audit trail in `docs/`.

## Common pitfalls

- **Forgetting to explore dependencies** — a broken chart may be caused by a missing
  ECharts component registration, not the chart component itself. Always check library
  setup files.
- **Inline objects in templates** — pagination configs, style objects, and option literals
  recreated on every render cause subtle state loss. Watch for these during review.
- **Too many agents** — group fixes by file or concern to avoid agent sprawl. 3-4 parallel
  agents is usually the sweet spot.
- **Skipping verification** — parallel agents can make conflicting edits. Always read the
  final state of modified files before declaring success.
