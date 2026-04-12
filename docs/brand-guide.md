# ParishHub Brand Guide & Design System

**Version:** 1.0
**Last Updated:** 2026-04-12
**Style:** Accessible & Ethical
**Status:** Active

---

## 1. Brand Identity

**ParishHub** is a community management platform for Catholic parishes. The brand conveys trust, warmth, professionalism, and inclusivity.

### Brand Pillars
- **Trustworthy** — Handles sacred community data with care
- **Accessible** — WCAG AAA compliant, works for everyone
- **Warm** — Approachable, not clinical or cold
- **Professional** — Enterprise-grade reliability for parish staff

---

## 2. Color System

### Primary Palette

| Role | Name | Hex | CSS Variable | Usage |
|------|------|-----|-------------|-------|
| Primary | Navy | `#0F172A` | `--color-primary` | Headers, nav, primary buttons, key UI chrome |
| Primary Light | Navy 600 | `#1E293B` | `--color-primary-light` | Hover states, secondary panels |
| Primary Muted | Navy 400 | `#475569` | `--color-primary-muted` | Body text on light backgrounds |
| Accent | Amber | `#D97706` | `--color-accent` | CTAs, highlights, active states, links |
| Accent Light | Amber 300 | `#FBBF24` | `--color-accent-light` | Hover on accent, soft highlights |
| Accent Muted | Amber 50 | `#FFFBEB` | `--color-accent-muted` | Accent background tints |

### Neutral Palette

| Role | Hex | CSS Variable |
|------|-----|-------------|
| Background | `#FFFFFF` | `--color-bg` |
| Background Subtle | `#F8FAFC` | `--color-bg-subtle` |
| Background Muted | `#F1F5F9` | `--color-bg-muted` |
| Border | `#E2E8F0` | `--color-border` |
| Border Strong | `#CBD5E1` | `--color-border-strong` |
| Text Primary | `#0F172A` | `--color-text` |
| Text Secondary | `#475569` | `--color-text-secondary` |
| Text Muted | `#94A3B8` | `--color-text-muted` |
| White | `#FFFFFF` | `--color-white` |

### Semantic Colors

| Role | Hex | CSS Variable | Usage |
|------|-----|-------------|-------|
| Success | `#059669` | `--color-success` | Confirmations, active records |
| Success BG | `#ECFDF5` | `--color-success-bg` | Success message backgrounds |
| Error | `#DC2626` | `--color-error` | Validation errors, destructive actions |
| Error BG | `#FEF2F2` | `--color-error-bg` | Error message backgrounds |
| Warning | `#D97706` | `--color-warning` | Warnings (uses accent) |
| Warning BG | `#FFFBEB` | `--color-warning-bg` | Warning message backgrounds |
| Info | `#2563EB` | `--color-info` | Informational notices |
| Info BG | `#EFF6FF` | `--color-info-bg` | Info message backgrounds |

### Dark Mode Palette

| Role | Hex | CSS Variable |
|------|-----|-------------|
| Background | `#0F172A` | `--color-dark-bg` |
| Background Subtle | `#1E293B` | `--color-dark-bg-subtle` |
| Background Muted | `#334155` | `--color-dark-bg-muted` |
| Border | `#334155` | `--color-dark-border` |
| Text Primary | `#F8FAFC` | `--color-dark-text` |
| Text Secondary | `#CBD5E1` | `--color-dark-text-secondary` |
| Text Muted | `#94A3B8` | `--color-dark-text-muted` |
| Accent | `#FBBF24` | `--color-dark-accent` |

### Color Contrast Ratios (WCAG AAA)
- Navy on White: **16.75:1** PASS
- Amber on White: **3.06:1** (large text only — do NOT use for body text)
- Amber on Navy: **5.47:1** PASS (use amber text on navy backgrounds)
- White on Navy: **16.75:1** PASS
- Navy 400 on White: **7.45:1** PASS

**Rule:** Never use amber (#D97706) as body text on white. Use it for large headings (24px+), buttons (white text on amber bg), or as accent on dark backgrounds.

---

## 3. Typography

### Font Stack

**Primary:** Inter
**Fallback:** -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### Type Scale

| Level | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Display | 48px / 3rem | 700 | 1.1 | -0.02em | Hero headings |
| H1 | 36px / 2.25rem | 700 | 1.2 | -0.01em | Page titles |
| H2 | 30px / 1.875rem | 600 | 1.3 | -0.01em | Section headings |
| H3 | 24px / 1.5rem | 600 | 1.4 | 0 | Subsection headings |
| H4 | 20px / 1.25rem | 600 | 1.4 | 0 | Card titles, labels |
| Body Large | 18px / 1.125rem | 400 | 1.6 | 0 | Intro paragraphs |
| Body | 16px / 1rem | 400 | 1.6 | 0 | Default body text |
| Body Small | 14px / 0.875rem | 400 | 1.5 | 0.01em | Secondary text, captions |
| Caption | 12px / 0.75rem | 500 | 1.4 | 0.02em | Labels, badges, metadata |

---

## 4. Spacing & Layout

### Spacing Scale (4px base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight inner padding |
| `space-2` | 8px | Icon-text gap, small padding |
| `space-3` | 12px | Form field internal padding |
| `space-4` | 16px | Default component padding |
| `space-5` | 20px | Card padding |
| `space-6` | 24px | Section padding |
| `space-8` | 32px | Large section gaps |
| `space-10` | 40px | Page section spacing |
| `space-12` | 48px | Major section dividers |
| `space-16` | 64px | Page margins (desktop) |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Subtle rounding (badges) |
| `rounded` | 6px | Default (inputs, buttons) |
| `rounded-md` | 8px | Cards, modals |
| `rounded-lg` | 12px | Large panels |
| `rounded-full` | 9999px | Avatars, pills |

### Breakpoints

| Name | Width | Target |
|------|-------|--------|
| `sm` | 375px | Mobile |
| `md` | 768px | Tablet |
| `lg` | 1024px | Small desktop |
| `xl` | 1440px | Desktop |

---

## 5. Components

### Buttons

**Primary** — Navy background, white text
**Accent/CTA** — Amber background, white text
**Secondary/Outline** — Transparent, border, navy text
**Destructive** — Red background, white text

Sizing:
- Small: `px-3 py-1.5 text-sm` (14px)
- Default: `px-5 py-2.5 text-base` (16px)
- Large: `px-6 py-3 text-lg` (18px)
- Minimum touch target: **44x44px**

All buttons require:
- `cursor-pointer`
- `transition-colors duration-200`
- `focus:ring-2 focus:ring-[#D97706] focus:ring-offset-2`

### Form Inputs

- Label: `text-sm font-medium text-[#0F172A]`
- Input: `border border-[#E2E8F0] rounded px-3 py-2.5`
- Focus: `focus:ring-2 focus:ring-[#D97706] focus:border-[#D97706]`
- Error: `border-[#DC2626] bg-[#FEF2F2]`
- Hint text: `text-sm text-[#94A3B8]`

### Cards

- Background: white
- Border: `1px solid #E2E8F0`
- Border radius: 8px
- Padding: 20px
- Hover: `shadow-md` with 200ms transition

### Badges

- **Active:** `bg-[#ECFDF5] text-[#059669]`
- **Inactive:** `bg-[#F1F5F9] text-[#475569]`
- **Pending:** `bg-[#FFFBEB] text-[#D97706]`

### Alerts

- **Success:** `bg-[#ECFDF5] border-[#059669]/20 text-[#059669]`
- **Error:** `bg-[#FEF2F2] border-[#DC2626]/20 text-[#DC2626]`
- Always use `role="alert"` for accessibility
- Include SVG icon (no emojis)

### Tables

- Header: `bg-[#F8FAFC]`, uppercase caption text
- Rows: `divide-[#E2E8F0]`, hover `bg-[#F8FAFC]`
- Cell padding: `px-4 py-3`

### Navigation

- Background: `#0F172A` (navy)
- Text: white for brand, `#CBD5E1` for links
- Link hover: white with 150ms transition
- Height: 56px (h-14)

---

## 6. Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-dropdown` | 10 | Dropdowns, popovers |
| `z-sticky` | 20 | Sticky headers, navbars |
| `z-overlay` | 30 | Modal backdrops |
| `z-modal` | 40 | Modal dialogs |
| `z-toast` | 50 | Toast notifications |

**Rule:** Never use arbitrary z-index values. Always use this scale.

---

## 7. Interaction States

### Hover
- Duration: 150-300ms
- Easing: ease-in-out or ease-out
- All clickable elements must have visible hover states

### Focus
- Ring: 2px solid `#D97706` with 2px offset
- Visible on ALL interactive elements
- Never use `outline: none` without replacement

### Loading
- Form submissions: show spinner then success/error feedback
- Lazy load heavy assets (tables, images, charts)
- Skeleton screens for data-heavy pages

---

## 8. Iconography

**Library:** Lucide (preferred) or Heroicons
**Style:** Outline, 1.5px stroke
**Sizes:** 16px (inline), 20px (default), 24px (large), 32px (feature)

Never use emojis as icons. Always use SVG.

---

## 9. Motion & Animation

### Principles
- Motion supports meaning — never decorative only
- Respect `prefers-reduced-motion: reduce`
- Keep durations short (150-300ms)

### Standard Durations

| Action | Duration | Easing |
|--------|----------|--------|
| Button hover | 150ms | ease-out |
| Card hover | 200ms | ease-out |
| Modal enter | 200ms | ease-out |
| Toast enter | 250ms | ease-out |
| Page transition | 300ms | ease-in-out |

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

## 10. Accessibility Checklist

### WCAG AAA Target

**Contrast & Color**
- [ ] Text contrast 4.5:1 minimum (normal text)
- [ ] Large text (18px+) contrast 3:1 minimum
- [ ] Color never sole indicator of state
- [ ] Focus ring visible on all interactive elements

**Interaction**
- [ ] 44x44px minimum touch targets
- [ ] cursor-pointer on all clickable elements
- [ ] Hover transitions 150-300ms
- [ ] prefers-reduced-motion respected

**Semantic HTML**
- [ ] All images have meaningful alt text
- [ ] Form inputs have associated labels
- [ ] ARIA labels on icon-only buttons
- [ ] Skip navigation link present
- [ ] Semantic elements (nav, main, section)

**Pre-Delivery**
- [ ] No emojis — use SVG icons (Lucide)
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] Loading states on form submissions
- [ ] Lazy load heavy assets

---

## 11. CSS Custom Properties

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

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0F172A;
    --color-bg-subtle: #1E293B;
    --color-bg-muted: #334155;
    --color-border: #334155;
    --color-text: #F8FAFC;
    --color-text-secondary: #CBD5E1;
    --color-text-muted: #94A3B8;
    --color-accent: #FBBF24;
  }
}
```

---

## 12. Tailwind Config

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

*This document is the single source of truth for ParishHub visual design. All frontend work should reference these tokens and patterns.*
