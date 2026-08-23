---
name: IB Conecta
description: Chapel door sign on limewash — enamel plates for the next service, brass for the visit.
colors:
  brass: "#947a57"
  brass-hover: "#7f6748"
  enamel: "#353b33"
  enamel-hover: "#2a2f28"
  oxblood: "#632f1a"
  limewash: "#d6ccb7"
  limewash-highlight: "#e8e0c9"
  cream: "#f8f4dc"
  wall-ink: "#1b1c12"
  muted: "#5c5648"
  success-wash: "#e4ecdf"
  error-wash: "#ead4c8"
typography:
  display:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "clamp(2.8rem, 13vw, 4.2rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "0.06em"
    fontFeature: "tabular-nums"
  headline:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "clamp(1.7rem, 4.5vw, 2.3rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "0.04em"
  title:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "1.15rem"
    fontWeight: 800
    lineHeight: 1.3
    letterSpacing: "0.06em"
  body:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  lede:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "1.05rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "0.82rem"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "0.04em"
  cta:
    fontFamily: 'Overpass, "Segoe UI", sans-serif'
    fontSize: "1rem"
    fontWeight: 800
    lineHeight: 1.5
    letterSpacing: "0.08em"
  mono:
    fontFamily: 'ui-monospace, "Cascadia Mono", Consolas, monospace'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  field: "0.35rem"
  message: "0.7rem"
  plate: "1.15rem"
  cta: "999px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "3rem"
components:
  button-primary:
    backgroundColor: "{colors.brass}"
    textColor: "{colors.oxblood}"
    typography: "{typography.cta}"
    rounded: "{rounded.cta}"
    padding: "0.85rem 2.1rem"
  button-primary-hover:
    backgroundColor: "{colors.brass-hover}"
    textColor: "{colors.oxblood}"
    rounded: "{rounded.cta}"
    padding: "0.85rem 2.1rem"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.enamel}"
    typography: "{typography.cta}"
    rounded: "{rounded.cta}"
    padding: "0.75rem 1.2rem"
  button-secondary-hover:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    rounded: "{rounded.cta}"
    padding: "0.75rem 1.2rem"
  panel:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    typography: "{typography.body}"
    rounded: "{rounded.plate}"
    padding: "1.5rem 1.35rem 1.35rem"
  door-plate:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    typography: "{typography.display}"
    rounded: "{rounded.plate}"
    padding: "2.15rem 1.5rem 1.7rem"
  input-text:
    backgroundColor: "{colors.limewash-highlight}"
    textColor: "{colors.wall-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "0.55rem 0.65rem"
    width: "100%"
  message-success:
    backgroundColor: "{colors.success-wash}"
    textColor: "{colors.wall-ink}"
    rounded: "{rounded.message}"
    padding: "0.7rem 0.9rem"
  message-error:
    backgroundColor: "{colors.error-wash}"
    textColor: "{colors.oxblood}"
    rounded: "{rounded.message}"
    padding: "0.7rem 0.9rem"
  pix-key:
    backgroundColor: "{colors.limewash-highlight}"
    textColor: "{colors.wall-ink}"
    typography: "{typography.mono}"
    rounded: "{rounded.field}"
    padding: "0.35rem 0.5rem"
  brand:
    textColor: "{colors.wall-ink}"
    typography: "{typography.title}"
  news-item:
    textColor: "{colors.wall-ink}"
    typography: "{typography.body}"
    padding: "0 0 1rem"
  skip-link:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    typography: "{typography.cta}"
    rounded: "{rounded.cta}"
    padding: "0.7rem 1.1rem"
  media-embed:
    width: "100%"
    rounded: "0.6rem"
---

# Design System: IB Conecta

## Overview

**Creative North Star: "Plaquinha da Porta"**

IB Conecta is a chapel door sign on limewash plaster. The next service is an enamel plate with cream caps and corner screws; Planeje sua visita is a brass plate with oxblood type. The page is a wall, not a cream letter and not a worship-hero church site.

The personality is wayfinding and pastoral: tracked Overpass caps, metals that look fastened, a phone-first column that stays light on a limited connection. Portuguese (`lang="pt-BR"`) is the interface language. Hours, address, WhatsApp, PIX, and the next-service line are CMS-owned; the visual system does not invent those facts. WhatsApp is a human channel, not a 24-hour desk. No video autoplays.

**Key Characteristics:**
- Limewash plaster field (tiled raster), not a cream paper canvas
- Enamel plates for facts; brass plates for the primary action
- Cream type on enamel; oxblood type on brass
- Self-hosted Overpass (400 / 700 / 800) as the only UI face
- Corner screws as signature fasteners
- Offset plate shadow; hover darkens the metal and does not lift it
- Pill CTAs; enamel plates at 1.15rem radius
- One 720px centered column

## Colors

Two metals on a plaster wall: brass for the next human step, enamel for facts, cream and oxblood as type on those metals.

### Primary
- **Brass** (`brass`): The visit plate. Fills the primary CTA, including the tiled brass grain and the two side screws. Selection highlight uses Brass behind Cream type.
- **Brass Hover** (`brass-hover`): Primary CTA hover only. A darker cut of the same brass; not a second brand hue.

### Secondary
- **Enamel** (`enamel`): The fact plate. Fills panels and the door plate, paints default links, the skip-link chip, and the `:focus-visible` ring. Secondary CTAs stroke this enamel.
- **Enamel Hover** (`enamel-hover`): Darker enamel reserved for enamel-fill hover when a control sits on enamel; secondary CTA hover fills Enamel with Cream type.

### Tertiary
- **Oxblood** (`oxblood`): Type on brass, caret color, form-error text, and primary-CTA focus ring. It is the voice of the brass plate, not a page accent wash.

### Neutral
- **Limewash** (`limewash`): Page ground. Body fill plus the repeating limewash raster (256px tile).
- **Limewash Highlight** (`limewash-highlight`): Field and PIX-key fill — a paler scrape of the same plaster, not white app chrome.
- **Cream** (`cream`): Caps on enamel (plate type, inner hairline, skip-link type). Cream is plate lettering, never the wall.
- **Wall Ink** (`wall-ink`): Type painted on the plaster — wordmark, nav, inner-page titles, footer, news titles, body.
- **Muted** (`muted`): Secondary copy on the wall (CMS ledes, news meta, helper lines). On enamel, mute by mixing Cream into Enamel (~72%), not by using this wall muted.
- **Success Wash** (`success-wash`): Confirmation flash fill, a green-gray plaster tint.
- **Error Wash** (`error-wash`): Error flash fill. Error flash type is Oxblood.

### Named Rules
**The Two Metals Rule.** Enamel holds facts. Brass holds the next human step. Do not invert them, and do not introduce a third metal or a leftover forest green.

**The Wall Field Rule.** The page is limewash plaster. Cream belongs on enamel plates; chalk-white belongs nowhere as a canvas.

## Typography

**Display Font:** Overpass, self-hosted (with Segoe UI, sans-serif)
**Body Font:** Overpass, self-hosted (with Segoe UI, sans-serif)
**Label/Mono Font:** ui-monospace, Cascadia Mono, Consolas, monospace — PIX keys and print song sheets only

**Character:** One wayfinding sans for the wordmark, the service time, nav, buttons, and reading. Overpass is loaded at 400, 700, and 800 (latin + latin-ext, `font-display: swap`). Caps, tracking, and weight do the hierarchy; a second display serif does not.

### Hierarchy
- **Display** (800, `clamp(2.8rem, 13vw, 4.2rem)`, line-height 1.15, tracking 0.06em, tabular nums, uppercase): Next-service time on the door plate (`h1` inside `.door-plate`). The largest type in the system; home only.
- **Headline** (800, `clamp(1.7rem, 4.5vw, 2.3rem)`, line-height 1.15, tracking 0.04em, uppercase): Inner-page titles (`h1`). Painted on the wall, not on a plate.
- **Title** (800, 1.15rem, line-height 1.3, tracking 0.06em, uppercase): Panel headings (`h2` / `h3` on enamel) and the header wordmark (tracking 0.12em on `.brand`).
- **Lede** (400, 1.05rem, Muted): Supporting sentence under an inner-page headline (`.cms-page .lede`). The home evangelistic line under the sign (`.home-lede`) stays wall-ink body, not a muted eyebrow.
- **Body** (400, 1rem, line-height 1.5): Default reading on the wall and on plates. Keep the measure inside the 720px column.
- **Label** (700, 0.82rem, tracking 0.04em, uppercase): Painted nav links. The door-plate host line is a tighter cut (0.72rem / 700 / 0.16em) and lives only on that plate.
- **CTA** (800, 1rem, tracking 0.08em, uppercase): Brass and enamel buttons, including the skip link.
- **Mono** (400, 1rem): PIX key and song-sheet `pre` bodies. Never for headlines or navigation.

### Named Rules
**The Wayfinding Caps Rule.** Overpass in tracked uppercase is the voice of the door. Headlines, nav, plates, and CTAs share that sans. Monospace is reserved for copy-once data (PIX keys) and print song sheets. Do not load a serif as the UI face.

## Layout

Shared shell CSS lives in `static/css/ib-conecta.css` (`{% static 'css/ib-conecta.css' %}` from `templates/base.html`). Tokens there are the implementation of this file’s frontmatter. Materials: tiled `limewash.png` on the body, `enamel.png` / `brass.png` on plates, `screw.svg` at fasteners.

Every screen that uses the shared shell lives in one centered column: `width: min(720px, calc(100% - 2rem))`, top padding 1.5rem, bottom padding 3rem. Header and footer add 1rem of vertical padding inside that column. There is no authored layout breakpoint and no hamburger — nav is a wrapping uppercase row with middots. The only fluid type is the display and headline clamps.

**Home** reorders the column with a four-row grid (`main`, `header`, `lede`, `footer`): enamel door plate and brass visit CTA first, painted nav under the plates, CMS evangelistic copy under the sign. The header wordmark is clipped on home; `IB Conecta` lives on the plate. The brass CTA is centered and at least `min(100%, 22rem)` wide.

**Inner screens** (visit, prayer, login, private modules) keep header then content: wall-painted headline, optional muted lede, then stacked enamel plates. Form fields are full width; field blocks space at 0.85rem. News lists divide items with a 1px cream-into-enamel rule. A 16/9 media host may sit above body copy at 1.2rem margin-bottom; it is a video hole, not a layout system.

Print sheets may flatten textures and shadows and hide chrome. That is operational paper, not a second public layout.

### Named Rules
**The Narrow Door Rule.** Public and private screens share one centered column (`min(720px, calc(100% - 2rem))`). Home stacks plate then nav; other screens keep header then plates. No multi-column app shell, no full-bleed hero, no hamburger.

## Elevation & Depth

Plates are fastened to the wall. Depth is a hard offset shadow plus corner (or side) screws, not stacked paper and not Material elevation. Hover darkens brass or enamel; it does not add lift or scale. The home door plate plays one settle: the plate shadow eases from a lighter rest to the full plate shadow (`0.65s` / `cubic-bezier(0.16, 1, 0.3, 1)`). Inner pages have no entrance choreography. `prefers-reduced-motion: reduce` cancels that animation.

### Shadow Vocabulary
- **Plate** (`box-shadow: 0 16px 32px rgba(27, 28, 18, 0.32)`): Enamel panels and the door plate. The shadow color is Wall Ink at 32%.
- **CTA** (`box-shadow: 0 10px 22px rgba(27, 28, 18, 0.28)`): Brass primary only. Secondary CTAs have no shadow.
- **Flash** (`box-shadow: 0 8px 18px rgba(27, 28, 18, 0.16)`): Success and error messages.

### Named Rules
**The Fastened Plate Rule.** Enamel and brass lift with their offset shadows and keep their screws. Hover changes the metal, not the elevation. Do not replace this with a 1px straw hairline or a flat card.

## Shapes

Enamel plates are rounded rectangles (1.15rem) with an 18px screw in each corner, 12px inset. The door plate adds an inset cream hairline (`16px` in, radius `calc(1.15rem - 10px)`). Brass CTAs are capsules (`999px`) with a 16px screw on each side, 12px from the ends. Secondary CTAs share the capsule but drop screws, grain, and shadow, and use a 2px enamel stroke.

Fields use a slight rounding (0.35rem). Flash messages round at 0.7rem. The media host rounds at 0.6rem and clips overflow. Decorative geometry on the door plate is two hairline rules with a 5px cream dot between them — plate furniture, not a bullet list style.

### Named Rules
**The Capsule-and-Plate Rule.** Primary actions are pills. Facts are 1.15rem enamel plates with corner screws. Do not square the plates to look like a letter, and do not round the wall-painted headline.

## Components

Metals on plaster: a brass capsule for the next step, an outlined enamel twin for sibling actions, enamel plates for facts, limewash-highlight fields, painted nav.

### Buttons
- **Shape:** Capsule (`999px`)
- **Primary:** Brass fill, brass grain tile, oxblood uppercase type, padding 0.85rem 2.1rem, CTA shadow, screws on both sides. No border on `button.cta`.
- **Secondary:** Transparent fill, 2px enamel stroke, enamel type, padding 0.75rem 1.2rem, no shadow, no screws.
- **Hover / Focus:** Primary hover fills Brass Hover; type stays Oxblood. Secondary hover fills Enamel with Cream type. No translate, no extra shadow. Primary `:focus-visible` uses an Oxblood outline; the shared ring is 2px Enamel with 3px offset.

### Cards / Containers
- **Corner Style:** Plate rounding (1.15rem)
- **Background:** Enamel fill plus enamel grain tile
- **Shadow Strategy:** Plate shadow — see Elevation
- **Border:** None on the plate edge; cream hairline only on the door plate’s inner inset
- **Internal Padding:** 1.5rem 1.35rem 1.35rem, 1rem vertical margin between plates
- **Type:** Cream. Links on a plate are Cream. Muted lines mix Cream into Enamel.

### Inputs / Fields
- **Style:** Full width, Limewash Highlight fill, 2px stroke mixed from Cream into Enamel, field rounding (0.35rem), padding 0.55rem 0.65rem, Overpass inherited. Text, email, number, date, datetime-local, password, textarea, and select share this recipe. Checkboxes stay auto-width. Labels are 700, 0.25rem above the field.
- **Focus:** Shared `:focus-visible` (2px Enamel, 3px offset). No glow.
- **Error:** Oxblood list text on the wall. On enamel, error lists lighten toward cream-rose (`#f0c9b8` in the build — a plate-on-enamel exception, not a palette token). Flash-level errors use Error Wash, not a field fill.

### Navigation
- **Style:** Wall-painted uppercase links in Wall Ink, 0.82rem / 700, no underline at rest, middot separators, wrapping row. Hover underlines. The wordmark is Wall Ink, 1.15rem / 800 / 0.12em tracking, no underline. Header and footer are not bars, not sticky, and not inverse. On home the wordmark is clipped; the plate carries the name.

### Door plate
Signature home component (`.panel.door-plate`). Centered enamel plate: `IB Conecta` (cream, 0.18em tracking), hairline-and-dot rules, institution line, huge next-service `h1`, address. CMS supplies the time and address. This anatomy is the home sign, not a kicker pattern for inner pages.

### News list
- Unstyled list. Wall-ink titles (700, no underline) and optional muted meta at 0.95rem. A 1px cream-into-enamel rule under each item. On enamel, titles and meta switch to cream / mixed cream. Used for news, convocations, playlists, and similar stacked records.

### Flash messages
- Unstyled list of notes. Default is Success Wash with Wall Ink. `.error` swaps to Error Wash with Oxblood. Padding 0.7rem 0.9rem, 0.7rem rounding, flash shadow. No icons.

### PIX key
- Limewash Highlight chip, field-like rounding, padding 0.35rem 0.5rem, ui-monospace stack, `user-select: all`. Copy-once data for the church PIX key — not a tag, not a button.

### Media embed
- Full-width 16/9 host with a near-black fill (`#1a1a1a` is the video hole, not a brand token) and 0.6rem rounding. Iframe fills the host. No autoplay in the product. Do not reuse that black as a surface or text color.

### Skip link
- Enamel capsule, cream uppercase type, hidden until focus. Focus outline is Cream.

## Do's and Don'ts

### Do:
- **Do** keep the page on the limewash wall (Limewash fill + tiled plaster raster).
- **Do** put facts on enamel plates with corner screws and Cream type; put the primary action on a brass capsule with Oxblood type.
- **Do** set `lang="pt-BR"` and keep interface type in Overpass.
- **Do** keep the shell at `min(720px, calc(100% - 2rem))`, with painted wrapping nav (no hamburger).
- **Do** take hours, address, next service, WhatsApp, and PIX from the CMS; keep pages light and never autoplay video.
- **Do** honor `prefers-reduced-motion` by dropping the home plate-settle animation.

### Don't:
- **Don't** treat cream paper, Source Serif, Palatino, or forest green as the current system — that letter-column world is retired.
- **Don't** use Cream or white as the page canvas; Cream is enamel lettering.
- **Don't** drop the corner screws on enamel plates or the side screws on the brass primary.
- **Don't** put a kicker or eyebrow above an inner-page headline; evangelistic copy sits under the home sign, as body on the wall.
- **Don't** lift or scale plates on hover; darken the metal instead.
- **Don't** autoplay video, promote the media-host black into the palette, or invent hours, PIX, WhatsApp, or testimonials.
- **Don't** promote A4 print margins or hide-chrome-on-print into the public layout.
