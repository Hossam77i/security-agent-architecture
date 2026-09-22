#!/bin/bash
# recon.sh — canonical one-shot recon pipeline (hunt-productivity).
# Usage: recon.sh <domain> [--quick]   (authorized targets ONLY)
# Output: recon/<domain>_<ts>/{subs,urls,js,params,nuclei,report.md}
# Stages dedupe into files the next stage reads. Missing tools are skipped, not fatal.
set -u
TARGET="${1:?usage: recon.sh <domain> [--quick]}"
QUICK="${2:-}"
TS=$(date +%Y%m%d_%H%M%S)
OUT="recon/${TARGET}_${TS}"
mkdir -p "$OUT"/{subs,urls,js,params,nuclei}
log(){ echo "[*] $*"; }
have(){ command -v "$1" >/dev/null 2>&1; }
# Every external stage gets a hard timeout — a hung tool must never hang the pipeline.
# (verified 2026-09-14: subfinder with no timeout blocked the whole run in a restricted net)
T_SUBS=300; T_NET=180; T_SCAN=600
run(){ local t="$1"; shift; timeout "$t" "$@" 2>/dev/null; }

log "target=$TARGET out=$OUT"
# 1. passive subs
> "$OUT/subs/passive.txt"
have subfinder && run $T_SUBS subfinder -d "$TARGET" -all -recursive -silent -o "$OUT/subs/subfinder.txt"
ESCAPED_TARGET=$(echo "$TARGET" | sed 's/\./\\./g')
run $T_NET curl -s "https://crt.sh/?q=%25.$TARGET&output=json" 2>/dev/null | tr ',{}' '\n' | grep -oE "[a-zA-Z0-9_.-]+\.${ESCAPED_TARGET}" | sed 's/^\.//' | sort -u > "$OUT/subs/crtsh.txt" 2>/dev/null
cat "$OUT"/subs/*.txt 2>/dev/null | sort -u > "$OUT/subs/all_raw.txt"
log "passive subs: $(wc -l < "$OUT/subs/all_raw.txt")"
# 2. resolve
if have httpx; then
  httpx -l "$OUT/subs/all_raw.txt" -silent -o "$OUT/subs/resolved.txt" 2>/dev/null || cp "$OUT/subs/all_raw.txt" "$OUT/subs/resolved.txt"
else
  cp "$OUT/subs/all_raw.txt" "$OUT/subs/resolved.txt"
fi
# 3. probe live + tech
if have httpx; then
  run $T_NET httpx -l "$OUT/subs/resolved.txt" -ports 80,443,8080,8443,8000,8888 -title -status-code -tech-detect -follow-redirects -silent -o "$OUT/live_apps.txt"
  log "live: $(wc -l < "$OUT/live_apps.txt" 2>/dev/null)"
fi
# 4. urls + js (skip in --quick)
if [ -z "$QUICK" ]; then
  grep -oP 'https?://\S+' "$OUT/live_apps.txt" 2>/dev/null | sort -u > "$OUT/urls/live_urls.txt"
  have katana && run $T_NET katana -list "$OUT/urls/live_urls.txt" -silent -jc -o "$OUT/urls/katana.txt"
  cat "$OUT"/urls/*.txt 2>/dev/null | sort -u > "$OUT/urls/all.txt"
  log "urls: $(wc -l < "$OUT/urls/all.txt" 2>/dev/null)"
  grep -oP 'https?://\S+\.js(\?\S+)?' "$OUT/urls/all.txt" 2>/dev/null | sort -u > "$OUT/js/files.txt"
  log "js files: $(wc -l < "$OUT/js/files.txt" 2>/dev/null)"
  # 5. nuclei on live
  have nuclei && run $T_SCAN nuclei -l "$OUT/urls/live_urls.txt" -tags cve,misconfig,exposure,takeover -silent -o "$OUT/nuclei/findings.txt"
fi
# 6. report stub
{
  echo "# Recon $TARGET ($TS)"; echo
  echo "- subs raw: $(wc -l < "$OUT/subs/all_raw.txt")"
  echo "- live: $([ -f "$OUT/live_apps.txt" ] && wc -l < "$OUT/live_apps.txt" || echo 0)"
  echo "- urls: $([ -f "$OUT/urls/all.txt" ] && wc -l < "$OUT/urls/all.txt" || echo 0)"
  echo "- js: $([ -f "$OUT/js/files.txt" ] && wc -l < "$OUT/js/files.txt" || echo 0)"
  echo; echo "## Next (recon-driven, not checklist)"
  echo "- [ ] JS analysis: endpoints/secrets/params from js/files.txt"
  echo "- [ ] API docs: /swagger /openapi.json /graphql on live hosts"
  echo "- [ ] Param discovery on interesting endpoints"
  echo "- [ ] Diff vs last run for new assets"
} > "$OUT/report.md"
log "done -> $OUT/report.md"
