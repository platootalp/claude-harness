---
tags: [<tag1>, <tag2>]
date: YYYY-MM-DD
last_updated: YYYY-MM-DD
sources:
  - wiki/sources/<source1>.md
status: draft | stable | needs-update
page_type: concept
---

# <Concept Name>

## Summary

<100-150 words. Must cover three things: (1) what the concept is — a clear definition, (2) why it matters — the problem it solves or the value it provides, (3) what distinguishes it from related concepts. Write as a single cohesive paragraph.>

<example>
The LLM Wiki pattern is a knowledge management approach where an LLM maintains a structured wiki from raw source documents. Unlike traditional wikis where humans write and organize content, the LLM Wiki delegates all bookkeeping — summarizing, cross-referencing, filing, and updating — to the LLM. The human's role shifts to curating sources, directing analysis, and asking questions. This pattern matters because it makes personal knowledge bases viable for individuals who lack the time for manual wiki maintenance, while producing more structured and cross-referenced output than simple note-taking tools.
</example>

## Core Idea

<200-400 words. This is the heart of the concept page. Must include: (1) the mental model — how to think about this concept, (2) the key insight — the non-obvious thing that makes it work, (3) how it works step-by-step — the mechanism or process. Write in depth; this section should leave the reader with a solid understanding they could explain to someone else.>

<example>
The LLM Wiki pattern is built on a three-layer architecture that separates concerns between source material, synthesized knowledge, and schema conventions.

The first layer is **raw sources** — immutable documents that serve as ground truth. These are never modified after creation, which means they can always be used to re-synthesize wiki pages if the synthesized layer becomes stale or contradictory. Think of raw sources as the "primary sources" in academic research.

The second layer is **wiki pages** — LLM-generated synthesis organized by type (source summaries, entities, concepts, syntheses). Each page type has a different structure optimized for its purpose: entity pages have domain-specific Key Areas, concept pages explore ideas in depth, and synthesis pages capture insights that emerge from cross-referencing multiple sources. The key insight is that organizing by page type rather than by domain produces better structure — an entity page and a synthesis page about the same domain have fundamentally different shapes.

The third layer is **schema conventions** (embodied in CLAUDE.md and templates) — the rules that tell the LLM how to structure the wiki. This layer is co-evolved between human and LLM over time, as you discover what works for your domain.

The workflow is: ingest a source → the LLM reads it, discusses key points with the human, then writes source summary + entity/concept pages, updates the index and overview, and adds cross-references to related pages. Over time, the wiki compounds — query answers get filed as synthesis pages, creating new connections that weren't visible from any single source.
</example>

## Applications

<2+ concrete scenarios, each 50-100 words. Show how the concept manifests in different contexts. Each scenario should be specific enough that a reader can see how to apply the concept themselves.>

<example>
**Personal knowledge base for a developer**: A developer collects documentation from multiple AI coding tools (Claude Code, Cursor, Codex). Each tool's docs get ingested as a source, producing entity pages with structured Key Areas. When the developer wonders "which tool has the best permission model?", a query produces a comparison synthesis page that persists for future reference.

**Research notebook for a team**: A research team ingests papers, meeting notes, and internal docs. The wiki grows to include concept pages for key ideas and synthesis pages connecting findings across sources. New team members can query the wiki to get up to speed without reading every raw source.
</example>

## Trade-offs

<Must include: (1) at least one limitation or scenario where the concept breaks down, (2) at least one alternative approach and when to prefer it. Be honest — every concept has weaknesses.>

<example>
The main limitation is **trust in synthesis quality**. The LLM may introduce subtle errors during summarization that are hard to detect without re-reading the original source. This is mitigated by the raw source layer (always available for verification) and the lint skill (which checks for contradictions), but it remains a fundamental trade-off: you gain maintenance-free structure at the cost of potential synthesis errors.

An alternative approach is **Zettelkasten** (manual note-linking), which gives the human full control over connections and ensures every link represents a genuine insight. Prefer Zettelkasten when the domain requires precise, expert-validated connections (e.g., legal reasoning, medical knowledge). Prefer LLM Wiki when the volume of sources makes manual maintenance impractical and approximate synthesis is acceptable.
</example>

## See Also

<Must use relative-path markdown links. At least 2 cross-references.>

- [Related Concept](./<concept>.md) — <one-line reason for the link>
- [Source Summary](../sources/<source>.md) — <the source this was derived from>

<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary is 100-150 words and covers what/matters/distinguishes
- [ ] Core Idea is 200-400 words with mental model + key insight + step-by-step
- [ ] Applications has 2+ concrete scenarios, each 50-100 words
- [ ] Trade-offs includes at least 1 limitation and 1 alternative
- [ ] Cross-references use relative-path markdown links (not wikilink)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
