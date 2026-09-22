import os
import re

# Read original
with open('v2/index.html', 'r') as f:
    html = f.read()

# Extract the mermaid diagram blocks from the original HTML if needed, but I'll generate a fresh modern HTML.

new_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RA SECURITY - Architecture & Research</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
    <header class="hero">
        <div class="container">
            <h1>RA SECURITY</h1>
            <p class="tagline">An evolving architectural framework for long-running, autonomous cybersecurity agents.</p>
            <div class="links">
                <a href="https://github.com/Hossam77i/security-agent-architecture" class="btn">View on GitHub</a>
                <a href="#interactive-architecture" class="btn btn-outline">Explore Architecture</a>
            </div>
        </div>
    </header>

    <nav class="sticky-nav">
        <div class="container">
            <a href="#why">Why it Exists</a>
            <a href="#problem-space">Agent Problems</a>
            <a href="#principles">Design Principles</a>
            <a href="#interactive-architecture">Architecture</a>
            <a href="#evaluation">Evaluation</a>
            <a href="#docs">Documentation</a>
        </div>
    </nav>

    <main class="container">
        
        <section id="why">
            <h2>Why This Exists</h2>
            <p>General-purpose LLM agents are highly capable but fail in deep security workflows due to context collapse, reasoning fixation, and unsafe execution. <strong>RA SECURITY</strong> introduces strict architectural boundaries—separating reasoning, planning, memory, and execution—to solve these problems fundamentally.</p>
        </section>

        <section id="problem-space">
            <h2>Agent Problem Space</h2>
            <p class="desc">Interactive taxonomy of 60+ engineering challenges. Click categories to expand.</p>
            <div class="problems-grid" id="problem-cards">
                <!-- Populated by JS -->
            </div>
            <a href="../docs/research/agent-problems.md" class="read-more">Read Full Taxonomy →</a>
        </section>

        <section id="principles">
            <h2>Design Principles</h2>
            <ul class="principles-list">
                <li><strong>Capability ≠ Authority:</strong> The LLM proposes intent; policies dictate execution.</li>
                <li><strong>Experience → Knowledge:</strong> Memories are distilled, not just appended.</li>
                <li><strong>Token Efficiency:</strong> Compute is optimized; unnecessary loops are blocked.</li>
                <li><strong>Deterministic Safety:</strong> Security boundaries exist outside the LLM.</li>
            </ul>
        </section>

        <section id="interactive-architecture">
            <h2>Interactive Architecture Flow</h2>
            <p class="desc">Click any node to view its purpose, inputs, outputs, and security considerations.</p>
            
            <div class="arch-container">
                <div class="diagram-area">
                    <div class="mermaid">
flowchart TD
    %% Cognitive Flow
    classDef cognitive fill:#1a237e,stroke:#5c6bc0,stroke-width:2px,color:#fff;
    %% Control Flow
    classDef control fill:#b71c1c,stroke:#ef5350,stroke-width:2px,color:#fff;
    %% Learning Flow
    classDef learning fill:#1b5e20,stroke:#66bb6a,stroke-width:2px,color:#fff;
    
    USER[User / Task] --> ORCH[Orchestrator]
    
    subgraph Cognitive ["Cognitive Flow"]
        ORCH --> REASON[Reasoning Layer]
        REASON --> PLAN[Planning Layer]
        PLAN --> MEM[Memory / Knowledge]
        MEM -.-> REASON
    end
    
    subgraph Control ["Control Flow"]
        PLAN --> GATE[Tool Gateway / Policy]
        GATE --> EXEC[Execution Sandbox]
    end
    
    subgraph Learning ["Learning & Observation Flow"]
        EXEC --> OBS[Observation Layer]
        OBS --> EVAL[Evaluation Layer]
        EVAL --> LEARN[Learning Engine]
        LEARN -.-> MEM
        OBS -.-> REASON
    end

    class USER,ORCH,REASON,PLAN,MEM cognitive;
    class GATE,EXEC control;
    class OBS,EVAL,LEARN learning;
    
    click USER "javascript:showNodeData('user')"
    click ORCH "javascript:showNodeData('orch')"
    click REASON "javascript:showNodeData('reason')"
    click PLAN "javascript:showNodeData('plan')"
    click MEM "javascript:showNodeData('mem')"
    click GATE "javascript:showNodeData('gate')"
    click EXEC "javascript:showNodeData('exec')"
    click OBS "javascript:showNodeData('obs')"
    click EVAL "javascript:showNodeData('eval')"
    click LEARN "javascript:showNodeData('learn')"
                    </div>
                </div>
                <div class="info-panel" id="info-panel">
                    <h3>Select a node</h3>
                    <p>Click on any component in the diagram to explore its architectural details.</p>
                </div>
            </div>
        </section>

        <section id="evaluation">
            <h2>Evaluation & Efficiency</h2>
            <div class="grid-2">
                <div class="card">
                    <h3>Token Efficiency</h3>
                    <p>Token optimization is a first-class metric. By using the Context Manager, we drastically reduce <strong>Repeated Context Injection</strong> and enforce strict limits on tool loops.</p>
                </div>
                <div class="card">
                    <h3>Evaluation Methodology</h3>
                    <p>Independent State-Transition checks prevent <strong>False Success</strong>. Regression testing ensures prompt updates do not degrade the agent's baseline capabilities.</p>
                </div>
            </div>
        </section>

        <section id="docs">
            <h2>Documentation & Resources</h2>
            <div class="grid-3">
                <a href="https://github.com/Hossam77i/security-agent-architecture" class="doc-link">GitHub Repository</a>
                <a href="../docs/architecture/system-architecture.md" class="doc-link">System Architecture</a>
                <a href="../docs/research/agent-problems.md" class="doc-link">Agent Problems Taxonomy</a>
                <a href="../docs/research/problem-coverage.md" class="doc-link">Problem Coverage Matrix</a>
                <a href="../docs/security/threat-model.md" class="doc-link">Threat Model</a>
                <a href="../docs/architecture/decisions/ADR-001-llm-not-architecture.md" class="doc-link">Architecture Decisions (ADRs)</a>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>RA SECURITY - Autonomous Security Agent Architecture</p>
        </div>
    </footer>

    <script src="js/app.js"></script>
</body>
</html>
"""

css = """
:root {
    --bg: #0d1117;
    --card: #161b22;
    --text: #c9d1d9;
    --primary: #58a6ff;
    --border: #30363d;
    --success: #238636;
    --warning: #d29922;
    --danger: #da3633;
}
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.6; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.hero { text-align: center; padding: 80px 20px; background: linear-gradient(180deg, #1f2937 0%, var(--bg) 100%); border-bottom: 1px solid var(--border); }
.hero h1 { font-size: 3rem; margin: 0; color: #fff; letter-spacing: 2px; }
.hero .tagline { font-size: 1.2rem; color: #8b949e; margin: 20px 0; }
.btn { display: inline-block; padding: 10px 20px; background: var(--primary); color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; }
.btn-outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
.sticky-nav { position: sticky; top: 0; background: var(--card); border-bottom: 1px solid var(--border); padding: 15px 0; z-index: 100; display: flex; justify-content: center; gap: 20px; }
.sticky-nav a { color: var(--text); text-decoration: none; font-weight: 500; }
.sticky-nav a:hover { color: var(--primary); }
section { padding: 60px 0; border-bottom: 1px solid var(--border); }
h2 { color: #fff; font-size: 2rem; margin-bottom: 20px; }
.desc { color: #8b949e; margin-bottom: 30px; }

/* Problems Grid */
.problems-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
.problem-card { background: var(--card); border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.problem-header { padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: #21262d; font-weight: bold; }
.problem-header:hover { background: #30363d; }
.problem-body { padding: 15px; display: none; font-size: 0.9rem; }
.status-badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; font-weight: bold; }
.status-current { background: #2ea04333; color: #3fb950; border: 1px solid #2ea043; }
.status-experimental { background: #d2992233; color: #d29922; border: 1px solid #d29922; }

/* Interactive Architecture */
.arch-container { display: flex; gap: 30px; margin-top: 30px; }
.diagram-area { flex: 2; background: #fff; border-radius: 8px; padding: 20px; }
.info-panel { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; min-height: 400px; }
.info-panel h3 { color: var(--primary); margin-top: 0; }
.info-panel strong { color: #fff; }
.info-label { display: block; font-size: 0.8rem; color: #8b949e; text-transform: uppercase; margin-top: 15px; margin-bottom: 5px;}

/* Utils */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
.card { background: var(--card); border: 1px solid var(--border); padding: 20px; border-radius: 6px; }
.doc-link { display: block; padding: 15px; background: var(--card); border: 1px solid var(--border); text-decoration: none; color: var(--primary); border-radius: 6px; text-align: center; font-weight: bold; }
.doc-link:hover { background: #30363d; }
footer { text-align: center; padding: 40px 0; color: #8b949e; }

@media(max-width: 768px) {
    .arch-container { flex-direction: column; }
    .sticky-nav { display: none; }
}
"""

js = """
// Initialize Mermaid
mermaid.initialize({ startOnLoad: true, theme: 'default' });

// Problem Data
const problems = [
    { cat: "Context & Memory", items: [
        { name: "Context Saturation", status: "CURRENT", cls: "status-current", desc: "Agent working memory fills with noisy logs.", response: "Observation parsing, compression." },
        { name: "Context Contamination", status: "EXPERIMENTAL", cls: "status-experimental", desc: "Irrelevant facts confuse the current task.", response: "Scope partitioning." }
    ]},
    { cat: "Reasoning & Planning", items: [
        { name: "Poor Task Decomposition", status: "CURRENT", cls: "status-current", desc: "Agent tries to solve massive tasks in one step.", response: "Hierarchical delegation." },
        { name: "Hypothesis Fixation", status: "EXPERIMENTAL", cls: "status-experimental", desc: "Refusing to abandon failing attack paths.", response: "Independent Evaluation Engine forcing reassessment." }
    ]},
    { cat: "Security & Safety", items: [
        { name: "Indirect Prompt Injection", status: "CURRENT", cls: "status-current", desc: "Target poisons logs to hijack agent.", response: "Sanitization & Isolation." },
        { name: "Scope Confusion", status: "CURRENT", cls: "status-current", desc: "Agent attacks wrong domains.", response: "Preflight Boundary checks." }
    ]}
];

// Render Problems
const probContainer = document.getElementById('problem-cards');
problems.forEach(p => {
    let html = `<div class="problem-card">
        <div class="problem-header" onclick="toggleBody(this)">
            <span>${p.cat}</span>
            <span>+</span>
        </div>
        <div class="problem-body">`;
    p.items.forEach(i => {
        html += `<div style="margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <strong style="color:#58a6ff;">${i.name}</strong>
                <span class="status-badge ${i.cls}">${i.status}</span>
            </div>
            <p style="margin: 0 0 5px 0;"><strong>Problem:</strong> ${i.desc}</p>
            <p style="margin: 0;"><strong>Response:</strong> ${i.response}</p>
        </div>`;
    });
    html += `</div></div>`;
    probContainer.innerHTML += html;
});

function toggleBody(el) {
    const body = el.nextElementSibling;
    body.style.display = body.style.display === 'block' ? 'none' : 'block';
    el.children[1].innerText = body.style.display === 'block' ? '-' : '+';
}

// Architecture Node Data
const nodeData = {
    user: { title: "User / Task", purpose: "Defines the goal.", inputs: "User Prompt", outputs: "Task Object", status: "CURRENT" },
    orch: { title: "Orchestrator", purpose: "Manages task state, checkpoints, and recovery.", inputs: "Task", outputs: "Delegated Sub-tasks", status: "CURRENT" },
    reason: { title: "Reasoning Layer", purpose: "Generates hypotheses and logical next steps.", inputs: "Observation, Memory", outputs: "Proposed Action", status: "CURRENT" },
    plan: { title: "Planning Layer", purpose: "Selects tools based on hypothesis.", inputs: "Proposed Action", outputs: "Tool Request", status: "CURRENT" },
    mem: { title: "Memory / Knowledge", purpose: "Stores validated methodologies.", inputs: "Extracted Knowledge", outputs: "Context", status: "EXPERIMENTAL" },
    gate: { title: "Tool Gateway (Policy)", purpose: "Enforces security bounds (Capability vs Authority).", inputs: "Tool Request", outputs: "Authorized Command", status: "CURRENT" },
    exec: { title: "Execution Sandbox", purpose: "Runs untrusted code/tools safely.", inputs: "Command", outputs: "Raw Logs", status: "CURRENT" },
    obs: { title: "Observation Layer", purpose: "Parses and sanitizes raw logs into JSON.", inputs: "Raw Logs", outputs: "Clean Observation", status: "CURRENT" },
    eval: { title: "Evaluation Layer", purpose: "Independently checks if the task succeeded.", inputs: "Observation", outputs: "Success/Fail State", status: "PLANNED" },
    learn: { title: "Learning Engine", purpose: "Extracts failure/success lessons.", inputs: "Eval State", outputs: "New Methodology", status: "RESEARCH" }
};

window.showNodeData = function(id) {
    const data = nodeData[id];
    if(!data) return;
    
    document.getElementById('info-panel').innerHTML = `
        <h3>${data.title}</h3>
        <span class="info-label">Purpose</span>
        <p>${data.purpose}</p>
        <span class="info-label">Inputs & Outputs</span>
        <p><strong>In:</strong> ${data.inputs}<br><strong>Out:</strong> ${data.outputs}</p>
        <span class="info-label">Implementation Status</span>
        <span class="status-badge status-current">${data.status}</span>
    `;
};
"""

with open('v2/index.html', 'w') as f: f.write(new_html)
with open('v2/css/style.css', 'w') as f: f.write(css)
with open('v2/js/app.js', 'w') as f: f.write(js)

