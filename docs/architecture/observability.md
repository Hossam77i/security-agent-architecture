# Observability

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
