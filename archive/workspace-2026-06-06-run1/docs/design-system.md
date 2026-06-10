
# Wilder: Design System

This document outlines the core visual components of the Wilder website. The system is designed to be natural, calming, and highly readable, evoking the feeling of a modern field guide.

---

## 1. Color Palette

The palette is inspired by natural landscapes—deep forests, rich earth, and warm sunlight—with a clean, light base for content. Colors are defined as HSL values within CSS custom properties for easy manipulation and theming.

```css
:root {
  /* Primary & Accents */
  --color-primary: hsl(158, 25%, 30%);   /* Deep Forest Green */
  --color-primary-light: hsl(158, 25%, 40%);
  --color-primary-dark: hsl(158, 25%, 20%);
  --color-accent: hsl(38, 90%, 65%);     /* Warm Sunlight Yellow */
  --color-accent-dark: hsl(38, 90%, 55%);

  /* Neutrals */
  --color-text: hsl(210, 15%, 20%);         /* Dark Slate */
  --color-text-muted: hsl(210, 12%, 45%);
  --color-surface: hsl(30, 20%, 98%);       /* Off-White/Light Tan */
  --color-border: hsl(210, 15%, 88%);
  --color-background: hsl(0, 0%, 100%);     /* Pure White */

  /* Semantic Colors */
  --color-success: hsl(140, 50%, 45%);
  --color-warning: hsl(45, 100%, 55%);
  --color-error: hsl(0, 70%, 50%);
}
```

---

## 2. Typography

We use a classic serif for headlines to give a sense of authority and timelessness, paired with a highly legible sans-serif for body copy and UI elements.

*   **Heading Font:** Lora (Google Fonts)
*   **Body Font:** Inter (Google Fonts)

### Tailwind Theme Scale

This scale is defined in `rem` for accessibility and responsiveness.

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    fontSize: {
      'xs':   ['0.75rem',  { lineHeight: '1rem' }],      // 12px
      'sm':   ['0.875rem', { lineHeight: '1.25rem' }],   // 14px
      'base': ['1rem',     { lineHeight: '1.75rem' }],   // 16px
      'lg':   ['1.125rem', { lineHeight: '1.75rem' }],   // 18px
      'xl':   ['1.25rem',  { lineHeight: '2rem' }],      // 20px
      '2xl':  ['1.5rem',   { lineHeight: '2.25rem' }],   // 24px
      '3xl':  ['1.875rem', { lineHeight: '2.5rem' }],   // 30px
      '4xl':  ['2.5rem',   { lineHeight: '3rem' }],      // 40px
      '5xl':  ['3.25rem',  { lineHeight: '1.1' }],      // 52px
      '6xl':  ['4rem',     { lineHeight: '1' }],         // 64px
    },
    // ...
  }
}
```

---

## 3. Spacing & Sizing

A 4-point grid (1 unit = 0.25rem) is used for all spacing, padding, and margins to ensure consistency.

### Tailwind Theme Scale

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    spacing: {
      'px': '1px',
      '0': '0',
      '1': '0.25rem',  // 4px
      '2': '0.5rem',   // 8px
      '3': '0.75rem',  // 12px
      '4': '1rem',     // 16px
      '5': '1.25rem',  // 20px
      '6': '1.5rem',   // 24px
      '8': '2rem',     // 32px
      '10': '2.5rem',  // 40px
      '12': '3rem',    // 48px
      '16': '4rem',    // 64px
      '20': '5rem',    // 80px
      '24': '6rem',    // 96px
      '32': '8rem',    // 128px
    },
    // ...
  }
}
```

---

## 4. Layout & Grid

*   **Grid System:** A 12-column flexible grid will be used for primary page layouts.
*   **Container:** The main content container will have a max-width of `1280px` (`max-w-7xl` in Tailwind) with horizontal padding.
*   **Breakpoints:** Standard responsive breakpoints will be used (sm, md, lg, xl, 2xl). Design is mobile-first.

---

## 5. Component Inventory

A preliminary list of key components to be built based on this system.

*   **Buttons:**
    *   `Primary`: Solid fill (`--color-primary`), white text. Used for main CTAs.
    *   `Secondary`: Outline (`--color-text`), text in `--color-text`. Used for less prominent actions.
    *   `Link`: Styled like a hyperlink but with added padding for a larger click target.
*   **Cards:**
    *   `Destination Card`: Image, location name, and short description. Features a subtle hover effect (slight lift and shadow).
    *   `Story Card`: Image, category, title, and author.
*   **Forms & Inputs:**
    *   `Text Input`: Clean, minimal style with a clear border on focus.
    *   `Search Bar`: A prominent input field, often paired with a primary button.
    *   `Filter Chips`: Button-like elements for selecting categories on the Explore page.
*   **Navigation:**
    *   `Main Header`: Contains logo and primary navigation links. Becomes sticky after scrolling past the hero section.
    *   `Footer`: Contains sitemap links, social media icons, and mission statement.
*   **Tags/Badges:**
    *   Small, rounded elements used to display metadata like difficulty (`Easy`, `Moderate`) or categories.
*   **Iconography:**
    *   A set of clean, line-art icons (e.g., Feather Icons or a custom set) will be used for UI elements and the "Why Go Wild?" section.
