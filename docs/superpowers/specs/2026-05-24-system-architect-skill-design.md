# System Architect Skill Design

## Overview

A new skill `system-architect` for the spec-workflow plugin. The AI acts as system architect for 0→1 projects — consuming a PRD as input, producing a comprehensive architecture design document covering application, data, infrastructure, and integration dimensions.

## Iron Law

**NO ARCHITECTURE WITHOUT A VALIDATED PRD.** The architect consumes functional requirements; it does not create them. Architecture decisions must trace back to specific PRD requirements. "Validated" means the PRD has been reviewed and approved by the user — the skill asks the user to confirm the PRD is ready before proceeding.

## Responsibility Boundaries

Per industry best practices, the architect skill owns four dimensions and explicitly excludes two:

| Dimension | Owner | Input | Output |
|-----------|-------|-------|--------|
| Application Architecture | Architect (this skill) | Functional requirements from PRD | C4 diagrams, service boundaries, API contracts |
| Information Architecture | Architect (this skill, lead) | Data requirements from PRD | Entity models, data flows, storage strategy |
| Integration Architecture | Architect (this skill) | External dependencies from PRD | Interface contracts, protocols, sync strategy |
| Technical Architecture | Architect (this skill) | Non-functional requirements from PRD | Tech stack, deployment topology, security, observability |
| Functional Architecture | Product (NOT this skill) | — | — |
| Business Architecture | Product (NOT this skill) | — | — |

The architect informs domain boundaries (making the functional model technically viable) but does not define what features exist or why.

## Four-Phase Process

### Phase 1: Context Ingestion

**Input:** PRD document (required)

**Actions:**
- Parse PRD, extract functional requirements, non-functional requirements, constraints
- Identify key quality attributes (performance, availability, security, etc.) and their priority
- Extract external system dependencies and data requirements
- Clarify ambiguities (ask user one question at a time)

**Output:** Structured requirements summary (internalized into subsequent phases, not a standalone document)

### Phase 2: Architecture Design

Designed in dependency order — each dimension builds on the previous:

1. **Application Architecture** (first — subsequent dimensions depend on service boundaries)
   - C4 Context diagram → Container diagram → Component diagram
   - Service/module boundary decomposition
   - API contracts (interface definitions, communication patterns)
   - Key interaction sequences

2. **Information Architecture** (depends on application architecture's service boundaries)
   - Core entities and relationships (domain model)
   - Data flow diagrams
   - Storage strategy (selection, read/write separation, caching)
   - Data consistency approach

3. **Integration Architecture** (depends on application architecture's interface definitions)
   - External system interface contracts
   - Protocol selection and data formats
   - Data synchronization strategy
   - Fault isolation and degradation

4. **Technical Architecture** (depends on constraints from the three above)
   - Tech stack selection (with alternatives and tradeoff reasoning)
   - Deployment topology
   - Security approach
   - Observability approach

**Validation gate after each dimension:** Requirements coverage check — does every PRD requirement have a corresponding architecture element?

### Phase 3: Decision Recording

**Actions:**
- Record an ADR (Architecture Decision Record) for each key architectural decision
- ADR format: Context → Decision → Alternatives Considered → Rationale → Consequences
- Must cover at minimum: service decomposition strategy, tech stack selection, data storage selection, integration protocol selection

**Output:** ADR list (embedded in architecture document)

### Phase 4: Review & Validation

**Actions:**
- Requirements coverage: every PRD requirement mapped to an architecture element
- Consistency check: no contradictions across dimensions
- Feasibility check: tech selections match team capabilities and constraints
- Risk identification: flag high-risk architectural decisions with mitigation measures

**Output:** Architecture document + risk register

## File Structure

```
plugins/spec-workflow/skills/system-architect/
  SKILL.md                              # Main skill definition (process, iron law, checklist)
  references/
    application-architecture.md          # Application architecture guide (C4 templates, service decomposition methods)
    information-architecture.md          # Information architecture guide (entity modeling, data flows, storage strategies)
    integration-architecture.md          # Integration architecture guide (interface contracts, protocol selection, degradation patterns)
    technical-architecture.md            # Technical architecture guide (stack selection framework, deployment patterns, security checklist)
    adr-template.md                      # ADR template and examples
    architecture-review-checklist.md     # Review validation checklist
```

## Output Document Structure

Single architecture design document at `docs/specs/YYYY-MM-DD-<project>-architecture.md`:

```markdown
# [Project Name] System Architecture Design

## 1. Overview
  - Project background (from PRD)
  - Key quality attributes and priority
  - Architecture constraints

## 2. Application Architecture
  ### 2.1 System Context (C4 Context)
  ### 2.2 Container View (C4 Container)
  ### 2.3 Component View (C4 Component)
  ### 2.4 Service Boundaries & API Contracts
  ### 2.5 Key Interaction Sequences

## 3. Information Architecture
  ### 3.1 Domain Model
  ### 3.2 Data Flows
  ### 3.3 Storage Strategy
  ### 3.4 Data Consistency Approach

## 4. Integration Architecture
  ### 4.1 External System Interfaces
  ### 4.2 Protocols & Data Formats
  ### 4.3 Data Synchronization Strategy
  ### 4.4 Fault Isolation & Degradation

## 5. Technical Architecture
  ### 5.1 Tech Stack Selection
  ### 5.2 Deployment Topology
  ### 5.3 Security Approach
  ### 5.4 Observability Approach

## 6. Architecture Decision Records (ADRs)

## 7. Risk Register
```

C4 diagrams use Mermaid (consistent with `system-architecture-analysis` skill):
- Context: `graph LR` or `flowchart LR`
- Container: `graph TB`
- Component: `graph TB`
- Data flow: `flowchart LR`

## Integration with Existing Skills

### Position in spec-workflow pipeline

```
brainstorming → PRD → system-architect → dev-plan → implementation
```

`system-architect` sits **after PRD, before dev-plan**. It consumes PRD output and produces architecture documentation that feeds into the `dev-plan` skill.

### Relationships

| Existing Skill | Relationship |
|---------------|-------------|
| `brainstorming` | Upstream — brainstorming may produce the PRD that feeds this skill |
| `dev-plan-review` | Downstream — reviews development plans based on this skill's architecture output |
| `system-architecture-analysis` (analysis plugin) | Complementary — that skill **analyzes existing** codebase architecture; this skill **designs new** architecture from scratch |
| `codebase-to-docs` (analysis plugin) | Complementary — that generates docs from code; this generates architecture from requirements |
| `using-superpowers` (superpowers-pro) | Integration — superpowers router should route to this skill when architecture design is needed |

### Superpowers router extension

Add routing condition to `using-superpowers`:
- When user is past PRD phase and needs system-level architecture design → route to `system-architect`
- Trigger phrases: "design architecture", "system architecture", "architect from scratch", "architecture design"

### Explicit Non-Goals

- Does NOT design functional architecture (product responsibility)
- Does NOT produce code-level detailed design (dev-plan responsibility)
- Does NOT analyze existing system architecture (system-architecture-analysis responsibility)
- Does NOT teach microservice decomposition methodology in isolation (only applies it in real projects)
