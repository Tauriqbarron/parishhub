# ParishHub — Design Bible

**Version:** 2.0
**Last Updated:** 2026-04-12
**Primary Logo:** M1 — Shield Cathedral
**Status:** Active

---

## Table of Contents

1. [Brand Overview](#1-brand-overview)
2. [Logo System](#2-logo-system)
3. [Color System](#3-color-system)
4. [Typography](#4-typography)
5. [Spacing & Layout](#5-spacing--layout)
6. [Components](#6-components)
7. [Dark Mode](#7-dark-mode)
8. [Iconography](#8-iconography)
9. [Motion & Animation](#9-motion--animation)
10. [Accessibility](#10-accessibility)
11. [Implementation](#11-implementation)
12. [Brand Rules](#12-brand-rules)

---

## 1. Brand Overview

### What is ParishHub?

ParishHub is a parish management platform for Catholic communities. It handles member records, sacraments, household data, and community events — the sacred operational backbone of a parish.

### Brand Pillars

| Pillar | Meaning |
|--------|---------|
| **Trustworthy** | Handles sacred community data with reverence and care |
| **Accessible** | WCAG AAA compliant — works for every parishioner and staff member |
| **Warm** | Approachable and human, not clinical or cold |
| **Professional** | Enterprise-grade reliability meets parish simplicity |

### Brand Voice

- Clear, not clever
- Warm, not casual
- Reverent, not stiff
- Helpful, not preachy

### Tagline

**"Parish Records · Perfected"**

Use sparingly. Appears under the logo in full brand lockups and on marketing materials. Never use in UI copy.

---

## 2. Logo System

### Primary Logo: M1 Shield Cathedral

The ParishHub logo is a shield containing a cross above a house/church silhouette. The cross represents faith and the sacred nature of parish work. The house represents community, home, and the parish itself. The shield represents protection and trust — we guard what matters.

#### SVG (Primary Mark)

```svg
<svg viewBox="0 0 200 200" width="200" height="200">
  <path d="M100,22 L166,54 L166,118 Q166,168 100,186 Q34,168 34,118 L34,54 Z" fill="none" stroke="#0F172A" stroke-width="5"/>
  <rect x="96" y="44" width="8" height="52" rx="1" fill="#D97706"/>
  <rect x="80" y="58" width="40" height="8" rx="1" fill="#D97706"/>
  <path d="M80,156 L80,130 L100,114 L120,130 L120,156 Z" fill="none" stroke="#0F172A" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="100" y1="112" x2="100" y2="104" stroke="#D97706" stroke-width="2"/>
  <line x1="96" y1="108" x2="104" y2="108" stroke="#D97706" stroke-width="2"/>
  <rect x="96" y="144" width="8" height="12" rx="4" fill="none" stroke="#0F172A" stroke-width="1.5"/>
</svg>
```

### Logo Anatomy

```
    ┌─────────────┐
    │  ╔═══════╗  │  ← Shield outline (Navy #0F172A, 5px stroke)
    │  ║   ┃   ║  │  ← Cross (Amber #D97706, filled)
    │  ║ ━━╋━━ ║  │
    │  ║       ║  │
    │  ║  ╱  ╲ ║  │  ← Roof (Navy, 2.5px stroke)
    │  ║ ╱    ╲║  │
    │  ║╱  []  ╲│  │  ← Arched door (Navy outline)
    │  ╚═══════╝  │
    └─────────────┘
```

### Logo Variants

| Variant | Use Case | Background |
|---------|----------|------------|
| **Light (Primary)** | Default — web, print, light surfaces | White or light neutral |
| **Dark** | Dark mode, navy backgrounds | Navy #0F172A or #1E293B |
| **Monochrome Navy** | Print (single color), watermarks | Any |
| **Monochrome White** | Reversed on photography, dark overlays | Dark or photographic |
| **Favicon (32px)** | Browser tab | Browser chrome |
| **App Icon (512px)** | PWA, mobile home screen | Rounded rect background |

### Light Variant (Default)

```svg
<!-- Shield: Navy outline. Cross: Amber filled. House: Navy outline. Chimney cross: Amber. Door: Navy outline. -->
<path d="M100,22 L166,54 L166,118 Q166,168 100,186 Q34,168 34,118 L34,54 Z" fill="none" stroke="#0F172A" stroke-width="5"/>
<rect x="96" y="44" width="8" height="52" rx="1" fill="#D97706"/>
<rect x="80" y="58" width="40" height="8" rx="1" fill="#D97706"/>
<path d="M80,156 L80,130 L100,114 L120,130 L120,156 Z" fill="none" stroke="#0F172A" stroke-width="2.5" stroke-linejoin="round"/>
<line x1="100" y1="112" x2="100" y2="104" stroke="#D97706" stroke-width="2"/>
<line x1="96" y1="108" x2="104" y2="108" stroke="#D97706" stroke-width="2"/>
<rect x="96" y="144" width="8" height="12" rx="4" fill="none" stroke="#0F172A" stroke-width="1.5"/>
```

### Dark Variant

```svg
<!-- Shield: White outline. Cross: Amber filled. House: White outline. Chimney cross: Amber. Door: White outline. -->
<path d="M100,22 L166,54 L166,118 Q166,168 100,186 Q34,168 34,118 L34,54 Z" fill="none" stroke="#f8fafc" stroke-width="5"/>
<!-- (cross and chimney cross stay Amber #D97706) -->
<!-- (house stroke changes to #f8fafc) -->
```

### Favicon (32px)

```svg
<svg viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="4" fill="#f8fafc"/>
  <path d="M16,4 L27,9 L27,20 Q27,27 16,30 Q5,27 5,20 L5,9 Z" fill="none" stroke="#0F172A" stroke-width="2"/>
  <rect x="14.5" y="7" width="3" height="8" rx="0.5" fill="#D97706"/>
  <rect x="12" y="9.5" width="8" height="2" rx="0.5" fill="#D97706"/>
  <path d="M11,25 L11,21 L16,17 L21,21 L21,25 Z" fill="none" stroke="#0F172A" stroke-width="1.5" stroke-linejoin="round"/>
</svg>
```

### App Icon (512px)

```svg
<svg viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" rx="96" fill="#0F172A"/>
  <path d="M256,60 L420,130 L420,340 Q420,452 256,484 Q92,452 92,340 L92,130 Z" fill="none" stroke="#f8fafc" stroke-width="16"/>
  <rect x="244" y="140" width="24" height="100" rx="3" fill="#D97706"/>
  <rect x="210" y="168" width="92" height="16" rx="3" fill="#D97706"/>
  <path d="M190,380 L190,330 L256,288 L322,330 L322,380 Z" fill="none" stroke="#f8fafc" stroke-width="10" stroke-linejoin="round"/>
  <line x1="256" y1="284" x2="256" y2="268" stroke="#D97706" stroke-width="6"/>
  <line x1="248" y1="276" x2="264" y2="268" stroke="#D97706" stroke-width="6"/>
  <rect x="248" y="356" width="16" height="24" rx="8" fill="none" stroke="#f8fafc" stroke-width="6"/>
</svg>
```

### Logo Clear Space

Minimum clear space around the logo equals the height of the cross element (approximately 52 units in the 200-unit viewBox). No text, graphics, or other visual elements may enter this zone.

```
    ┌──────────────────┐
    │                  │
    │   clear space    │
    │  ┌────────────┐  │
    │  │   LOGO     │  │
    │  └────────────┘  │
    │                  │
    └──────────────────┘
```

### Minimum Size

| Context | Minimum Width |
|---------|---------------|
| Digital | 24px |
| Print | 12mm |
| Favicon | 16px (use simplified version) |

### Logo Don'ts

- Do NOT rotate the logo
- Do NOT change the colors (amber cross + navy shield is fixed)
- Do NOT add drop shadows, gradients, or effects
- Do NOT stretch or distort
- Do NOT place on busy photographic backgrounds without a solid backing panel
- Do NOT separate the cross from the shield — they are one unit
- Do NOT animate the logo without brand team approval

### Wordmark Lockup

The logo appears to the left of the wordmark "ParishHub" in Inter Bold. The tagline "Parish Records · Perfected" appears below in Inter Medium, amber color, uppercase, tracked out.

```
  [SHIELD]  ParishHub
            PARISH RECORDS · PERFECTED
```

- Icon to text gap: 16px
- Wordmark to tagline gap: 4px
- Tagline: 12px, medium weight, uppercase, 2px letter-spacing, amber #D97706

---

## 3. Color System

### Design Philosophy

The ParishHub palette is built on two anchoring colors — Navy and Amber — chosen to convey trust and warmth. Navy says "we are serious about your data." Amber says "we are human, and we care."

Light theme is the default. Dark theme is an equal citizen, not an afterthought.

### Primary Palette

| Role | Name | Hex | RGB | Usage |
|------|------|-----|-----|-------|
| **Primary** | Navy | `#0F172A` | 15, 23, 42 | Headers, nav, primary buttons, logo outlines |
| **Primary Light** | Navy 600 | `#1E293B` | 30, 41, 59 | Hover states, secondary panels, dark surfaces |
| **Primary Muted** | Navy 400 | `#475569` | 71, 85, 105 | Body text on light backgrounds |
| **Accent** | Amber | `#D97706` | 217, 119, 6 | CTAs, highlights, active states, logo cross |
| **Accent Light** | Amber 300 | `#FBBF24` | 251, 191, 36 | Hover on accent, soft highlights |
| **Accent Muted** | Amber 50 | `#FFFBEB` | 255, 251, 235 | Accent background tints |

### Neutral Palette

| Role | Name | Hex | CSS Variable |
|------|------|-----|-------------|
| Background | White | `#FFFFFF` | `--color-bg` |
| Background Subtle | Slate 50 | `#F8FAFC` | `--color-bg-subtle` |
| Background Muted | Slate 100 | `#F1F5F9` | `--color-bg-muted` |
| Border | Slate 200 | `#E2E8F0` | `--color-border` |
| Border Strong | Slate 300 | `#CBD5E1` | `--color-border-strong` |
| Text Primary | Navy | `#0F172A` | `--color-text` |
| Text Secondary | Slate 500 | `#475569` | `--color-text-secondary` |
| Text Muted | Slate 400 | `#94A3B8` | `--color-text-muted` |

### Semantic Colors

| Role | Hex | Usage |
|------|-----|-------|
| Success | `#059669` | Confirmations, active records |
| Success BG | `#ECFDF5` | Success message backgrounds |
| Error | `#DC2626` | Validation errors, destructive actions |
| Error BG | `#FEF2F2` | Error message backgrounds |
| Warning | `#D97706` | Warnings (uses accent) |
| Warning BG | `#FFFBEB` | Warning backgrounds (uses accent-muted) |
| Info | `#2563EB` | Informational notices |
| Info BG | `#EFF6FF` | Info message backgrounds |

### Contrast Ratios (WCAG AAA)

| Combination | Ratio | Grade | Notes |
|-------------|-------|-------|-------|
| Navy on White | 16.75:1 | AAA | Primary text — always safe |
| White on Navy | 16.75:1 | AAA | Dark-on-light reversed |
| Navy 400 on White | 7.45:1 | AAA | Secondary text |
| Amber on Navy | 5.47:1 | AA | Use for headings/buttons on dark |
| Amber 300 on Navy | 10.2:1 | AAA | Light amber on dark backgrounds |
| Amber on White | 3.06:1 | AA Large | **Large text only (24px+)** — never body text |

### Color Usage Rules

1. **Never** use amber (#D97706) as body text on white backgrounds — it fails contrast for small text
2. Amber on white is allowed for: large headings (24px+), buttons (white text on amber bg), decorative accents
3. Amber on navy is the primary accent-on-dark pairing
4. Primary text is always Navy on light, White on dark — never amber for text body
5. Semantic colors (success, error, info) are fixed and never swapped

---

## 4. Typography

### Font Family

**Primary:** Inter
**Fallback:** -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

Inter was chosen for its excellent legibility at small sizes (critical for data-heavy parish records), clean geometric forms, and professional but warm character.

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Type Scale

| Level | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Display | 48px / 3rem | 700 | 1.1 | -0.02em | Hero headings, landing pages |
| H1 | 36px / 2.25rem | 700 | 1.2 | -0.01em | Page titles |
| H2 | 30px / 1.875rem | 600 | 1.3 | -0.01em | Section headings |
| H3 | 24px / 1.5rem | 600 | 1.4 | 0 | Subsection headings |
| H4 | 20px / 1.25rem | 600 | 1.4 | 0 | Card titles, fieldset legends |
| Body Large | 18px / 1.125rem | 400 | 1.6 | 0 | Intro paragraphs |
| Body | 16px / 1rem | 400 | 1.6 | 0 | Default body text |
| Body Small | 14px / 0.875rem | 400 | 1.5 | 0.01em | Secondary text, captions |
| Caption | 12px / 0.75rem | 500 | 1.4 | 0.02em | Labels, badges, metadata |
| Overline | 11px / 0.6875rem | 600 | 1.4 | 0.08em | Section labels, table headers |

### Typography Rules

1. Body text is always 16px on desktop. Never smaller for reading content.
2. Line height is never below 1.4 for body text.
3. Maximum line width: 72 characters for comfortable reading.
4. Use weight, not color, to create hierarchy when possible.
5. Never use amber text on white for body copy.

---

## 5. Spacing & Layout

### Spacing Scale (4px base)

All spacing uses a 4px base unit. This creates a consistent vertical and horizontal rhythm across the entire application.

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight inner padding, icon-text gap |
| `space-2` | 8px | Small padding, between related items |
| `space-3` | 12px | Form field internal padding |
| `space-4` | 16px | Default component padding |
| `space-5` | 20px | Card padding |
| `space-6` | 24px | Section internal padding |
| `space-8` | 32px | Between sections |
| `space-10` | 40px | Major section spacing |
| `space-12` | 48px | Section dividers |
| `space-16` | 64px | Page margins (desktop) |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-none` | 0 | Sharp edges (tables) |
| `rounded-sm` | 4px | Badges, tight elements |
| `rounded` | 6px | Inputs, buttons |
| `rounded-md` | 8px | Cards, modals, panels |
| `rounded-lg` | 12px | Large containers |
| `rounded-xl` | 16px | Feature panels, hero sections |
| `rounded-full` | 9999px | Avatars, pills, toggle switches |

### Breakpoints

| Name | Width | Target |
|------|-------|--------|
| `sm` | 375px | Mobile |
| `md` | 768px | Tablet |
| `lg` | 1024px | Small desktop |
| `xl` | 1440px | Desktop |
| `2xl` | 1920px | Large desktop |

### Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-base` | 0 | Default |
| `z-dropdown` | 10 | Dropdowns, popovers |
| `z-sticky` | 20 | Sticky headers, navbars |
| `z-overlay` | 30 | Modal backdrops |
| `z-modal` | 40 | Modal dialogs |
| `z-toast` | 50 | Toast notifications |

Rule: Never use arbitrary z-index values. Always use this scale.

---

## 6. Components

### Buttons

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| Primary | Navy `#0F172A` | White | None | Navy 600 `#1E293B` |
| Accent | Amber `#D97706` | White | None | `#B45309` |
| Outline | Transparent | Navy | 1px `#E2E8F0` | Background `#F8FAFC` |
| Ghost | Transparent | Navy | None | Background `#F1F5F9` |
| Destructive | Red `#DC2626` | White | None | `#B91C1C` |

Sizing:
- Small: 32px height, 13px text, 12px horizontal padding
- Default: 40px height, 14px text, 20px horizontal padding
- Large: 48px height, 16px text, 24px horizontal padding
- Minimum touch target: 44x44px

All buttons require:
- `cursor-pointer`
- 200ms transition on color/background
- Focus ring: 2px solid `#D97706` with 2px offset
- `font-weight: 500`

### Form Inputs

| Element | Style |
|---------|-------|
| Label | 14px, font-weight 500, Navy text |
| Input | 1px `#E2E8F0` border, 6px radius, 10px/12px padding |
| Focus | Border `#D97706`, ring `rgba(217,119,6,0.2)` 2px |
| Error | Border `#DC2626`, background `#FEF2F2` |
| Hint | 12px, `#94A3B8` text |
| Error message | 12px, `#DC2626` text |

### Cards

- Background: White
- Border: 1px solid `#E2E8F0`
- Border radius: 8px
- Padding: 20px
- Hover: box-shadow with 200ms transition

### Badges

| State | Background | Text |
|-------|-----------|------|
| Active / Success | `#ECFDF5` | `#059669` |
| Inactive / Muted | `#F1F5F9` | `#475569` |
| Pending / Accent | `#FFFBEB` | `#D97706` |
| Error | `#FEF2F2` | `#DC2626` |

All badges: 12px text, 500 weight, pill shape (9999px radius), 2px/10px padding.

### Alerts

| Type | Background | Border | Text | Icon |
|------|-----------|--------|------|------|
| Success | `#ECFDF5` | `#059669` 20% opacity | `#059669` | Checkmark circle |
| Error | `#FEF2F2` | `#DC2626` 20% opacity | `#DC2626` | X circle |
| Warning | `#FFFBEB` | `#D97706` 20% opacity | `#D97706` | Exclamation triangle |
| Info | `#EFF6FF` | `#2563EB` 20% opacity | `#2563EB` | Info circle |

Always use `role="alert"` for accessibility. Always include an SVG icon (never emojis).

### Tables

- Header: background `#F8FAFC`, 11px uppercase caption text, `#94A3B8` color
- Rows: divide with `#E2E8F0`, hover background `#F8FAFC`
- Cell padding: 12px vertical, 16px horizontal
- Text: 14px

### Navigation

- Background: `#0F172A` (Navy)
- Height: 56px
- Brand text: White, 18px, bold
- Links: `#CBD5E1`, 14px
- Link hover: White with 150ms transition
- Active link: White with 2px amber bottom border

---

## 7. Dark Mode

Dark mode is not a color inversion — it is a carefully tuned alternate palette that maintains the same visual hierarchy and brand identity.

### Dark Mode Palette

| Role | Light | Dark |
|------|-------|------|
| Background | `#FFFFFF` | `#0F172A` |
| Background Subtle | `#F8FAFC` | `#1E293B` |
| Background Muted | `#F1F5F9` | `#334155` |
| Border | `#E2E8F0` | `#334155` |
| Border Strong | `#CBD5E1` | `#475569` |
| Text Primary | `#0F172A` | `#F8FAFC` |
| Text Secondary | `#475569` | `#CBD5E1` |
| Text Muted | `#94A3B8` | `#94A3B8` |
| Accent | `#D97706` | `#FBBF24` |

### Dark Mode Rules

1. The logo switches to its dark variant (white outlines, amber cross stays amber)
2. Accent color lightens from `#D97706` to `#FBBF24` for better contrast on dark surfaces
3. Text muted stays the same (`#94A3B8`) — it works on both backgrounds
4. Semantic colors (success, error, info, warning) do not change
5. Borders use `#334155` instead of `#E2E8F0`

### CSS Implementation

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0F172A;
    --color-bg-subtle: #1E293B;
    --color-bg-muted: #334155;
    --color-border: #334155;
    --color-border-strong: #475569;
    --color-text: #F8FAFC;
    --color-text-secondary: #CBD5E1;
    --color-text-muted: #94A3B8;
    --color-accent: #FBBF24;
  }
}
```

---

## 8. Iconography

### Library

**Primary:** Lucide
**Fallback:** Heroicons

### Style

- Outline style, 1.5px stroke
- Round line cap and join
- No filled icons except for specific state indicators

### Sizes

| Token | Size | Usage |
|-------|------|-------|
| `icon-xs` | 12px | Inline with small text |
| `icon-sm` | 16px | Inline with body text |
| `icon-md` | 20px | Default — buttons, list items |
| `icon-lg` | 24px | Section headers, feature callouts |
| `icon-xl` | 32px | Feature highlights, empty states |
| `icon-2xl` | 48px | Hero illustrations |

### Rules

- Never use emojis as icons — always SVG
- Icons inherit text color by default
- Amber icons only for active/selected states or decorative accents
- All icon-only buttons must have `aria-label`

---

## 9. Motion & Animation

### Principles

1. Motion supports meaning — never decorative only
2. Respect `prefers-reduced-motion: reduce`
3. Keep durations short and purposeful

### Duration Scale

| Action | Duration | Easing |
|--------|----------|--------|
| Button hover | 150ms | ease-out |
| Card hover | 200ms | ease-out |
| Modal enter/exit | 200ms | ease-out |
| Toast enter | 250ms | ease-out |
| Page transition | 300ms | ease-in-out |
| Skeleton pulse | 1.5s | ease-in-out (infinite) |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 10. Accessibility

### Target: WCAG AAA

Every release must pass the following checklist.

### Contrast & Color

- [ ] Text contrast 4.5:1 minimum (normal text)
- [ ] Large text (18px+) contrast 3:1 minimum
- [ ] Color never sole indicator of state
- [ ] Focus ring visible on all interactive elements

### Interaction

- [ ] 44x44px minimum touch targets
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover transitions 150-300ms
- [ ] `prefers-reduced-motion` respected

### Semantic HTML

- [ ] All images have meaningful alt text
- [ ] Form inputs have associated `<label>` elements
- [ ] ARIA labels on icon-only buttons
- [ ] Skip navigation link present
- [ ] Semantic elements used: `<nav>`, `<main>`, `<section>`, `<article>`

### Pre-Delivery

- [ ] No emojis — use SVG icons (Lucide)
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] Loading states on form submissions
- [ ] Lazy load heavy assets

---

## 11. Implementation

### CSS Custom Properties

```css
:root {
  /* Primary */
  --color-primary: #0F172A;
  --color-primary-light: #1E293B;
  --color-primary-muted: #475569;

  /* Accent */
  --color-accent: #D97706;
  --color-accent-light: #FBBF24;
  --color-accent-muted: #FFFBEB;

  /* Neutral */
  --color-bg: #FFFFFF;
  --color-bg-subtle: #F8FAFC;
  --color-bg-muted: #F1F5F9;
  --color-border: #E2E8F0;
  --color-border-strong: #CBD5E1;
  --color-text: #0F172A;
  --color-text-secondary: #475569;
  --color-text-muted: #94A3B8;

  /* Semantic */
  --color-success: #059669;
  --color-success-bg: #ECFDF5;
  --color-error: #DC2626;
  --color-error-bg: #FEF2F2;
  --color-warning: #D97706;
  --color-warning-bg: #FFFBEB;
  --color-info: #2563EB;
  --color-info-bg: #EFF6FF;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Z-Index */
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-overlay: 30;
  --z-modal: 40;
  --z-toast: 50;
}
```

### Tailwind Config

```js
// tailwind.config.js — ParishHub Design Tokens
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0F172A',
          light: '#1E293B',
          muted: '#475569',
        },
        accent: {
          DEFAULT: '#D97706',
          light: '#FBBF24',
          muted: '#FFFBEB',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      zIndex: {
        dropdown: '10',
        sticky: '20',
        overlay: '30',
        modal: '40',
        toast: '50',
      },
    },
  },
}
```

---

## 12. Brand Rules

### Do

- Use the M1 shield logo as the primary brand mark
- Keep light theme as the default experience
- Use amber sparingly and purposefully — it is an accent, not a primary
- Maintain clear space around the logo
- Use Inter for all text
- Follow the spacing scale — no magic numbers

### Don't

- Don't modify the logo colors, proportions, or orientation
- Don't use amber as body text on white backgrounds
- Don't introduce colors outside this palette
- Don't use arbitrary z-index values
- Don't use emojis as icons
- Don't skip accessibility checks
- Don't animate the logo without approval

---

*This document is the single source of truth for ParishHub visual design. All frontend work must reference these tokens and patterns. When in doubt, refer to this document.*
