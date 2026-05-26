# Wiki Ingest Quality Rubric

Used by the LLM judge to score wiki page output quality.

## Scoring

Score each dimension 0-5. Calculate the weighted total (0-5 scale). Passing threshold: 3.5/5.

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 25% | Are all key information from the source extracted and present in the wiki page? |
| Accuracy | 25% | Is the content factually consistent with the source material? No invented details. |
| Structure | 15% | Does the page follow its template? All required sections present, correct frontmatter. |
| Depth | 20% | Does each section meet the depth target? Not just 1-2 sentence summaries. |
| Cross-references | 15% | Are links present, correctly formatted (relative-path markdown), and pointing to relevant pages? |

## Dimension Details

### Completeness (25%)

| Score | Criteria |
|-------|----------|
| 0 | Major information from the source is missing — key features, concepts, or details not mentioned |
| 1 | Several important points missing; page covers less than half the source's content |
| 2 | Some important points missing; page covers about half the source's content |
| 3 | Most important points present; minor details may be missing |
| 4 | Nearly all important points present; only trivial details missing |
| 5 | All key information extracted and synthesized; nothing important is missing |

### Accuracy (25%)

| Score | Criteria |
|-------|----------|
| 0 | Contains factual errors that contradict the source material |
| 1 | Multiple errors or significant misrepresentations |
| 2 | A few errors or oversimplifications that change the meaning |
| 3 | Mostly accurate with minor imprecisions that don't change meaning |
| 4 | Accurate with only trivial imprecisions |
| 5 | Fully consistent with source material; no errors or misrepresentations |

### Structure (15%)

| Score | Criteria |
|-------|----------|
| 0 | Does not follow template at all; missing major sections |
| 1 | Follows template loosely; several sections missing or misplaced |
| 2 | Follows template partially; some sections present, some missing |
| 3 | Follows template mostly; all major sections present but some subsections missing |
| 4 | Follows template well; all sections present with minor formatting issues |
| 5 | Follows template completely; all sections present, correct frontmatter, proper formatting |

### Depth (20%)

| Score | Criteria |
|-------|----------|
| 0 | Every section is 1-2 sentences; no substance |
| 1 | Most sections are shallow; only 1-2 sentences each |
| 2 | Some sections have depth; others are shallow |
| 3 | Most sections meet minimum depth targets |
| 4 | All sections meet depth targets with some exceeding them |
| 5 | All sections are thorough with definition + example + edge case where applicable |

### Cross-references (15%)

| Score | Criteria |
|-------|----------|
| 0 | No cross-references at all, or all use wrong format (wikilinks instead of relative paths) |
| 1 | Very few cross-references; most expected links missing |
| 2 | Some cross-references present but format inconsistent or links point to wrong targets |
| 3 | Most expected cross-references present; format mostly correct |
| 4 | All expected cross-references present with correct format |
| 5 | All expected cross-references present, correctly formatted, and linking to the most relevant pages |

## Output Format

Return scores as JSON:

```json
{
  "completeness": { "score": 0, "reason": "..." },
  "accuracy": { "score": 0, "reason": "..." },
  "structure": { "score": 0, "reason": "..." },
  "depth": { "score": 0, "reason": "..." },
  "cross_references": { "score": 0, "reason": "..." },
  "weighted_total": 0.0,
  "pass": false
}
```

Weighted total = completenessx0.25 + accuracyx0.25 + structurex0.15 + depthx0.20 + cross_referencesx0.15
Pass = weighted_total >= 3.5
