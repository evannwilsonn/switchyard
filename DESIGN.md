---
name: Switchyard
description: One small data platform drawn as a rail yard; three product tracks, five switch points, one main line into the app.
colors:
  rust: "#9c3d1c"
  rust-wash: "rgba(156,61,28,.10)"
  rail: "#6e4a36"
  ground: "#f1ebdf"
  sheet: "#faf6ee"
  ballast: "#ddd3c2"
  tie: "#b9ab95"
  rule: "#d6ccbb"
  rule-2: "#b5a991"
  ink: "#2b221c"
  ink-2: "#544638"
  ink-3: "#77685a"
  rust-dark: "#d4614a"
  rust-wash-dark: "rgba(212,97,74,.13)"
  rail-dark: "#a8968a"
  ground-dark: "#1d1916"
  sheet-dark: "#26211d"
  ballast-dark: "#352e28"
  tie-dark: "#544a40"
  rule-dark: "#3d352e"
  rule-2-dark: "#5a4f44"
  ink-dark: "#f2e9dc"
  ink-2-dark: "#cfc1ae"
  ink-3-dark: "#a8998a"
typography:
  display:
    fontFamily: "Big Shoulders Display, Public Sans, system-ui, sans-serif"
    fontSize: "clamp(30px, 4.4vw, 46px)"
    fontWeight: 900
    lineHeight: 0.9
    letterSpacing: "0.01em"
  headline:
    fontFamily: "Big Shoulders Display, Public Sans, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "0.01em"
  title:
    fontFamily: "Big Shoulders Display, Public Sans, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.02em"
  body:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 400
  data:
    fontFamily: "Space Mono, ui-monospace, Menlo, monospace"
    fontSize: "12.5px"
    fontWeight: 400
    lineHeight: 1.6
  data-strong:
    fontFamily: "Space Mono, ui-monospace, Menlo, monospace"
    fontSize: "13.5px"
    fontWeight: 700
rounded:
  none: "0px"
spacing:
  container: "1320px"
  gutter: "clamp(16px, 3vw, 36px)"
  panel: "16px"
  section: "46px"
components:
  button-open:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.none}"
    padding: "9px 14px"
  button-open-hover:
    backgroundColor: "{colors.rust}"
    textColor: "{colors.sheet}"
  button-theme:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.none}"
    padding: "4px 10px"
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    padding: "8px 14px 12px"
  tab-selected:
    textColor: "{colors.ink}"
  yard-panel:
    backgroundColor: "{colors.sheet}"
    rounded: "{rounded.none}"
  readout:
    backgroundColor: "{colors.ground}"
    padding: "12px 16px 14px"
  car:
    backgroundColor: "{colors.sheet}"
    rounded: "{rounded.none}"
    padding: "16px 18px 22px"
---

# Design System: Switchyard

## Overview

**Creative North Star: "The Drafted Rail Yard"**

Switchyard is a railroad track diagram on a cream drafting sheet. Every part of the page is a piece of a yard: the run is a set of product tracks laid on ballast beds with ties, the pipeline steps are switch points carrying signal lamps, history is a row of sidings, products are cars on a drawn rail. Data is drawn, not boxed; the status-card grid is refused.

The mood is warm, mechanical, and plain-spoken: dark umber ink, a ballast-grey bed, and rust reserved for the rails' working accent (selection, failure, the active tab, the primary hover). Corners are square everywhere. Depth comes from the drawing (bed under track, sill under car), not from shadows. Light and dark share one structure; the dark world is a warm umber night with a neutral-red rust.

**Key Characteristics:**
- Track diagram as the page's spine; on phones the yard turns vertical and tracks run down the screen.
- State is read by lamp shape, never by hue alone.
- Measured quantities become track: weight in the yard, length in the sidings.
- Three-voice type: condensed display for names, Public Sans for prose, Space Mono for every time, id and count.
- Square, hairline-ruled panels; no radius, no drop shadows.

## Colors

A warm, low-chroma drafting palette with one working accent: rust.

### Primary
- **Signal Rust** (rust; dark: rust-dark): selected-tab underline, selected lamp ring and its wash, failed lamp square, siding buffer stops, links, focus outline, and the hover fill of the "Open dashboard" button. In dark mode it shifts to a neutral red so it reads as rust, not orange.
- **Rail Umber** (rail; dark: rail-dark): every drawn rail: yard tracks, joining curves and main line, siding track, the rail under the cars, couplers, car sills, and the 3px rule under the top bar.

### Neutral
- **Drafting Cream** (ground): page ground, readout panel, top bar.
- **Sheet Cream** (sheet): raised paper for the yard, sidings, cars and "How a run works"; also the knockout inside lamps.
- **Ballast Grey** (ballast) and **Tie Grey** (tie): the track bed and its crossties. They exist only under track.
- **Hairline** (rule) and **Hairline Deep** (rule-2): panel borders, row dividers, dotted switch guides, dashed did-not-run track, the theme button border.
- **Umber Ink** (ink), **Ink 2** (ink-2), **Ink 3** (ink-3): text in three steps; ink also fills clean lamps and car wheels and backs the primary button.

### Named Rules
**The No Signal Colours Rule.** No blue, orange, green, plum or lime anywhere; these belong to the sibling portfolio worlds. Status is not encoded with a traffic-light palette.

**The Rust Is Work Rule.** Rust marks selection, failure and action only. It is never a decorative fill or a section colour.

## Typography

**Display Font:** Big Shoulders Display (700/800/900, fallback Public Sans)
**Body Font:** Public Sans (400–700, fallback system-ui)
**Label/Mono Font:** Space Mono (400/700, fallback ui-monospace)

**Character:** Condensed industrial lettering for names, as on yard signage, over a sober civic sans; a typewriter mono carries the log.

### Hierarchy
- **Display** (900, clamp 30–46px, 0.9): the wordmark "Switchyard" only.
- **Headline** (900, 28px, 1): section titles; car names at 26px.
- **Title** (800, 15–19px): track names (19px), switch names (15px), readout label and run-step names (17px).
- **Body** (400, 15px, 1.55; lede 16px): prose, held to 70–80ch.
- **Label** (400, 11–12px, Public Sans, ink-3): secondary lines under names (track kind, switch detail, tab sublabels).
- **Data** (Space Mono 400 11.5–13px; 700 for emphasis, 20px for the readout seconds): run ids, timestamps, seconds, counts, database names, log lines.

### Named Rules
**The Mono Means Measured Rule.** Every number or identifier that comes from the ops log is set in Space Mono; prose never is.

## Layout

Single column inside a 1320px container with a fluid gutter (clamp 16–36px). First viewport: top bar (wordmark left, tabs right, 3px rail beneath), masthead with lede left and mono run line right, then the full yard with the step readout attached directly beneath it (shared border, no gap) and a shape key. Sections follow at 46px intervals: sidings, cars, how a run works, footer.

Yard: product tracks run horizontally through five evenly spaced switch columns joined by dotted guides; the two outer tracks curve into one main line ending at "App". Below 700px yard width it redraws vertically: products become columns, switches become rows, and the main line drops to "App" at the bottom. Sidings are rows of id / three tracks / outcome; below 700px the tracks wrap to a full-width second row. Cars sit three across on one shared rail; below 980px they stack and couplers turn vertical. The five-step strip collapses to one column below 900px. The readout drops its detail to a full-width row below 640px.

## Elevation & Depth

Flat. No drop shadows. Depth is drawn: tracks sit on a ballast bed, panels are sheet on ground with a 1px hairline, cars stand on a rail on wheels. The only box-shadows are structural: the car's inset hairline plus a 6px rail-coloured underframe sill, and a 3px ground-coloured halo that seats each wheel on the rail.

### Named Rules
**The Drawn Depth Rule.** If something needs to read as raised, draw what it stands on; never lift it with a shadow.

## Shapes

Square corners throughout (0px); the only circles are lamps and wheels. Lamp shapes are the state vocabulary: filled ink disc ran clean; half-filled disc ran with warnings; rust square with a sheet-coloured X failed; dashed ink-3 ring did not run. A selected lamp gets a 2px rust ring over a rust wash; Clip Curator's extract lamp carries a dashed rust ring and the "saved AI" label. Track weight scales with the square root of a step's seconds (2–11px); did-not-run track is 2px dashed hairline. Siding track length is seconds on one shared scale; a failed run ends at a 6x16px rust buffer stop, a clean one at a rail-coloured end bar, and outliers beyond the 90th-percentile cap carry a double-slash break mark.

## Components

### Buttons
- **Shape:** square (0px).
- **Primary ("Open the … dashboard"):** ink fill, sheet text, Public Sans 700 14px, 9px 14px padding; sits at the foot of each car.
- **Hover / Focus:** fill turns rust; focus is the global 2px rust outline at 2px offset.
- **Ghost (theme switch):** transparent, ink-2 text, 1px rule-2 border, 4px 10px, 600 12px.

### Navigation
Text tabs with a sublabel (Public Sans 600 13.5px; sublabel 400 11.5px ink-3). Default ink-2, hover and selected ink; the selected tab carries a 4px rust underline inset to the text width, sitting on the bar's 3px rail rule. Below 560px sublabels hide and padding tightens; the row scrolls horizontally without a scrollbar.

### Yard Diagram (signature)
Sheet panel with hairline border holding the SVG yard. Lamps are focusable buttons; click, tap or arrow keys move across steps and tracks (axes swap in the vertical yard). Hover shows the rust wash.

### Step Readout
Ground-coloured strip attached under the yard: lamp glyph, display-face step label with a small sans status line, mono log detail (with an italic sans note where needed), and large mono seconds at the right.

### Sidings
Hairline-ruled list on sheet; each run row shows mono id and time, three ballast-bedded tracks on one time scale with mono captions, and an outcome word with mono duration.

### Product Car
Sheet panel, inset 1px hairline, 6px rail-coloured underframe sill, two ink wheels haloed in ground, rail-coloured couplers between neighbours, all standing on one 3px rail. Contents: display name, kind line, a definition list with mono values right-aligned, the primary button, and a repo link.

## Do's and Don'ts

### Do:
- **Do** encode step state by lamp shape (filled, half, crossed square, dashed ring) and keep the shape key visible beneath the yard.
- **Do** draw quantities as track: weight for seconds in the yard, length on a single shared scale in the sidings.
- **Do** keep failed runs in the sidings, ended by a rust buffer stop.
- **Do** set every logged number, id and time in Space Mono.
- **Do** keep track on ballast with ties; ballast and tie colours appear only under track.
- **Do** turn the yard vertical on narrow widths rather than shrinking it.

### Don't:
- **Don't** use blue, orange, green, plum or lime, or a traffic-light status palette.
- **Don't** carry status by hue alone.
- **Don't** round corners or add drop shadows; depth is drawn.
- **Don't** fall back to a grid of status cards for runs or steps.
- **Don't** use rust as decoration; it marks selection, failure and action.
