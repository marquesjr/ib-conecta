# Surface: public home (shared shell)

Mode: Persuade on the home; Operate on login and the private area. One visual world for the whole shell.

## Job

A first-time visitor on a phone in Santa Leopoldina should see the next service, the address, and Planeje sua visita within one viewport, then reach WhatsApp or the visit page. Members use the same wall and plates for login and internal tools. Stay light: no hosted video autoplay, no heavy photography.

## Direction

Plaquinha da Porta (seed `757cf6f6`). The site is a painted chapel door sign on limewash plaster: enamel plate for facts, brass plate for the primary action, wayfinding caps, fasteners at the corners.

Approved composition: `.impeccable/mocks/comp-a-sign.png` (Placa na parede). Comp-led.

## First viewport (home)

Limewash field. Centered enamel plate: IB Conecta, institution name, next service time as the display, address. Brass plate below: Planeje sua visita. Wall-painted text nav under the plates (all destinations remain visible; no hamburger). Evangelistic CMS copy sits under the sign, not as an eyebrow.

## Do not literalize

- Photoreal rust, 3D bevels, or a photograph of a physical sign sitting on a table
- Worship stage photography or gold
- Invented hours, PIX, WhatsApp number, or testimonials — CMS/settings only
- Dropping the corner fasteners (signature geometry) or the two-plate stack (enamel then brass)

## Sampled from the approved comp (1024×1536)

| Role | Hex | How |
|---|---|---|
| Limewash ground | `#D6CCB7` | wall-corner patch average |
| Limewash highlight | `#E8E0C9` | max in wall patch |
| Enamel plate | `#353B33` | plate side interior |
| Cream plate type | `#F8F4DC` | high-luminance pixels on the plate |
| Brass CTA | `#947A57` | CTA plate average |
| Oxblood on brass | `#632F1A` | red-channel pixels on the CTA |
| Wall ink | `#1B1C12` | darkest footer type |

## Inventory

| Ingredient | Medium |
|---|---|
| Limewash wall | generated raster, tiled (`static/img/limewash.png`) |
| Enamel grain | generated raster overlay (`static/img/enamel.png`) |
| Brass grain | generated raster overlay (`static/img/brass.png`) |
| Corner screws | authored SVG (`static/img/screw.svg`) |
| Plate lift | CSS `box-shadow` with offset + blur |
| Wayfinding type | self-hosted Overpass (OFL) |
| Display time, wordmark, CTAs, nav, fields | semantic HTML/CSS |
| Next service / address / WhatsApp | Django/Wagtail settings |

## Motion

One moment: the enamel plate settles onto the wall (already visible; short ease-out on shadow). No entrance choreography on inner pages. Hover darkens enamel/brass; no lift.
