# ADR-001: The LLM is Not the Entire Architecture

**Status:** Accepted
**Context:** Standard AI agents wrap a single LLM with a loop and tool access. This fails in cybersecurity due to hallucinations, context loss, and safety risks.
**Decision:** We restrict the LLM purely to the "Reasoning" and "Language" nodes. Memory, planning, evaluation, and execution are handled by deterministic Python/system boundaries.
**Consequences:** Increased engineering complexity, but guarantees strict safety boundaries and deterministic control flow.
