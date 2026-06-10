
# Motion & Interaction Spec

This document specifies the animation and interaction behavior for the key narrative moments in "An Interactive Guide to the Universe".

**Core Philosophy:** Motion should feel cinematic, fluid, and directly tied to the user's scroll. It serves to explain the concept, not just to decorate the page. We will primarily use `GSAP + ScrollTrigger` for orchestrating animations and `react-three-fiber` for 3D scenes.

| Section & Interaction | Primary Technique | Trigger | Easing | Duration | Reduced Motion Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. The Big Bang** | `react-three-fiber` (Particles)<br/>`GSAP + ScrollTrigger` (Orchestration) | User scroll down from top. | `Power2.inOut` | Tied to scroll distance (`200vh`) | Cross-fade from a single point image to a static starfield image. |
| **2. 3D Galaxy Cluster** | `react-three-fiber` (Scene)<br/>`GSAP + ScrollTrigger` (Camera/Scale) | User scroll through Section 2. | `Linear` | Tied to scroll distance (~`150vh`) | A pre-rendered video auto-playing on loop, or a series of static images showing the expansion. |
| **3. CMB Data Viz** | `GSAP + ScrollTrigger` (Cross-fade/Pixelation effect) | User scroll into Section 3. | `Sine.out` | Tied to scroll distance (`100vh`) | Display the final, high-resolution CMB map directly with no "static" or resolving animation. |
| **4. Cosmic Pie Chart**| `D3.js` or `Visx`<br/>`GSAP + ScrollTrigger` (Triggering) | Element enters viewport. | `Elastic.out(1, 0.5)` | Fixed `1.5s` on trigger | Display the final, complete pie chart with all three segments visible. No animation. |
| **5. Branching Fates** | `CSS Animations` or `anime.js` | `onClick` event for each of the three buttons. | `easeInOut` | `2-3s` per animation | Instead of playing an animation, clicking a button reveals a static illustration for that fate. |

## Global Motion Elements

*   **Smooth Scroll:** To enhance the cinematic feel and ensure consistent animation performance across devices, we will implement a smooth scroll library like **Lenis**. This normalizes the scroll input, which is crucial for `ScrollTrigger`'s reliability.
*   **Headline & Text Reveals:** As users scroll, headlines and their corresponding text paragraphs will fade and slide into view. This will be a subtle, reusable effect managed by `GSAP + ScrollTrigger` on a global scale.
    *   **Technique:** CSS + `GSAP`
    *   **Trigger:** Element is `80%` visible in viewport.
    *   **Animation:** `opacity: 0 -> 1`, `y: 20px -> 0`
    *   **Duration:** `0.8s`
    *   **Easing:** `Power3.out`
    *   **Reduced Motion Fallback:** No animation; elements are simply visible.
