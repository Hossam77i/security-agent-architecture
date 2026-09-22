# Security Boundaries

RA SECURITY relies on strict boundaries where security enforcement happens *outside* the LLM. 

## Capability vs. Authority
The core principle of this architecture is **Capability ≠ Authority**.
*   **Capability**: The agent (LLM) knows *how* to perform an action (e.g., it knows the syntax for `sqlmap --drop`).
*   **Authority**: The system decides if the action is *permitted*. 

The LLM never defines its own authority. It proposes a plan, and the **Tool Gateway** enforces policy.

## The Execution Boundary
1.  **Agent Reasoning**: Proposes an action and target.
2.  **Policy / Scope Check**: Verifies the target is in the allowlist and the action is non-destructive.
3.  **Tool Gateway**: Receives the approved action.
4.  **Sandbox Execution**: The tool is run in an isolated environment.
5.  **Observation Layer**: The output is caught, parsed, and sanitized before returning to the LLM.

Security-sensitive controls are hardcoded programmatic checks, not natural language prompt instructions.
