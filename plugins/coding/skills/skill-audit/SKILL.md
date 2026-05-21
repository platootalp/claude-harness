---
name: skill-audit
description: Comprehensive quality and security analysis for Claude Code skills. Evaluates skills across five dimensions (structure 20%, security 30%, UX 20%, code quality 15%, integration 15%) with automated security scanning for 40+ attack patterns. Use when analyzing skill quality, checking security, auditing skills, or certifying skill readiness.
---

# Skill Audit

Comprehensive quality and security analysis for Claude Code skills. Evaluates across five dimensions with integrated security scanning.

## Output Modes

1. **Comprehensive Report** — Detailed markdown report with numerical scores (0-100) across all dimensions
2. **Interactive Review** — Step-by-step analysis with specific, actionable recommendations
3. **Pass/Fail Certification** — Binary quality assessment with specific issues blocking certification

## Evaluation Dimensions

### 1. Structure & Documentation (20%)

- SKILL.md exists and follows best practices
- Proper YAML frontmatter (name, description fields)
- Clear description with trigger phrases
- Well-organized sections (Overview, When to Use, Workflow, Resources)
- Examples, templates, and usage guidance provided

**Scoring:**
- 90-100: Exemplary documentation, comprehensive examples
- 70-89: Good documentation with minor gaps
- 50-69: Basic documentation lacking detail
- 0-49: Missing critical documentation

### 2. Security (30%)

Automated scanning for 40+ malicious patterns across 6 analysis phases:

**Phase 1: Structural Validation** — SKILL.md exists, MANIFEST.json integrity, directory structure

**Phase 2: YAML Frontmatter** — Parse with `yaml.safe_load()`, detect `!!python` directives, `__proto__` pollution

**Phase 3: Comprehensive File Scanning** — ALL text files, scripts/, references/, assets/, SKILL.md content

**Phase 4: Import Analysis** — Extract imports, typosquatting detection (Levenshtein distance <= 2), validate against known packages

**Phase 5: Cross-File Analysis** — Data flow between files, user input sources, dangerous operation sinks

**Phase 6: Anomaly Detection** — Obfuscation ratio, unusual patterns, statistical outliers

**Severity Ratings:**

| Severity | Examples | Security Score Impact |
|----------|----------|----------------------|
| CRITICAL | Command injection, credential theft, YAML injection, sandbox escape | 0-40 |
| HIGH | Advanced encoding (ROT13/zlib/XOR), time bombs, environment hijacking, data exfiltration | 50-69 |
| MEDIUM | Obfuscated code (Base64/hex), hardcoded secrets, undocumented network calls | 70-89 |
| LOW | Missing MANIFEST.json checksums, documentation gaps | 90-100 |

**Detection highlights:**
- Indirect execution: `getattr(os, 'system')`, `__builtins__` access
- Shell injection: `bash -c`, `python -c`, `perl -e` in subprocess
- Typosquatting: `request` vs `requests`, `urlib` vs `urllib`
- Time bombs: datetime conditionals near dangerous ops
- Environment manipulation: `LD_PRELOAD`, `PATH` manipulation

### 3. User Experience (20%)

- Clear, specific trigger phrases
- Well-documented workflow with step-by-step guidance
- Helpful, practical examples
- Appropriate use of references/ for detailed info
- Clear scope definition (when to use vs. not use)

**Scoring:**
- 90-100: Exceptional UX, immediately clear how to use
- 70-89: Good UX with minor confusion points
- 50-69: Usable but requires effort to understand
- 0-49: Confusing, unclear, or poorly organized

### 4. Code Quality (15%)

- Proper resource organization (references/, scripts/, assets/)
- Clear, maintainable structure
- Scripts are well-documented and safe
- No unnecessary complexity
- Consistent formatting and style

**Scoring:**
- 90-100: Exemplary code quality and organization
- 70-89: Good quality with minor issues
- 50-69: Acceptable but could be improved
- 0-49: Poor quality, hard to maintain

### 5. Integration & Tools (15%)

- Appropriate tool/skill invocation patterns
- Proper MCP integration (if applicable)
- Efficient resource usage
- Scripts properly integrated
- Clear integration documentation

**Scoring:**
- 90-100: Perfect tool integration and efficiency
- 70-89: Good integration with minor improvements possible
- 50-69: Basic integration, missing optimization opportunities
- 0-49: Poor integration or misuse of tools

## Analysis Workflow

1. **Understand source & mode** — Get skill source (GitHub URL, marketplace link, ZIP, local dir) and analysis mode
2. **Read SKILL.md** — Understand purpose, use cases, capabilities, workflow
3. **Run security analysis** — Execute 6-phase security scanning
4. **Evaluate structure & documentation** — Check frontmatter, sections, examples, resources
5. **Evaluate user experience** — Review from user perspective, check anti-patterns
6. **Evaluate code quality** — Review directory structure, scripts, formatting
7. **Evaluate integration & tools** — Check tool usage, MCP integration, resource efficiency
8. **Generate output** — Produce report based on selected mode

## Recommendations

### REJECT (Do Not Install)
- Any CRITICAL findings
- 3+ HIGH findings
- Evidence of command injection, credential theft, data exfiltration, YAML injection

### REVIEW (Manual Inspection Required)
- 1-2 HIGH findings
- 5+ MEDIUM findings
- Patterns requiring context (documented network calls, scoped file operations)

### APPROVE (Safe to Install)
- No CRITICAL/HIGH findings
- <5 MEDIUM findings
- All functionality documented, input validation present

## Certification Requirements

To pass certification:
- Overall score >= 70/100
- Security score >= 80/100
- Structure score >= 70/100
- UX score >= 70/100
- Code Quality score >= 60/100
- Integration score >= 60/100
- No CRITICAL security findings

## Grading Scale

- 90-100 (A+/A): Excellent
- 80-89 (B+/B): Good
- 70-79 (C+/C): Acceptable
- 60-69 (D): Needs Improvement
- 0-59 (F): Poor

## Quick Start

```bash
# Scan a single skill
python3 scripts/security_scanner.py /path/to/skill

# Scan with verbose output
python3 scripts/security_scanner.py /path/to/skill --verbose

# Scan all installed skills
python3 scripts/security_scanner.py ~/claude/skills/ --recursive

# Output to JSON
python3 scripts/security_scanner.py /path/to/skill --output report.json

# Run test suite
python3 scripts/test_scanner.py
```

## Anti-Patterns to Flag

| Category | Anti-Patterns |
|----------|---------------|
| Structure | Missing frontmatter, vague description, no "When to Use", no examples |
| Security | Command injection, hardcoded secrets, unsafe file ops, YAML injection, obfuscated code |
| UX | Unclear purpose, missing triggers, confusing workflow, no examples |
| Code Quality | Messy structure, undocumented scripts, inconsistent formatting |
| Integration | Tool overuse/underuse, inefficient resource loading, missing MCP |

## Resources

For detailed security detection patterns, quality rubrics, and report templates, see [references/](references/).