# Architecture Decision Record (ADR) Template

## Format

Each ADR follows this structure:

```markdown
## ADR-[N]: [Title]

**Status:** Proposed / Accepted / Deprecated / Superseded by ADR-[M]

**Context:**
[What is the issue that we're seeing that is motivating this decision or change? Include any forces at play: technical, organizational, schedule, constraints.]

**Decision:**
[What is the change that we're proposing and/or doing?]

**Alternatives Considered:**
1. [Alternative A] — [brief description]
2. [Alternative B] — [brief description]
3. [Alternative C] — [brief description]

**Rationale:**
[Why did we choose this option over the alternatives? What are the key tradeoffs?]

**Consequences:**
- [Positive consequence]
- [Negative consequence or risk]
- [What becomes easier or harder to do because of this change]
```

## Example ADRs

### ADR-1: Use PostgreSQL as Primary Database

**Status:** Accepted

**Context:**
The system needs a primary data store for user accounts, orders, and product catalog. The PRD requires ACID transactions for order processing and complex queries for reporting. Team has 3 developers with PostgreSQL experience.

**Decision:**
Use PostgreSQL 15 as the primary relational database.

**Alternatives Considered:**
1. MySQL 8 — widely deployed, but weaker JSON support and fewer advanced index types
2. MongoDB — flexible schema, but no ACID transactions across documents (needed for orders)
3. DynamoDB — fully managed, but single-table design pattern is unfamiliar and limits query flexibility

**Rationale:**
PostgreSQL provides the strongest combination of ACID compliance, query flexibility, and team expertise. JSONB columns handle semi-structured data when needed. The operational burden is acceptable given team experience.

**Consequences:**
- Schema migrations require careful planning (use migration tool)
- Read scaling requires read replicas (not built-in sharding)
- Team can leverage existing knowledge — faster development

### ADR-2: Monolith-First Architecture

**Status:** Accepted

**Context:**
The project is a new system with 2-3 developers. The PRD identifies 4 major functional areas but the team is small and domain boundaries are not yet well-understood. Premature decomposition risks creating distributed monolith.

**Decision:**
Start as a modular monolith with clear internal module boundaries. Design for future decomposition but deploy as a single unit initially.

**Alternatives Considered:**
1. Microservices from day one — allows independent deployment but adds operational complexity disproportionate to team size
2. Serverless functions — good for event-driven workloads but poor fit for the request-response dominant pattern in the PRD

**Rationale:**
A modular monolith preserves deployment simplicity while enforcing boundary discipline internally. When a module needs independent scaling or deployment, it can be extracted with minimal disruption because boundaries are already defined.

**Consequences:**
- Must maintain strict module boundaries internally (no cross-module DB access)
- Single deployment unit means coordinated releases
- Future extraction to microservices is straightforward if boundaries are respected

## Required ADRs

At minimum, the architecture document must include ADRs for:

1. **Service decomposition strategy** — monolith vs microservices vs modular monolith
2. **Tech stack selection** — primary language, framework, and rationale
3. **Data storage selection** — primary database and rationale
4. **Integration protocol selection** — how services/systems communicate

Additional ADRs should be recorded for any decision where:
- There were viable alternatives
- The choice has significant tradeoffs
- Future developers would benefit from understanding why
