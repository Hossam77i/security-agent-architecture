# ADR-002: Separation of Memory and Context

**Status:** Accepted
**Context:** Injecting the entire conversation history into the prompt causes Context Saturation.
**Decision:** Implement a Context Manager. The LLM only sees the current state, active hypothesis, and summarized observations. History is moved to Episodic Memory.
**Consequences:** Massive token savings and prevention of context window collapse, requiring a robust retrieval mechanism.
