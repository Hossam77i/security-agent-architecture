import sys

with open('viewer.html', 'r') as f:
    html = f.read()

styles = """
        .problem-space { background: #1E1E1E; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #333; }
        .problem-category { cursor: pointer; background: #263238; padding: 15px; margin-bottom: 10px; border-radius: 4px; border-left: 4px solid #b39ddb; color: #FFF; font-weight: bold; }
        .problem-category:hover { background: #37474f; }
        .problem-details { display: none; padding: 10px 15px; background: #121212; margin-bottom: 15px; border-radius: 0 0 4px 4px; color: #ddd; }
        .problem-item { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #333; }
        .problem-item h4 { margin: 0 0 5px 0; color: #90caf9; }
        .status-badge { display: inline-block; padding: 2px 6px; font-size: 10px; border-radius: 4px; margin-left: 10px; font-weight: bold; }
        .status-current { background: #1b5e20; color: #a5d6a7; }
        .status-experimental { background: #f57f17; color: #fff59d; }
        .status-planned { background: #0d47a1; color: #90caf9; }
        .status-research { background: #4a148c; color: #ce93d8; }
"""

html = html.replace('</style>', styles + '\n    </style>')

interactive_html = """
    <h2>The Agent Problem Space</h2>
    <div class="problem-space">
        <p style="color: #aaa; font-size: 14px; margin-bottom: 20px;">An evolving taxonomy of 60+ documented engineering challenges encountered in long-running AI agents. Click a category to expand.</p>
        
        <div class="problem-category" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">A. Context & Memory</div>
        <div class="problem-details">
            <div class="problem-item">
                <h4>Context Window Saturation <span class="status-badge status-current">🟢 CURRENT</span></h4>
                <p><strong>Problem:</strong> Agent working memory fills with noisy logs.</p>
                <p><strong>Response:</strong> Observation parsing, compression. (Context Manager)</p>
            </div>
            <div class="problem-item">
                <h4>Context Contamination <span class="status-badge status-experimental">🟡 EXPERIMENTAL</span></h4>
                <p><strong>Problem:</strong> Irrelevant facts confuse the current task.</p>
                <p><strong>Response:</strong> Scope partitioning in episodic memory.</p>
            </div>
        </div>

        <div class="problem-category" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">B. Reasoning & Planning</div>
        <div class="problem-details">
            <div class="problem-item">
                <h4>Reasoning Restart <span class="status-badge status-research">🟣 RESEARCH</span></h4>
                <p><strong>Problem:</strong> Agent repeatedly discovers the same information across tasks.</p>
                <p><strong>Response:</strong> Extraction of reusable methodology. (Curriculum Engine)</p>
            </div>
            <div class="problem-item">
                <h4>Poor Task Decomposition <span class="status-badge status-current">🟢 CURRENT</span></h4>
                <p><strong>Problem:</strong> Agent tries to solve a massive task in one step.</p>
                <p><strong>Response:</strong> Hierarchical delegation. (Orchestrator & Planner)</p>
            </div>
        </div>

        <div class="problem-category" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">C. Tool Use & Execution</div>
        <div class="problem-details">
            <div class="problem-item">
                <h4>Tool Chaos <span class="status-badge status-current">🟢 CURRENT</span></h4>
                <p><strong>Problem:</strong> Using the wrong tool or random exploration.</p>
                <p><strong>Response:</strong> Just-in-time selection based on hypotheses. (Planning Layer)</p>
            </div>
            <div class="problem-item">
                <h4>Untrusted Output (Indirect Injection) <span class="status-badge status-current">🟢 CURRENT</span></h4>
                <p><strong>Problem:</strong> Attackers poison logs to hijack the agent.</p>
                <p><strong>Response:</strong> Sanitization and isolated parsing. (Tool Gateway)</p>
            </div>
        </div>
        
        <p style="color: #aaa; font-size: 12px; margin-top: 15px;"><em>View the full taxonomy in docs/research/agent-problems.md</em></p>
    </div>
"""

html = html.replace('<h2>1. Master System Architecture</h2>', interactive_html + '\n    <h2>1. Master System Architecture</h2>')

with open('viewer.html', 'w') as f:
    f.write(html)

