# Wiki Plugin Quality & Eval System Design

## Problem

Three issues with the wiki plugin:

1. **Output path wrong** — wiki data (`raw/`, `wiki/`) is written to the user's project directory instead of the plugin's own directory. Users expect the data to live alongside the plugin, with configurable override.
2. **Document quality low** — templates are skeleton-only (~20 lines each with `<placeholder>` hints), giving the agent insufficient guidance to produce thorough, long-form wiki pages. Entity pages end up with 1-2 sentence sections instead of substantive content.
3. **No evaluation** — there's no way to measure whether the plugin produces good output, making it impossible to iterate on quality systematically.

## Approach

Incremental enhancement (方案 A): enhance existing templates in-place, add path configuration, build a lightweight LLM-as-judge eval system. Minimal disruption, fast to implement.

---

## 1. Data Path

### Current state

`raw/` and `wiki/` live at the plugin root. Skills use relative paths with no configuration.

### New structure

```
plugins/wiki/
  data/              ← new data root
    config.json      ← plugin configuration
    raw/             ← migrated from plugins/wiki/raw/
    wiki/            ← migrated from plugins/wiki/wiki/
  skills/
  agents/
  ...
```

### Config file

`data/config.json`:

```json
{
  "dataDir": "."
}
```

- `dataDir`: path to the data directory, relative to the plugin root (`plugins/wiki/`). `"."` means the `data/` directory itself. Can also be an absolute path. All skills resolve `raw/` and `wiki/` inside this directory.
- Skills read `data/config.json` at startup, resolve `raw/` and `wiki/` relative to the resolved `dataDir` path.

### Migration

Move `raw/` and `wiki/` into `data/`. Update all path references in SKILL.md files, CLAUDE.md, and the wiki-maintainer agent.

---

## 2. Template Enhancement

### Strategy

Keep existing template structure (section names, frontmatter). Add to each section:
1. **Depth targets** — word count or content requirements (e.g., "150-300 words per Key Area")
2. **Example content** — wrapped in `<example>` tags showing expected depth and style
3. **Quality checklist** — self-check items at the end of each template

### Per-template changes

#### `page-entity.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| Summary | "One-paragraph synthesis" | 100-150 words. Must cover: what it is, what it does, key differentiator from similar entities |
| Key Areas | "2-5 sentences per area" | 150-300 words per area. Must include: definition, concrete example, edge case or limitation. Omit areas with no applicable content |
| See Also | placeholder | Must use relative-path markdown links (not wikilinks). At least 2 cross-references |

Add Quality Checklist at end.

#### `page-source.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| Summary | "One-paragraph summary" | 100-150 words. Must cover: what the source is, what it covers, key takeaways |
| Key Points | "5-10 points" | 8-15 points, each 1-2 sentences. Numbered. Cover the most important information |
| Notable Details | "specific details worth preserving" | Must include at least 3 specific items: exact commands, configuration values, version-specific behavior, or edge cases |

Add Quality Checklist at end.

#### `page-concept.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| Summary | "One-paragraph synthesis" | 100-150 words. Must cover: what the concept is, why it matters, what problem it solves |
| Core Idea | "Explain the concept in depth" | 200-400 words. Must include: mental model, key insight, how it works step-by-step |
| Applications | "Where is this applied" | 2+ concrete scenarios with context. Each scenario 50-100 words |
| Trade-offs | "Limitations, when it breaks down" | Must include at least 1 alternative approach and when to prefer it |

Add Quality Checklist at end.

#### `page-synthesis.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| Summary | "One-paragraph synthesis" | 100-150 words. Must state the insight or connection discovered |
| Analysis | No structural guidance | For comparison: must include a comparison table + verdict section. For analysis: argument + evidence from source pages + counter-argument. For connection: explain relationship + new understanding |
| Implications | "What does this mean" | Must include at least 1 actionable recommendation and 1 new question raised |

Add Quality Checklist at end.

#### `page-overview.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| Domains | "2-3 sentences per domain" | 100-200 words per domain. Must link to key entity and concept pages |
| Active Questions | placeholder | Must be specific questions, not vague statements. Each question should suggest what source or analysis could resolve it |
| Recent Activity | "Last 3-5 log entries" | Summarize last 5 log entries with dates |

Add Quality Checklist at end.

#### `raw-source.md`

| Section | Current | Enhanced |
|---------|---------|----------|
| frontmatter | basic fields | Add guidance: `media` field definitions, `domain` naming convention (kebab-case, match directory name under `raw/`) |

### Quality Checklist template

Appended to each page template as HTML comments (not rendered in output):

```markdown
<!-- Quality Checklist (self-check before finalizing)
- [ ] Summary captures the essence in the target word range
- [ ] Each substantive section meets depth requirements
- [ ] Cross-references use relative-path markdown links (not wikilinks)
- [ ] No content is copied verbatim from source — all synthesized
- [ ] All placeholder values replaced with real content
- [ ] Frontmatter fields are complete and accurate
-->
```

---

## 3. Evaluation System

### Architecture

```
skills/wiki-ingest/evals/
  rubric.md           ← scoring criteria (5 dimensions, 0-5 each)
  samples/
    input/            ← raw source inputs for testing
    expected/         ← golden sample wiki pages (expected output)
  run-eval.sh         ← eval runner script (calls Claude API as judge)
  results/            ← eval output (gitignored)
```

### Rubric (5 dimensions)

| Dimension | Weight | 0 points | 5 points |
|-----------|--------|----------|----------|
| Completeness | 25% | Major information missing from source | All key information extracted and synthesized |
| Accuracy | 25% | Factual errors vs. source | Fully consistent with source material |
| Structure | 15% | Does not follow template | Follows template completely, all sections present |
| Depth | 20% | Each section is 1-2 sentences | Each section has definition + example + edge case |
| Cross-references | 15% | No references or wrong format | Complete, correctly formatted relative-path links |

**Total score**: weighted sum, 0-5 scale. Passing threshold: 3.5/5.

### Eval samples

Start with 3 input/expected pairs from existing data:
1. A short raw source (~500 words) → entity page
2. A medium raw source (~1500 words) → entity page with many Key Areas
3. A long raw source (~3000+ words) → entity page + source page

Golden samples are hand-curated wiki pages that demonstrate the target quality level.

### Eval runner

`run-eval.sh`:
1. For each sample: run wiki-ingest on the input source (or use pre-generated output)
2. Call Claude API with: rubric + expected output + actual output → structured JSON scores per dimension
3. Aggregate scores across samples
4. Output summary report to `results/`

Requirements:
- `ANTHROPIC_API_KEY` environment variable
- `jq` for JSON processing
- Claude model for judging (default: claude-sonnet-4-6 for cost efficiency)

### Industry best practices referenced

- **Anthropic eval framework**: rubric-based LLM judging with periodic human calibration
- **OpenAI evals**: input/expected sample pairs with automated scoring
- **Key principle**: define rubric first, write golden samples second, run automated eval third
- **Anti-pattern**: relying solely on LLM judging without human calibration leads to judge drift over time

### Future improvements (not in scope)

- Human calibration step (periodic manual review of LLM judge scores)
- CI integration (run evals on PR)
- Query and lint skill evals
- Regression tracking over time

---

## Scope

This design covers:
- Data path migration + config.json
- Template enhancement (all 6 page templates + raw-source template)
- Eval system (rubric, 3 samples, runner script)

Not in scope:
- Query/lint skill improvements
- Human calibration workflow
- CI integration
- Template restructuring (keeping current structure, just enhancing content)
