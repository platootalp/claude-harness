# Review Process Rule

## Review Flow
1. Document author completes document
2. Author runs /review command
3. Review Agent evaluates against checklist
4. Review Agent outputs decision

## Review Decisions
| Decision | Meaning | Next Step |
|----------|---------|-----------|
| Approved | Document meets all criteria | Proceed to next stage |
| Approved with conditions | Minor issues noted | Proceed, fix in next version |
| Rejected | Major issues must be fixed | Revise and resubmit |

## Review Checklist Categories
- Completeness: All sections filled, no gaps
- Clarity: Unambiguous, implementable language
- Feasibility: Technically achievable
- Testability: Can be verified
- Consistency: Aligns with other documents

## Review Tracking
All reviews are saved to docs/review/ for traceability.
