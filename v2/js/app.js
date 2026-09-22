
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
