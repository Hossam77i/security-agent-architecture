# ADR-005: Separation of Capability and Authority

**Status:** Accepted
**Context:** Security agents can cause catastrophic damage if they autonomously execute destructive commands.
**Decision:** The agent proposes *intent*. A hardcoded Policy Engine (Tool Gateway) checks *authority* (scope, destructive flags) before execution.
**Consequences:** The agent cannot bypass security rules via prompt injection, as rules are enforced outside the LLM.
