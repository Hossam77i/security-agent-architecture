with open("README.md", "r") as f:
    content = f.read()

# Make sure we don't duplicate logo and headers if they exist.
if "![RA SECURITY Agent Logo]" not in content:
    content = content.replace("![Horus Eye Security Agent Logo](ra_security_logo_pro.jpg)", "![RA SECURITY Agent Logo](ra_security_logo_pro.jpg)")

new_top = """![RA SECURITY Agent Logo](ra_security_logo_pro.jpg)

# RA SECURITY - Autonomous Agent Architecture
> An evolving architectural framework for long-running, autonomous cybersecurity agents.

## 🚀 Explore the Interactive V2 Architecture
**[Interactive V2 Website & Architecture Explorer](https://Hossam77i.github.io/security-agent-architecture/)**

---
"""

# Replace the top of the README if needed
import re
content = re.sub(r'^\!\[.*?\]\(.*?\)\s*# .*?\n.*?\n', '', content, flags=re.MULTILINE|re.IGNORECASE|re.DOTALL)
content = re.sub(r'^# RA SECURITY - Security Agent Architecture\n.*?\n', '', content, flags=re.MULTILINE|re.IGNORECASE)

# Insert the new top
content = new_top + content

with open("README.md", "w") as f:
    f.write(content)

