# Design System: "The Story of Everything"

This document outlines the visual design system, component inventory, and layout principles for the project. It is intended to be used as a reference for developers to ensure a consistent and high-quality user interface.

## 1. Color Palette

The color palette is inspired by the deep, vibrant, and contrasting visuals of space. It's designed for a dark-mode experience. Colors are defined as CSS custom properties in HSL format for easy manipulation (e.g., adding opacity).

```css
:root {
  /* Brand & Accents */
  --color-primary: 217 91% 60%; /* A bright, celestial blue */
  --color-secondary: 282 44% 53%; /* A deep nebula purple */
  --color-accent: 318 81% 56%; /* A vibrant magenta for highlights */

  /* Backgrounds */
  --color-background: 222 47% 7%; /* A very dark, near-black blue */
  --color-surface: 222 40% 12%; /* Slightly lighter for cards and surfaces */

  /* Typography */
  --color-text-primary: 210 40% 98%; /* Almost white for high contrast */
  --color-text-secondary: 210 30% 70%; /* Lighter gray for sub-headings and body */
  --color-text-muted: 210 20% 50%; /* For captions and less important text */
}
```

### Tailwind CSS Theme (`tailwind.config.js`)

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'hsl(var(--color-primary) / <alpha-value>)',
        secondary: 'hsl(var(--color-secondary) / <alpha-value>)',
        accent: 'hsl(var(--color-accent) / <alpha-value>)',
        background: 'hsl(var(--color-background) / <alpha-value>)',
        surface: 'hsl(var(--color-surface) / <alpha-value>)',
        'text-primary': 'hsl(var(--color-text-primary) / <alpha-value>)',
        'text-secondary': 'hsl(var(--color-text-secondary) / <alpha-value>)',
        'text-muted': 'hsl(var(--color-text-muted) / <alpha-value>)',
      },
    },
  },
};
```

## 2. Typography

A clean, readable sans-serif font is recommended. `Inter` is a great choice. The typographic scale is responsive and uses `rem` units.

### Font Family

- **Headings & Body:** `Inter`, or a similar sans-serif font.

### Typographic Scale (Tailwind CSS)

```javascript
module.exports = {
  theme: {
    fontSize: {
      'xs': ['0.75rem', { lineHeight: '1rem' }], // 12px
      'sm': ['0.875rem', { lineHeight: '1.25rem' }], // 14px
      'base': ['1rem', { lineHeight: '1.5rem' }], // 16px
      'lg': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
      'xl': ['1.25rem', { lineHeight: '1.75rem' }], // 20px
      '2xl': ['1.5rem', { lineHeight: '2rem' }], // 24px
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
      '5xl': ['3rem', { lineHeight: '1' }], // 48px
      '6xl': ['3.75rem', { lineHeight: '1' }], // 60px
      '7xl': ['4.5rem', { lineHeight: '1' }], // 72px
      '8xl': ['6rem', { lineHeight: '1' }], // 96px
    },
  },
};
```

### Usage

- **H1 (`.text-7xl`, `font-bold`):** "The Story of Everything"
- **H2 (`.text-5xl`, `font-bold`):** Section headlines like "In the Beginning..."
- **Sub-heading (`.text-xl`, `font-light`):** "A journey from the beginning..."
- **Body Text (`.text-lg`, `font-normal`, `text-text-secondary`):** Main descriptive text.

## 3. Spacing

An 8-point grid system (`1 unit = 8px = 0.5rem`) is used for all margins, paddings, and gaps to ensure visual consistency.

### Spacing Scale (Tailwind's Default)

We will use Tailwind's default spacing scale, which is based on `0.25rem` increments and is highly comprehensive.

## 4. Layout

The website uses a single-column, centered layout.

- **Container:** A main content container will be used for each section to constrain the width of the text for readability on large screens.
  - `max-width: 72rem;` (`max-w-6xl` in Tailwind)
  - `margin: 0 auto;` (`mx-auto`)
  - `padding: 0 1rem;` (`px-4`)

## 5. Component Inventory

A preliminary list of components required for the build.

- **`Section`:** A full-width container with a centered inner `Container`. Takes up `100vh`.
- **`Container`:** A max-width, centered component for holding content.
- **`Typography`:** Components for H1, H2, H3, P, etc., styled according to the type scale.
- **`Hero`:** The initial landing view containing the main title, subtitle, and scroll prompt. Includes the `hero-starfield` animation.
- **`ScrollPrompt`:** The animated "Scroll to explore" element.
- **`GalaxyViewer`:** The interactive `react-three-fiber` component for the galaxy model.
- **`SolarSystemViewer`:** The interactive `react-three-fiber` component for the solar system model.
- **`PlanetCard`:** A small info card that appears on click within the `SolarSystemViewer`.
- **`ImageCarousel`:** A simple carousel to display high-resolution space telescope images.
- **`Footer`:** Contains closing text, credits, and external links.
