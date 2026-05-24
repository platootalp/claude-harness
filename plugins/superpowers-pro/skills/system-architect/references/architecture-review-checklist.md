# Architecture Review Checklist

Run this checklist after completing all four architecture dimensions. Each check must pass before the architecture document is finalized.

## 1. Requirements Coverage

For each requirement in the PRD:

- [ ] Functional requirement has a corresponding service/component in the application architecture
- [ ] Non-functional requirement (performance, availability, etc.) has a corresponding design element in the technical architecture
- [ ] Data requirement has a corresponding entity and storage strategy in the information architecture
- [ ] External dependency has a corresponding integration contract in the integration architecture

**If any requirement is uncovered:** Go back to the relevant architecture dimension and add the missing element. Do not proceed with gaps.

## 2. Cross-Dimension Consistency

- [ ] Service boundaries in application architecture match data ownership in information architecture (no service accessing another's data directly)
- [ ] API contracts in application architecture match the protocols selected in integration architecture
- [ ] Tech stack in technical architecture supports the communication patterns defined in application architecture
- [ ] Deployment topology in technical architecture supports the availability requirements from the PRD
- [ ] Security approach covers all external interfaces defined in integration architecture
- [ ] Observability covers all services defined in application architecture

**If contradictions found:** Resolve by revisiting the earlier dimension (dependency order: application → information → integration → technical).

## 3. Feasibility

- [ ] Team has experience with the selected tech stack (or has a realistic learning plan)
- [ ] Selected infrastructure is available within the project's cloud/provider constraints
- [ ] Third-party services in integration architecture have accessible APIs and acceptable SLAs
- [ ] Budget constraints from PRD are respected (no expensive managed services if budget is tight)
- [ ] Timeline constraints are realistic given the architecture complexity

**If feasibility issues found:** Adjust tech selections or simplify the architecture. Document the constraint in the risk register.

## 4. Risk Identification

For each risk, document:

```markdown
### Risk: [Title]
**Likelihood:** High / Medium / Low
**Impact:** High / Medium / Low
**Mitigation:** [What to do about it]
**Contingency:** [What to do if it materializes]
```

### Common Risk Categories to Check

- [ ] **Technical risk** — unproven technology, complex integration, performance unknowns
- [ ] **Organizational risk** — team skill gaps, key person dependency, vendor lock-in
- [ ] **Schedule risk** — architecture complexity vs timeline, external dependency availability
- [ ] **Operational risk** — monitoring gaps, deployment complexity, disaster recovery
- [ ] **Security risk** — sensitive data handling, authentication gaps, compliance requirements

## 5. Completeness

- [ ] All C4 levels present (Context, Container, Component for key containers)
- [ ] Domain model covers all entities from PRD
- [ ] All external systems have interface contracts
- [ ] ADRs cover the 4 required decisions (decomposition, tech stack, data storage, integration protocol)
- [ ] Risk register has at least 3 entries
- [ ] Mermaid diagrams render correctly (valid syntax)

## Pass Criteria

All checks in sections 1-4 must pass. Section 5 (Completeness) can have minor gaps if noted in the risk register with a plan to address them.
