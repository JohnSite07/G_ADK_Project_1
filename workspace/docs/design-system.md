
# Design System: An Interactive Guide to the Universe

This document outlines the visual design system for the project. The goal is to create a dark, immersive, and cinematic experience with high readability.

## Color Tokens

Colors are defined as CSS custom properties for easy use and theming. The palette is inspired by the cosmos: deep blacks, vibrant nebulas, and the stark white of distant stars.

```css
:root {
  /* Brand & Backgrounds */
  --color-background: #000000; /* Deep space black */
  --color-surface: #101015; /* A slightly lighter black for UI surfaces */
  --color-glow-primary: #7F00FF; /* 'Nebula Violet' for glows and highlights */
  --color-glow-secondary: #00BFFF; /* 'Starlight Blue' for secondary accents */

  /* Text */
  --color-text-primary: #FFFFFF; /* Pure white for primary headlines */
  --color-text-secondary: #A0A0B0; /* Light grey for body copy and less important text */
  --color-text-accent: var(--color-glow-secondary);

  /* Interactive Elements */
  --color-button-bg: transparent;
  --color-button-border: var(--color-text-secondary);
  --color-button-text: var(--color-text-secondary);
  --color-button-hover-bg: var(--color-surface);
  --color-button-hover-border: var(--color-text-primary);
  --color-button-hover-text: var(--color-text-primary);
}
```

## Typography

We will use a single, highly-readable sans-serif font, **Inter**, served from Google Fonts. The type scale is responsive and uses `rem` units.

### Tailwind Theme Values

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
    },
    fontSize: {
      'xs': '0.75rem',   // 12px - Tooltips, captions
      'sm': '0.875rem',  // 14px - Small body copy
      'base': '1.125rem', // 18px - Main body copy
      'lg': '1.5rem',    // 24px - Section sub-headlines
      'xl': '2.25rem',   // 36px - Section main headlines
      '2xl': '3.75rem',  // 60px - Major impact headlines
      '3xl': '5rem',     // 80px - "Overture" headline
    },
    // ...
  },
};
```

## Spacing

A 4-pixel base unit is used for a consistent and scalable spacing system.

### Tailwind Theme Values

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    spacing: {
      '0': '0',
      '1': '0.25rem', // 4px
      '2': '0.5rem',  // 8px
      '3': '0.75rem', // 12px
      '4': '1rem',    // 16px
      '5': '1.25rem', // 20px
      '6': '1.5rem',  // 24px
      '8': '2rem',    // 32px
      '10': '2.5rem', // 40px
      '12': '3rem',   // 48px
      '16': '4rem',   // 64px
      '20': '5rem',   // 80px
      '24': '6rem',   // 96px
      '32': '8rem',   // 128px
    },
    // ...
  },
};
```

## Layout Grid

The layout is a single column, centered on the viewport. The main content container will have a max-width to ensure readability on large screens.

*   **Container:** `max-width: 75ch;` (approx 75 characters wide), centered with `margin: 0 auto;`
*   **Padding:** Generous padding on the left and right, e.g., `2rem` (`--space-8`).
*   **Section Height:** Each content section will have a minimum height of `100vh` to ensure one "story" is told per screen view.

## Component Inventory

*   **Headlines:** Use the typography scale. Primary headlines (`font-2xl`, `font-3xl`) should have a subtle text-shadow to create a "glow" effect, using `--color-glow-primary`.
*   **Body Text:** `font-base`, color `--color-text-secondary`.
*   **Buttons:** Outlined style. On hover, the border and text color brighten, and the background subtly fills in. See color variables. They should have a `min-width` for a consistent look.
*   **Tooltips (for CMB):** Small, dark background (`--color-surface`) with light text (`--color-text-secondary`) and `font-xs`. Appears on hover/tap with a slight fade-in.
*   **Pie Chart (Cosmic):** Uses the color palette. Segments should be `--color-glow-primary`, `--color-glow-secondary`, and a third color like a deep red (`#FF4136`) for contrast.
