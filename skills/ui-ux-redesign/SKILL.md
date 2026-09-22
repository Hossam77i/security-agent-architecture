---
name: ui-ux-redesign
description: Eye-friendly dark dashboard redesign — calm contrast, readable typography, no flicker, accessible focus states. Use when a UI hurts the eyes or needs a professional ops-console look.
risk: low
source: community
date_added: '2026-09-10'
---

## Use this skill when

- User says design hurts eyes, too bright, too neon, hard to read
- Dark hacker/terminal theme with pure neon (#00ffcc/#0f0/#f00), glow text-shadow, scanlines, grid overlays
- Need calm professional ops-console restyle without breaking JS functionality

## Do not use this skill when

- Task is unrelated to UI/CSS readability
- User wants the harsh neon aesthetic preserved

## Instructions

- Preserve all element IDs, class names used by JS, and function names. Style-only changes unless asked.
- Apply the eye-comfort palette and typography below.
- Remove or neutralize motion that causes strain: scanline animations, blinking, heavy glow.
- Verify: file still parses, IDs intact, no inline neon left behind.

## Eye-comfort system

Palette (dark slate, muted accents):
- bg app: #0b1220, panels: #111c30 / #0f172a, borders: #22314d
- text primary: #dbe4f0, secondary: #94a3b8, muted: #64748b
- accent teal (muted): #2dd4bf, hover: #5eead4, text-on-accent: #06281f
- success: #34d399, warn: #fbbf24, danger: #fb7185, crisis: #facc15, info: #38bdf8
- Never use pure #0f0/#f00/#00ffcc on black. Never add text-shadow glow.

Typography:
- UI font: system stack (Inter, Segoe UI, Roboto, sans-serif). Mono ONLY for logs/coords/timestamps.
- Base 14-15px, line-height 1.55. Uppercase only for short labels with letter-spacing 0.08em.
- Max log/input font 0.85em minimum, no tiny dashed walls of text.

Motion & effects:
- No infinite full-screen animations (scanline, blink). Live dot may pulse gently at 2.4s, opacity 1->0.55.
- Grid overlay: remove or keep static at <=0.04 opacity. No box-shadow glow larger than 0 0 0 / subtle 0 4px 14px rgba(0,0,0,.4).
- Border-radius 8-10px on panels/buttons/inputs. Padding >=10px. Gap >=10px.

Accessibility:
- Focus-visible 2px outline accent on all inputs/buttons/links/list items.
- Contrast >=4.5:1 for body text. Muted text only for non-essential labels.
- Buttons: min-height 36px, disabled state with reduced opacity (not color-only).
- Scrollbars styled thin, thumb #22314d.

Map/Leaflet:
- Popups: dark slate bg #0f172a, light text, 8px radius, no glow.
- Markers: muted fills (#38bdf8 aviation, #fbbf24 energy, #fb7185 military, #facc15 crisis), white stroke 2px.
- Tactical rectangle: #2dd4bf dashed, image overlay opacity 0.85.

## Map tile performance (Leaflet zoom flood)

When zoom in/out spams the network tab with tile requests:

- `zoomSnap: 0` (continuous) reloads a full tile set per frame → use `0.5`,
  plus `wheelPxPerZoomLevel: 120` so one wheel flick = one level, not a burst.
- Tile layer: `updateWhenIdle: true, updateInterval: 250, keepBuffer: 1`
  (no mid-gesture fetching, fewer off-screen tiles), `detectRetina: false`
  (retina doubles payload on hidpi).
- Custom probe layers (e.g. fetch-then-inspect tile bytes): add a verdict
  cache `Map<z/x/y, 'origin'|blobURL>` with LRU cap (~600) and
  `URL.revokeObjectURL` on evict — cache hits must cost zero requests.
- In-flight dedup: same key requested twice shares one promise.
- Stale abort: `layer.on('tileunload')` → abort that tile's fetch, drop its
  queue entries, so fast zoom-out cancels bytes nobody will see.
- Throttle fallback hosts (e.g. max 4 concurrent OSM fetches) — public tile
  servers rate-limit.
- Debounce `resize` handlers (~150ms trailing); cache + throttle Nominatim
  (1 req/s policy) with sequence guards against out-of-order suggestions.

## Response Approach

1. Read the HTML file fully (style block + inline styles + JS-generated HTML/CSS).
2. Replace neon tokens, glow, scanline/grid animation with the system above.
3. Update JS-generated colors too (marker fills, popup HTML strings, dynamic button cssText).
4. Keep IDs: countrySelect, locationSearch, scanFilter, scanBtn, macroBtn, targetModal, modal-content, targetList-*, layer-*, logs, map.
5. Sanity check with grep for leftovers: `00ffcc`, `#0f0`, `#f00`, `text-shadow`, `scanline`, `blink`.
