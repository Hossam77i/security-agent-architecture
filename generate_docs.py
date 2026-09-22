import os

docs = {
    "docs/security/threat-model.md": """# Threat Model

## 1. Prompt Injection & Indirect Prompt Injection
*   **Attack Surface**: External web pages, server banners, log files read by the agent.
*   **Potential Impact**: An attacker can hijack the agent's instructions, forcing it to attack out-of-scope targets or exfiltrate data.
*   **Architectural Control**: Isolate & Parse Gateway. All tool outputs are parsed into deterministic JSON schemas. The agent never reads raw, untrusted HTML directly into its reasoning prompt.
*   **Current Status**: 🟢 CURRENT

## 2. Malicious Tool Output
*   **Attack Surface**: Tool execution layer (e.g., a reverse shell payload disguised as `nmap` output).
*   **Potential Impact**: The agent attempts to execute code embedded in tool output.
*   **Architectural Control**: Strict separation of reasoning from execution. Tools run in a sandboxed container. Tool selection requires pre-approved schemas.
*   **Current Status**: 🟢 CURRENT

## 3. Credential Exposure
*   **Attack Surface**: Agent memory, debug logs, observability streams.
*   **Potential Impact**: Leaking valid credentials discovered during testing.
*   **Architectural Control**: Secrets filtering at the Observation Layer before data enters long-term memory.
*   **Current Status**: 🟡 EXPERIMENTAL

## 4. Scope Confusion
*   **Attack Surface**: Redirects, linked domains, third-party CDNs.
*   **Potential Impact**: Agent attacks unauthorized infrastructure.
*   **Architectural Control**: Preflight Gate. Every requested URL/IP is checked against a hardcoded scope allowlist before execution.
*   **Current Status**: 🟢 CURRENT

## 5. Unsafe Execution
*   **Attack Surface**: The Tool Gateway.
*   **Potential Impact**: Agent runs destructive commands (e.g., `DROP TABLE`).
*   **Architectural Control**: Capability vs. Authority separation. The agent proposes intent; the Policy engine verifies authority. Dangerous flags are hard-blocked.
*   **Current Status**: 🟢 CURRENT
""",
    "docs/architecture/security-boundaries.md": """# Security Boundaries

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
""",
    "docs/architecture/observability.md": """# Observability

This architecture ensures complete transparency into the agent's internal state, reasoning, and actions.

## Answerable Questions
*   **What did the agent do?** Tracked via `tool_executed` events in the Tool Gateway.
*   **Why did it do it?** Tracked via `hypothesis_created` and `plan_created` states in the Planning Layer.
*   **What information did it use?** Logged via `context_retrieved` events.
*   **What did it learn?** Tracked via `knowledge_extracted` in the Evaluation Layer.
*   **How much did it cost?** Captured per-task via the Token Optimization Module.

## Conceptual Event Lifecycle
1.  `task_started`
2.  `context_retrieved`
3.  `hypothesis_created`
4.  `plan_created`
5.  `tool_requested`
6.  `policy_checked` (Security Boundary)
7.  `tool_executed`
8.  `observation_received`
9.  `evaluation_started`
10. `knowledge_extracted`
11. `task_completed`

*Note: The observability pipeline strips all secrets, tokens, and credentials before logging.*
""",
    "docs/architecture/decisions/ADR-001-llm-not-architecture.md": """# ADR-001: The LLM is Not the Entire Architecture

**Status:** Accepted
**Context:** Standard AI agents wrap a single LLM with a loop and tool access. This fails in cybersecurity due to hallucinations, context loss, and safety risks.
**Decision:** We restrict the LLM purely to the "Reasoning" and "Language" nodes. Memory, planning, evaluation, and execution are handled by deterministic Python/system boundaries.
**Consequences:** Increased engineering complexity, but guarantees strict safety boundaries and deterministic control flow.
""",
    "docs/architecture/decisions/ADR-002-memory-separated.md": """# ADR-002: Separation of Memory and Context

**Status:** Accepted
**Context:** Injecting the entire conversation history into the prompt causes Context Saturation.
**Decision:** Implement a Context Manager. The LLM only sees the current state, active hypothesis, and summarized observations. History is moved to Episodic Memory.
**Consequences:** Massive token savings and prevention of context window collapse, requiring a robust retrieval mechanism.
""",
    "docs/architecture/decisions/ADR-005-capability-authority.md": """# ADR-005: Separation of Capability and Authority

**Status:** Accepted
**Context:** Security agents can cause catastrophic damage if they autonomously execute destructive commands.
**Decision:** The agent proposes *intent*. A hardcoded Policy Engine (Tool Gateway) checks *authority* (scope, destructive flags) before execution.
**Consequences:** The agent cannot bypass security rules via prompt injection, as rules are enforced outside the LLM.
""",
    "docs/architecture/decisions/ADR-006-token-efficiency.md": """# ADR-006: Token Efficiency as a Core Metric

**Status:** Accepted
**Context:** Long-running security tasks can easily burn hundreds of dollars in API costs if unoptimized.
**Decision:** We treat token efficiency as a first-class metric. The goal is maximizing useful security task performance per unit of compute.
**Consequences:** Forces parallel tool execution, minimal loops, and aggressive output compression.
"""
}

for path, content in docs.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

