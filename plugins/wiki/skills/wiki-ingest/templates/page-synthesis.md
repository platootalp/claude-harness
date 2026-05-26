---
tags: [{tag1}, {tag2}]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/entities/{entity1}.md
  - wiki/entities/{entity2}.md
status: draft | stable | needs-update
page_type: synthesis
synthesis_type: comparison | analysis | connection
---

# {Synthesis Title}

## Summary

**100-150 words.** Must state the insight or connection discovered. For comparisons: what are the key differences and the overall verdict. For analysis: what argument is being developed and the conclusion. For connections: what relationship was discovered and why it matters.

> **Example:**
> Comparing Claude Code, Cursor, and Codex reveals three distinct approaches to AI coding assistance. Claude Code prioritizes deep model integration and plugin extensibility, Cursor focuses on editor-native AI with a polished CLI agent, and Codex emphasizes cloud-based sandboxed execution for safety. The key finding is that these tools are not direct substitutes — each excels in a different workflow context, and the best choice depends on whether you need local control (Claude Code), editor integration (Cursor), or isolated execution (Codex).

## Analysis

The core content. Structure depends on synthesis_type:

### For comparison (synthesis_type: comparison)

Must include: (1) a comparison table with key dimensions as rows and entities as columns, (2) a narrative analysis of each dimension (50-100 words per dimension), (3) a Verdict section with a clear recommendation.

> **Example:**
> | Dimension | Claude Code | Cursor | Codex |
> |-----------|-------------|--------|-------|
> | Execution | Local CLI | Local CLI + Editor | Cloud sandbox |
> | Model access | Claude only | Multi-provider | OpenAI only |
> | Plugin system | Yes (Plugin Builder) | Limited | No |
> | Permissions | Glob-based allow/deny | Glob-based allow/deny | Sandboxed by default |
> | MCP support | Full | Full | No |
>
> **Execution model**: Claude Code and Cursor run locally, giving developers full control over their environment. Codex runs in a cloud sandbox, which is safer for untrusted code but requires network access and has latency overhead.
>
> **Verdict**: For daily development with trusted codebases, Claude Code or Cursor are preferable due to local execution and richer tool access. For reviewing untrusted code or running in CI, Codex's sandboxed model provides better safety guarantees.

### For analysis (synthesis_type: analysis)

Must include: (1) a clear thesis statement, (2) evidence from source pages supporting the thesis, (3) a counter-argument or limitation, (4) a conclusion. Target 300-500 words total.

### For connection (synthesis_type: connection)

Must include: (1) what the connected pages have in common, (2) how they differ in approach or scope, (3) what new understanding emerges from the connection, (4) why this connection matters. Target 300-500 words total.

## Implications

Must include: (1) at least one actionable recommendation — what should the reader do differently based on this synthesis, (2) at least one new question raised — what should be investigated next.

> **Example:**
> **Recommendation**: Teams evaluating AI coding tools should test all three in their actual workflow rather than choosing based on feature lists alone. The execution model difference (local vs. cloud) has more practical impact than any feature comparison suggests.
>
> **Open question**: How will MCP server ecosystems evolve across tools? If MCP becomes a universal standard, the plugin advantage of Claude Code may diminish, making execution model the primary differentiator.

## See Also

Must use relative-path markdown links. Link to all source pages that contributed to this synthesis.

- [Source Page 1](../entities/{page1}.md) — {description}
- [Source Page 2](../entities/{page2}.md) — {description}

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and states the insight/connection
- [ ] Analysis follows the correct structure for synthesis_type
- [ ] Comparison has table + narrative + verdict
- [ ] Analysis has thesis + evidence + counter-argument + conclusion
- [ ] Connection has commonality + difference + new understanding + why it matters
- [ ] Implications has at least 1 recommendation and 1 new question
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
