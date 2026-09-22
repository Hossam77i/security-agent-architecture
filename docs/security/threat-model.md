# Threat Model

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
