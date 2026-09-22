# ADR-006: Token Efficiency as a Core Metric

**Status:** Accepted
**Context:** Long-running security tasks can easily burn hundreds of dollars in API costs if unoptimized.
**Decision:** We treat token efficiency as a first-class metric. The goal is maximizing useful security task performance per unit of compute.
**Consequences:** Forces parallel tool execution, minimal loops, and aggressive output compression.
