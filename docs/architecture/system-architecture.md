# System Architecture in Layers

The RA SECURITY architecture is organized into 10 interacting layers. This document explains the purpose, responsibilities, inputs, outputs, dependencies, failure modes, and security considerations for each layer.

## Layer 1 — Task / Interface
**Purpose:** Provides the entry point for the user to assign missions, set scope, and receive final reports.
**Responsibilities:** Translating user intent into a structured task definition and enforcing initial scope boundaries.
**Inputs:** Natural language requests, target URLs, IP ranges, authorization boundaries.
**Outputs:** Structured Task Object, constraints, and scope definition.
**Dependencies:** None.
**Failure modes:** Misinterpreted user intent, overly broad scope definitions.
**Security considerations:** Must enforce strict out-of-bounds checking before passing tasks to the orchestrator.

## Layer 2 — Orchestration
**Purpose:** The central coordinator that manages the lifecycle of the investigation.
**Responsibilities:** Routing tasks to specialized sub-agents, managing the core reasoning loop, and maintaining state.
**Inputs:** Structured Task Objects from Layer 1, updates from the Observation layer.
**Outputs:** State transitions, sub-agent invocations, and tool requests.
**Dependencies:** Layer 1, Layer 3 (Reasoning), Layer 5 (Memory).
**Failure modes:** Infinite loops, state corruption, dropping tasks.
**Security considerations:** Must run in an isolated environment to prevent orchestration hijacking.

## Layer 3 — Reasoning
**Purpose:** The core brain of the agent where logical deductions are made.
**Responsibilities:** Forming hypotheses based on observations and determining the best path forward.
**Inputs:** Context from Memory, current observations.
**Outputs:** Formulated hypotheses, confidence scores.
**Dependencies:** Layer 5 (Memory).
**Failure modes:** Hallucinations, incorrect logic, failure to recognize patterns.
**Security considerations:** Must be protected from prompt injection via untrusted observations.

## Layer 4 — Planning
**Purpose:** Translating reasoning and hypotheses into actionable steps.
**Responsibilities:** Selecting the right tools and ordering operations to validate hypotheses.
**Inputs:** Hypotheses from Layer 3.
**Outputs:** An execution graph or sequential plan of tool calls.
**Dependencies:** Layer 3 (Reasoning), Tool Registry.
**Failure modes:** Selecting inappropriate tools, planning invalid syntax.
**Security considerations:** The planner must not possess execution authority; it only requests actions.

## Layer 5 — Memory / Knowledge
**Purpose:** Managing both short-term context and long-term reusable knowledge.
**Responsibilities:** Filtering, compressing, and retrieving relevant information while adhering to token budgets.
**Inputs:** Observations, evaluation results, raw evidence.
**Outputs:** Context windows for the reasoning layer, reusable methodologies.
**Dependencies:** Vector databases, embedding models.
**Failure modes:** Context overflow, retrieval of irrelevant data, loss of critical facts.
**Security considerations:** Must securely isolate knowledge between different scopes and missions.

## Layer 6 — Tooling
**Purpose:** Defining the interface and capabilities available to the agent.
**Responsibilities:** Providing structured access to network tools, OSINT APIs, and scripts.
**Inputs:** Tool execution requests from the Execution Layer.
**Outputs:** Raw tool outputs.
**Dependencies:** Installed binaries (e.g., Nmap, Burp), API keys.
**Failure modes:** Missing dependencies, broken integrations.
**Security considerations:** Tools must be strictly sandboxed.

## Layer 7 — Execution
**Purpose:** Safely running the tools requested by the Planner.
**Responsibilities:** Enforcing policies, executing commands, and capturing outputs.
**Inputs:** Execution plans.
**Outputs:** Raw execution results (stdout/stderr, HTTP responses).
**Dependencies:** Layer 6 (Tooling).
**Failure modes:** Timeouts, tool crashes, environment failures.
**Security considerations:** This is the highest risk layer. Must run with least privilege and network isolation.

## Layer 8 — Observation
**Purpose:** Isolating, parsing, and formatting raw tool outputs.
**Responsibilities:** Converting chaotic raw data into structured evidence for the reasoning layer.
**Inputs:** Raw execution results.
**Outputs:** Parsed JSON, sanitized strings, structured observations.
**Dependencies:** Layer 7 (Execution).
**Failure modes:** Parsing errors, missing critical flags in noisy output.
**Security considerations:** Must sanitize outputs to prevent Cross-Site Scripting (XSS) or prompt injection attacks on the LLM.

## Layer 9 — Evaluation
**Purpose:** Assessing the success, failure, and efficiency of the agent's actions.
**Responsibilities:** Determining if a hypothesis was validated and evaluating token/context efficiency.
**Inputs:** Observations, initial hypotheses.
**Outputs:** Success/failure signals, efficiency metrics.
**Dependencies:** Layer 8 (Observation).
**Failure modes:** False positives, incorrect failure attribution.
**Security considerations:** Must remain objective and independent of the reasoning layer's biases.

## Layer 10 — Learning
**Purpose:** Turning raw experience into reusable knowledge.
**Responsibilities:** Analyzing failures and successes to extract methodologies and update the skill registry.
**Inputs:** Evaluation metrics, failure analysis.
**Outputs:** Updated knowledge base, new methodologies.
**Dependencies:** Layer 9 (Evaluation), Layer 5 (Memory).
**Failure modes:** Overfitting to specific scenarios, learning incorrect lessons.
**Security considerations:** Must not learn to bypass safety guardrails or policies.
