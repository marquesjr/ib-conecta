---
version: 1
slug: "templates-public-home-html"
primary_target: "templates/public/home.html"
related_targets: ["templates/base.html","static/css/ib-conecta.css","templates/accounts/login.html","templates/private_area/home.html","apps/public/models.py"]
---

# Surface: public shell and whole site (home, public pages, accounts, private area)

Mode: Persuade on the home; Operate on login and the private area; Read on news, agenda and sermons. One visual world for the whole site — the user scoped the redesign to everything, including the members' area.

## Job

A first-time visitor, usually on a phone in Santa Leopoldina or the surrounding countryside, must see the next service, the address and Planeje sua visita, and reach WhatsApp or the visit page. The church's own photographs are what prove it is alive this week, so they are the page's primary material rather than decoration. Members use the same paper, cells and plates for login and internal tools.

The lightness constraint recorded in PRODUCT.md principle 4 was explicitly overridden by the user for this redesign: a rich visual on every device, accepting a heavier page. The rural mobile visitor is still the primary audience; the page must stay legible and usable there, but is no longer capped on weight.

## Direction

Arquivo da Congregação (seed `e2d3e9a9`, safer register, re-roll round 1; the user pinned and then set this direction after declining the assigned Colcha da Colônia). The site is the church's own photographic archive: documentary photographs tiled as a contact sheet on archival paper, facts inset as inverted plates held by album corner mounts, hand-inked captions beneath every frame, hairline register crosses at the grid intersections, and one ink red as the single signal colour.

Craft bar, chosen by the agent at the user's delegation: Stripe (typographic precision, restrained colour used decisively), Instituto Moreira Salles (photography-led institutional calm), Life.Church (service time, location and next step resolved without clutter).

Approved composition: `.impeccable/mocks/comp-arquivo-b-folha.png` (Folha de Contato). Comp-led.

## First viewport (home)

Archival paper ground. A hairline row of small uppercase navigation across the top with the wordmark at its left end and a rule beneath; every destination visible, no hamburger. Below it the whole viewport is a contact-sheet cell grid, roughly six columns by three rows, gutters in paper shade, register crosses at the intersections. A solid white mount plate held by four album corner mounts occupies a two-by-two block at the upper left and is the brightest and most dominant element on the screen: label PRÓXIMO CULTO, the service time as the display, the address, the institution line. Directly beneath it the primary action fills exactly one cell as a solid ink red plate, and the WhatsApp action fills the neighbouring cell as a graphite plate. Two further cells invert from photograph to paper and hold dated Agenda and Sermões lists. The remaining cells are photographs, each filling its cell completely with a hand-inked caption beneath. A paper plate at the lower left carries the Instagram handle.

Density is a commitment, not a mood: the grid is roughly eighteen cells with twelve to fourteen photographic frames, and the field runs edge to edge with no empty outer margin. A grid rebuilt at a fraction of that density is a different design.

## Do not literalize

- Rounded corners, drop shadows, elevation or glass anywhere; depth is the gutter and the inversion of a cell
- A worship stage, coloured spotlights, backlit raised hands, or stock-slick smiling models
- Invented hours, PIX key, WhatsApp number, attendance figures or testimonials — CMS and settings only
- Dropping the album corner mounts, the register crosses, or the hand-inked captions (signature geometry)
- Letting the photographs become a decorative strip: they are the page's material, not a footer band
- Treating the graphite plates as a page ground; the page is light archival paper

## Sampled from the approved comp (1536×1024)

Sampled values supersede the palette chips authored before the comp existed; the chips called for a graphite page ground and the comp is light paper.

| Role | Hex | How |
|---|---|---|
| Archival paper ground | `#ECE8E2` | dominant quantized cluster, ~36% coverage |
| Paper shade (gutters, rules) | `#D4D0CA` | quantized cluster below the paper |
| Mount white (inverted plate) | `#F9F9F9` | plate interior patch average, clear of type |
| Graphite (dark plates) | `#222527` | WhatsApp plate interior patch average |
| Photo black (deepest ink) | `#111313` | dominant dark quantized cluster |
| Archival gray (secondary type, ticks) | `#74706C` | mid quantized cluster |
| Ink red (single signal, primary action) | `#8B211A` | action plate interior patch average |

## Component grammar

- Corners: square everywhere. No border radius on plates, cells, photographs, fields or buttons.
- Elevation: none. No box-shadow. A plate reads as laid on the sheet because the gutter separates it, not because it floats.
- Lines: 1px hairlines in paper shade; hairline register crosses at cell intersections; a rule under the nav row.
- Plates: solid flat fills flush to their cell boundary, type inset with generous margin. Inversion is the ranking device: a white plate outranks paper, paper outranks a photograph.
- Grid: the page is a cell grid and every region occupies whole cells. Nothing floats between cells.
- State: carried by inversion and by rule weight, never by hue alone, so the private area's schedule states stay legible without colour.

## Type ramp

| Role | Size | Treatment |
|---|---|---|
| Display (service time) | clamp 2.1rem–3.4rem | grotesque, medium, tabular figures |
| Address | 1.15rem | grotesque, medium |
| Institution line | 0.9rem | grotesque, regular, archival gray |
| Cell heading | 0.8rem | uppercase, tracked 0.12em |
| Label / nav | 0.68rem | uppercase, tracked 0.14em |
| Body / list row | 0.95rem | grotesque, regular; dates tabular |
| Inked caption | 0.8rem | script face, archival gray |

## Inventory

| Ingredient | Medium |
|---|---|
| Congregation and community photographs | raster — Instagram media stored locally; seeded synthetic rasters until the church's own feed is connected |
| Archival paper grain | generated raster tile (`static/img/paper.png`) |
| Album corner mounts | authored SVG (`static/img/corner.svg`) |
| Register crosses / crop ticks | authored SVG (`static/img/tick.svg`) |
| Contact-sheet grid, gutters, hairlines, plates | semantic HTML/CSS grid |
| Display time, wordmark, nav, actions, fields, lists | semantic HTML/CSS |
| Interface type | self-hosted Archivo (OFL), tabular figures enabled |
| Inked caption type | self-hosted Caveat (OFL) — font concession; the comp's fine pen hand is not legible at caption size |
| Next service / address / WhatsApp / PIX / handle | Django/Wagtail settings |
| Agenda, Sermões, Notícias rows | Wagtail pages |

Every photograph the site ships carries provenance: the generation prompt for a seeded synthetic raster, the Instagram permalink and fetch timestamp for real media.

## Motion

One moment, and it belongs to the archive: cells develop in. On first load the contact-sheet cells resolve from paper to image in reading order, a short staggered fade with no movement, as a print coming up in a tray. Nothing slides, nothing scales, nothing lifts. Hover deepens a photograph slightly and brings its caption from archival gray to graphite. `prefers-reduced-motion` ships the developed sheet with no stagger.

## Unresolved

- The church's Instagram must be converted to a Professional (Creator or Business) account before the official API can return media at all; until then the curated CMS gallery is the live source.
- No official logo file exists in the repository. The wordmark ships as letterspaced type; a real mark is on the user's replacement list.
- Real photography is not in the repository. Seeded frames are synthetic and labelled as such.
