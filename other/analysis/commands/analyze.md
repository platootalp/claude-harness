# Analyze Command

Invoke the Analysis Agent to analyze a codebase target.

## Usage
/analyze [target] [--full | --architecture | --inventory]

## Flags
- `--full` — Generate full documentation site (routes to codebase-to-docs)
- `--architecture` — C4 architecture analysis (routes to system-architecture-analysis)
- `--inventory` — Functional point inventory (routes to source-functional-analysis)
- No flag — Deep functional analysis of the target path (routes to deep-functional-analysis)

## Examples
/analyze src/auth/                    → deep-functional-analysis
/analyze --architecture               → system-architecture-analysis
/analyze --full                       → codebase-to-docs (entire project)
/analyze src/auth/ --full             → codebase-to-docs (auth module only)
/analyze --inventory                  → source-functional-analysis

## Description
Routes to the appropriate analysis skill based on the target and flags. The Analysis Agent determines the best analysis type and invokes the matching skill.
