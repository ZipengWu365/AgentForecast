# Unified Ecosystem Design System

This file defines the shared visual language for bright, scientific, agent-friendly open-source projects across the ecosystem.

## 1. Design rationale

- Use a white-first surface because scientific and technical users scan faster on bright, high-contrast layouts than on dark AI-brand tropes.
- Use sunlight yellow as the primary accent because it signals optimism, energy, and momentum without looking playful or juvenile.
- Use restrained blue as the technical accent because it carries scientific credibility, chart familiarity, and link/focus clarity.
- Keep the system calm and sparse so benchmark pages, docs, demos, and landing pages feel like one research product family instead of unrelated repos.

## 2. Design tokens

```yaml
color:
  bg: "#FFFFFF"
  bgSoft: "#FFFDF5"
  surface: "#FAFAFA"
  surfaceStrong: "#FFFFFF"
  card: "#FAFAFA"
  textPrimary: "#1F2937"
  textSecondary: "#6B7280"
  border: "#E5E7EB"
  borderStrong: "#D8DDE6"
  accentSun: "#FFC83D"
  accentSunSoft: "#FFF4C2"
  accentSunWarm: "#FFE27A"
  accentBlue: "#2F6BFF"
  accentBlueSoft: "#EEF4FF"
  success: "#1F8A5B"
  warning: "#AC6A00"

type:
  sans: "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, monospace"
  hero: "clamp(2.75rem, 5vw, 5rem)"
  h1: "clamp(2.2rem, 4vw, 4rem)"
  h2: "clamp(1.85rem, 3vw, 2.75rem)"
  h3: "1.2rem"
  body: "1rem"
  bodyLarge: "1.075rem"
  meta: "0.875rem"
  micro: "0.78rem"

space:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  5: "20px"
  6: "24px"
  7: "28px"
  8: "32px"
  10: "40px"
  12: "48px"
  16: "64px"
  20: "80px"

radius:
  sm: "12px"
  md: "16px"
  lg: "22px"
  xl: "28px"
  pill: "999px"

shadow:
  sm: "0 10px 30px rgba(31, 41, 55, 0.06)"
  md: "0 14px 40px rgba(31, 41, 55, 0.08)"
  lg: "0 18px 60px rgba(31, 41, 55, 0.10)"
```

## 3. Component specification

### Primary button

- Background: `linear-gradient(135deg, #FFC83D, #FFE27A)`
- Text: `#111827`
- Border: none
- Radius: pill
- Padding: `12px 18px`
- Hover: lift `-1px`, deepen shadow
- Use for: hero CTA, release CTA, "browse packs", "install now"

### Secondary button

- Background: `#FFFFFF`
- Text: `#1F2937`
- Border: `1px solid #E5E7EB`
- Radius: pill
- Padding: `12px 18px`
- Hover: slight border darkening and lift
- Use for: secondary navigation, feed/docs links, compare actions

### Tertiary text button

- Background: transparent
- Text: `#2F6BFF`
- Border: none
- Radius: `0`
- Padding: `0`
- Hover: underline
- Use for: inline links, docs jumps, ecosystem cross-links

### Cards

- Background: `#FAFAFA`
- Text: `#1F2937`
- Border: `1px solid #E5E7EB`
- Radius: `16px`
- Padding: `18px`
- Hover: border shifts warmer, shadow increases
- Use for: features, metrics, packs, artifacts

### Feature cards

- Same base as cards
- Add a small accent dot or warm header line
- Keep copy tight: headline + one paragraph
- Use 3-4 per row max

### Badges

- Neutral: white + gray border
- Accent: `#FFF4C2` background, warm border, brown text
- Technical: `#EEF4FF` background, blue text
- Radius: pill
- Padding: `6px 10px`
- Use for: selected backend, streaming, experimental, public beta

### Nav bar

- Background: translucent white with blur
- Border-bottom: soft gray
- Height: compact, not app-like
- Keep 3-5 links max

### Footer

- Background: white
- Border-top: none by default
- Use one card-like CTA strip instead of a dense link dump

### Section headings

- Eyebrow: uppercase, small, muted, warm dot
- H2: strong and wide with tight tracking
- Supporting copy: muted, max width `62ch`

### Code snippets

- Background: soft blue-white panel `#F8FBFF`
- Text: deep blue-gray
- Border: faint blue border
- Font: JetBrains Mono
- Radius: `16px`
- Padding: `16px 18px`

### Warning / info / success boxes

- Warning: pale warm background, amber text, warm border
- Info: pale blue background, blue text, blue border
- Success: pale green background, green text, green border
- Keep icon use minimal and optional

## 4. Landing page information architecture

### Hero

- Purpose: explain the repo in under 10 seconds
- Layout: left copy, right preview panel
- Hierarchy: eyebrow -> headline -> subhead -> CTA -> credibility pills
- Treatment: subtle white/yellow gradient, strong shadow, no clutter

### Trust strip / badges

- Purpose: reduce doubt immediately
- Layout: 3-4 small metric cards
- Hierarchy: label -> number/value -> short explanation
- Treatment: flat cards with very clean spacing

### Problem statement

- Purpose: say why this repo exists
- Layout: one large paragraph + two supporting bullets
- Treatment: simple white section with strong headline

### Key features

- Purpose: make differentiation obvious
- Layout: 2x2 or 4-up feature cards
- Treatment: neutral cards with one accent tag or line

### Architecture diagram section

- Purpose: show system shape quickly
- Layout: left text, right diagram or code-like block
- Treatment: white panel with soft blue code surface

### Example workflow

- Purpose: make usage feel easy
- Layout: 3-4 numbered cards
- Treatment: rhythmic, compact, high contrast

### Quickstart section

- Purpose: convert curiosity into action
- Layout: one code block + one output preview card
- Treatment: use sunlight accent only for CTA, not the code block

### Demo / screenshots

- Purpose: prove the repo does something real
- Layout: responsive card grid
- Treatment: preview image on top, stats below

### Ecosystem / related repos

- Purpose: create ecosystem gravity and cross-repo discovery
- Layout: 3-6 repo cards with clear roles
- Treatment: flatter and simpler than hero cards

### Final CTA

- Purpose: close the page with one next step
- Layout: single large CTA strip
- Treatment: premium white card with warm button

## 5. Style variants

### Variant A: Research Lab

- Density: low
- Tone: editorial, scientific, reflective
- Best for: research repos, representation learning, symbolic regression

### Variant B: Productized Open Source

- Density: medium
- Tone: sharper CTA hierarchy, stronger trust strip
- Best for: tools, agents, package landing pages

### Variant C: Benchmark / Dashboard

- Density: higher
- Tone: more tables, more cards, tighter spacing
- Best for: leaderboard pages, benchmark hubs, live galleries

## 6. Tailwind CSS theme proposal

See `website/tailwind.theme.ts` for a developer-ready theme extension object.

## 7. Example implementation

See `website/TSLabLanding.tsx` for a single-file React + Tailwind landing page implementation that follows this system.

## 8. README visual structure template

```md
# Repo Name

One-line value proposition in one sentence.

[badges]

## Why this exists

Short paragraph explaining the real problem.

## Quick example

```bash
pip install repo-name
repo-name demo
```

## What you get

- concise feature 1
- concise feature 2
- concise feature 3

## Installation

Base install first. Extras second.

## Quick start

Use one copy-paste command and one real output.

## Ecosystem

- related repo A
- related repo B
- related repo C

## Citation

BibTeX or `CITATION.cff` link.
```

## Strong recommendation

Do not let individual repos invent their own visual personality. Keep the ecosystem feeling like one bright research lab with multiple products, not multiple unrelated experiments.
