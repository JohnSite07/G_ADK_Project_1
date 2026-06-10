
# Wilder: Motion & Interaction Specification

This document details the key animations and interactions for the Wilder website. The goal of our motion design is to be immersive, intuitive, and purposeful, enhancing the user's connection to the content without being distracting.

---

## Guiding Principles

1.  **Subtle & Natural:** Motion should feel organic, like a gentle breeze or the slow pan of a nature documentary. Avoid jarring or overly "digital" effects.
2.  **Purposeful:** Animations should provide feedback, guide attention, or reveal information. They should never exist purely for decoration.
3.  **Performant & Accessible:** All animations must be highly performant (preferring CSS transforms and opacity) and must include a `prefers-reduced-motion` fallback.

---

## Interaction Inventory

### 1. Homepage Hero Fade & Zoom

*   **Description:** On page load, the hero video/image background subtly zooms in while the overlay text ("Breathe. Explore. Reconnect.") fades into view.
*   **Goal:** Create an immediate sense of immersion and calm.

| Property            | Specification                                                                      |
| ------------------- | ---------------------------------------------------------------------------------- |
| **Technique**       | CSS Animations. A `scale` transform on a pseudo-element for the zoom, `opacity` and `transform` for the text. |
| **Trigger**         | Page load.                                                                         |
| **Properties**      | `transform: scale()`, `opacity`, `transform: translateY()`                         |
| **Easing**          | `ease-out` (cubic-bezier(0.2, 0.8, 0.2, 1))                                          |
| **Duration**        | - **Zoom:** 15s (very slow and subtle)<br>- **Text Fade/Rise:** 1.2s with a 0.5s delay |
| **Reduced Motion**  | Disable the background zoom. Text and content are visible on load with no transition.   |

---

### 2. Scroll-Driven Parallax on Detail Pages

*   **Description:** As the user scrolls down a destination detail page, the hero image moves at a slower rate than the content, creating a sense of depth.
*   **Goal:** Add a modern, premium feel and keep the destination's beauty in view longer.

| Property            | Specification                                                              |
| ------------------- | -------------------------------------------------------------------------- |
| **Technique**       | GSAP + ScrollTrigger. This gives us precise control over the parallax speed. |
| **Trigger**         | User scroll on pages with a hero image (e.g., `/explore/:slug`).             |
| **Properties**      | `transform: translateY()` on the image element.                            |
| **Easing**          | `none` (linear), as the animation is directly mapped to the scroll position. |
| **Duration**        | Linked directly to the scroll speed and viewport height.                   |
| **Reduced Motion**  | Disable the effect. The image scrolls normally with the page.              |

---

### 3. Interactive "Benefits of Nature" Visualization

*   **Description:** An animated graphic that transitions from a "stressed" to a "calm" state as the user scrolls the "Why Go Wild?" section into view.
*   **Goal:** Make abstract health benefits tangible and memorable.

| Property            | Specification                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Technique**       | GSAP + ScrollTrigger controlling SVG path animations (`<path d="...">`). Ideal for morphing shapes between two states. |
| **Trigger**         | When the component scrolls into the viewport.                                                                       |
| **Properties**      | SVG path data (`d`), `stroke-dasharray`, `stroke-dashoffset`.                                                         |
| **Easing**          | `Power3.easeInOut` for a smooth, organic transition.                                                                |
| **Duration**        | 1.5s                                                                                                                |
| **Reduced Motion**  | Display the final "calm" state of the graphic statically. No animation occurs.                                      |

---

### 4. Explore Page Filter Animation

*   **Description:** When a user applies a filter, non-matching items fade out smoothly, and the remaining items rearrange themselves into a new grid layout.
*   **Goal:** Make the filtering process feel fluid and responsive, not jarring.

| Property            | Specification                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Technique**       | Framework-based state transition combined with CSS Transitions. On state change, apply classes to fade-out/fade-in items. A library like Isotope.js is a good alternative if complex sorting is needed. |
| **Trigger**         | User click on a filter button/chip.                                                                                            |
| **Properties**      | `opacity`, `transform: scale(0.95)`. The layout shift itself will be handled by the grid reflowing.                             |
| **Easing**          | `ease-in-out`                                                                                                                  |
| **Duration**        | 350ms. Fast enough to feel responsive.                                                                                         |
| **Reduced Motion**  | No transitions. The grid updates instantly to show the filtered results.                                                         |

