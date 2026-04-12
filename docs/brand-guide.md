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
- Navy on White: **16.75:1** ✓
- Amber on White: **3.06:1** (text) / **3.06:1** (large text only)
- Amber on Navy: **5.47:1** ✓ (use amber on navy for CTA buttons)
- White on Navy: **16.75:1** ✓
- Navy 400 on White: **7.45:1** ✓

> **Rule:** Never use amber (#D97706) as text on white backgrounds for body text. Use it for large headings (24px+), buttons (white text on amber), or as an accent on dark backgrounds.

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

### Tailwind Config

```js
// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    },
  },
}
```

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

```html
<!-- Primary -->
<button class="bg-[#0F172A] text-white px-5 py-2.5 rounded font-medium
               hover:bg-[#1E293B] transition-colors duration-200
               focus:outline-none focus:ring-2 focus:ring-[#D97706] focus:ring-offset-2
               cursor-pointer">
  Save Record
</button>

<!-- Accent / CTA -->
<button class="bg-[#D97706] text-white px-5 py-2.5 rounded font-medium
               hover:bg-[#B45309] transition-colors duration-200
               focus:outline-none focus:ring-2 focus:ring-[#D97706] focus:ring-offset-2
               cursor-pointer">
  Add Member
</button>

<!-- Secondary / Outline -->
<button class="border border-[#E2E8F0] text-[#0F172A] px-5 py-2.5 rounded font-medium
               hover:bg-[#F8FAFC] transition-colors duration-200
               focus:outline-none focus:ring-2 focus:ring-[#D97706] focus:ring-offset-2
               cursor-pointer">
  Cancel
</button>

<!-- Destructive -->
<button class="bg-[#DC2626] text-white px-5 py-2.5 rounded font-medium
               hover:bg-[#B91C1C] transition-colors duration-200
               focus:outline-none focus:ring-2 focus:ring-[#DC2626] focus:ring-offset-2
               cursor-pointer">
  Delete
</button>
```

**Button Sizing:**
- Small: `px-3 py-1.5 text-sm` (14px)
- Default: `px-5 py-2.5 text-base` (16px)
- Large: `px-6 py-3 text-lg` (18px)
- **Minimum touch target: 44x44px**

### Form Inputs

```html
<!-- Text Input -->
<div class="space-y-1.5">
  <label for="name" class="block text-sm font-medium text-[#0F172A]">
    Full Name
  </label>
  <input
    type="text"
    id="name"
    class="w-full px-3 py-2.5 border border-[#E2E8F0] rounded
           text-[#0F172A] placeholder-[#94A3B8]
           focus:outline-none focus:ring-2 focus:ring-[#D97706] focus:border-[#D97706]
           transition-colors duration-150"
    placeholder="Enter full name"
  />
</div>

<!-- Error State -->
<input
  class="w-full px-3 py-2.5 border border-[#DC2626] rounded
         text-[#0F172A] bg-[#FEF2F2]
         focus:outline-none focus:ring-2 focus:ring-[#DC2626] focus:border-[#DC2626]"
/>
<p class="text-sm text-[#DC2626] mt-1">This field is required</p>
```

### Cards

```html
<div class="bg-white border border-[#E2E8F0] rounded-lg p-5
            hover:shadow-md transition-shadow duration-200">
  <h4 class="text-lg font-semibold text-[#0F172A] mb-2">Card Title</h4>
  <p class="text-[#475569] text-base leading-relaxed">
    Card content with secondary text styling.
  </p>
</div>
```

### Badges / Tags

```html
<!-- Active -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
             bg-[#ECFDF5] text-[#059669]">
  Active
</span>

<!-- Inactive -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
             bg-[#F1F5F9] text-[#475569]">
  Inactive
</span>

<!-- Accent -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
             bg-[#FFFBEB] text-[#D97706]">
  Pending
</span>
```

### Navigation

```html
<nav class="bg-[#0F172A] text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center space-x-8">
        <span class="text-xl font-bold">ParishHub</span>
        <a href="#" class="text-[#CBD5E1] hover:text-white transition-colors duration-150
                          focus:outline-none focus:ring-2 focus:ring-[#D97706] rounded px-2 py-1">
          Dashboard
        </a>
      </div>
    </div>
  </div>
</nav>
```

### Alerts / Notifications

```html
<!-- Success -->
<div class="flex items-start gap-3 p-4 bg-[#ECFDF5] border border-[#059669]/20 rounded-lg"
     role="alert">
  <svg class="w-5 h-5 text-[#059669] mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
  </svg>
  <p class="text-[#059669] text-sm font-medium">Record saved successfully.</p>
</div>

<!-- Error -->
<div class="flex items-start gap-3 p-4 bg-[#FEF2F2] border border-[#DC2626]/20 rounded-lg"
     role="alert">
  <svg class="w-5 h-5 text-[#DC2626] mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
  </svg>
  <p class="text-[#DC2626] text-sm font-medium">Something went wrong. Please try again.</p>
</div>
```

### Tables

```html
<div class="overflow-x-auto">
  <table class="w-full text-left">
    <thead class="bg-[#F8FAFC] border-b border-[#E2E8F0]">
      <tr>
        <th class="px-4 py-3 text-xs font-semibold text-[#475569] uppercase tracking-wider">
          Name
        </th>
        <th class="px-4 py-3 text-xs font-semibold text-[#475569] uppercase tracking-wider">
          Status
        </th>
      </tr>
    </thead>
    <tbody class="divide-y divide-[#E2E8F0]">
      <tr class="hover:bg-[#F8FAFC] transition-colors duration-150">
        <td class="px-4 py-3 text-[#0F172A]">John Doe</td>
        <td class="px-4 py-3">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                       bg-[#ECFDF5] text-[#059669]">Active</span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 6. Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-base` | 0 | Default stacking |
| `z-dropdown` | 10 | Dropdowns, popovers |
| `z-sticky` | 20 | Sticky headers, navbars |
| `z-overlay` | 30 | Modal backdrops |
| `z-modal` | 40 | Modal dialogs |
| `z-toast` | 50 | Toast notifications |

> **Rule:** Never use arbitrary z-index values. Always use this scale.

---

## 7. Interaction States

### Hover Transitions
- **Duration:** 150-300ms
- **Easing:** `ease-in-out` (default) or `ease-out` for entering elements
- All clickable elements must have visible hover states

### Focus States
- **Ring:** 2px solid `#D97706` with 2px offset
- Must be visible on ALL interactive elements
- Never use `outline: none` without replacing with a focus ring

### Loading States
- Form submissions: show spinner → success/error feedback
- Lazy load heavy assets (tables, images, charts)
- Skeleton screens for data-heavy pages

---

## 8. Accessibility Checklist

### Compliance Target: WCAG AAA

- [ ] Text contrast ratio minimum **4.5:1** (normal text), **3:1** (large text 18px+)
- [ ] All interactive elements have **focus states** visible via keyboard
- [ ] **44x44px minimum** touch targets on mobile
- [ ] All images have meaningful `alt` text
- [ ] Form inputs have associated `<label>` elements
- [ ] ARIA labels on icon-only buttons
- [ ] Skip navigation link for keyboard users
- [ ] `prefers-reduced-motion` respected — disable animations when set
- [ ] Semantic HTML (`<nav>`, `<main>`, `<section>`, `<article>`)
- [ ] Color is never the sole indicator of state (always paired with text/icon)

### Pre-Delivery Checklist

- [ ] No emojis as icons — use **SVG icons** (Heroicons or Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover transitions 150-300ms
- [ ] Text contrast 4.5:1 minimum
- [ ] Responsive tested at: 375px, 768px, 1024px, 1440px
- [ ] Form submissions show loading → success/error feedback
- [ ] `prefers-reduced-motion` media query in CSS

---

## 9. Iconography

**Library:** Lucide (preferred) or Heroicons
**Style:** Outline, 1.5px stroke
**Sizes:** 16px (inline), 20px (default), 24px (large), 32px (feature)

```html
<!-- Lucide example -->
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
     stroke-linejoin="round">
  <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>
  <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
</svg>
```

---

## 10. Motion & Animation

### Principles
- Motion supports meaning — never decorative only
- Respect `prefers-reduced-motion: reduce`
- Keep durations short (150-300ms)

### Standard Animations

| Action | Duration | Easing | Property |
|--------|----------|--------|----------|
| Button hover | 150ms | ease-out | background-color |
| Card hover | 200ms | ease-out | box-shadow |
| Modal enter | 200ms | ease-out | opacity + transform |
| Toast enter | 250ms | ease-out | transform (slide up) |
| Page transition | 300ms | ease-in-out | opacity |

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

## 11. CSS Custom Properties (Copy-Paste Ready)

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

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Z-Index */
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-overlay: 30;
  --z-modal: 40;
  --z-toast: 50;
}

/* Dark Mode */
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

## 12. Tailwind Config Reference

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

*This document is the single source of truth for ParishHub's visual design. All frontend work should reference these tokens and patterns.*
