# ADR Rule

Save an Architecture Decision Record when a feature requires its own architecture.

## When to Write an ADR

Write an ADR when a feature:
- Introduces a new architectural pattern or component
- Changes how data flows through the system
- Adds a new integration (database, API, service)
- Makes a non-obvious technical decision with no single clear solution
- Affects multiple modules or layers

## ADR Format

Save to `docs/adr/ADR-XXX-short-title.md`:

```markdown
# ADR-XXX: Short Title

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated
**Context**: What problem or question does this ADR address?

## Decision

What was decided.

## Consequences

- **Positive**: What benefits this brings
- **Negative**: What drawbacks or tradeoffs exist
- **Neutral**: What side effects or things to consider

## Alternatives Considered

What other options were considered and why they were rejected.
```

## Naming

`ADR-XXX` where `XXX` is the next sequential number.
Check existing ADRs: `ls docs/adr/`

## Rule

Before starting implementation on any feature that touches architecture, create the ADR first.
This ensures the architecture is intentional and documented before code is written.