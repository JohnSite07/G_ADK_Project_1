# Motion & Interaction Specification

This document details the specification for all animations and interactive elements on the website, including the technology, triggers, and fallbacks for accessibility.

---

### 1. Hero Starfield (`hero-starfield`)

- **Description:** A continuous, slow-moving starfield to create an immersive "flying through space" effect in the hero section.
- **Technique:** **`react-three-fiber`**. A `THREE.Points` object with a large number of vertices. The camera will move slowly along the Z-axis, or the points themselves will be animated.
- **Trigger:** Automatic on page load; continuous animation loop.
- **Easing:** `linear`. The movement should be constant and subtle.
- **Duration:** Continuous.
- **`prefers-reduced-motion` Fallback:** The animation is disabled. A static, high-resolution image of a starfield is displayed as the background.

---

### 2. Big Bang Expansion (`big-bang-expansion`)

- **Description:** A visual representation of the Big Bang, where a single point of light expands to fill the screen as the user scrolls into the section.
- **Technique:** **`GSAP + ScrollTrigger`**. Animate the `scale` and `opacity` of a single `div` or a `react-three-fiber` mesh. The animation is scrubbed by the user's scroll position.
- **Trigger:** Scroll. The animation starts when the "The Big Bang" section's top edge meets the bottom of the viewport and completes when the section is centered in the viewport.
- **Easing:** `power2.in` for the initial expansion burst.
- **Duration:** Tied to scroll distance (e.g., over `100vh` of scrolling).
- **`prefers-reduced-motion` Fallback:** The element is not animated. A static graphic representing the expansion fades in as a whole when the section scrolls into view.

---

### 3. Interactive Galaxy (`galaxy-viewer`)

- **Description:** A 3D model of a spiral galaxy that the user can rotate.
- **Technique:** **`react-three-fiber` + `@react-three/drei`**. A `gltf` model of a galaxy is loaded. User interaction is handled by `drei/OrbitControls`.
- **Trigger:** User interaction (click-and-drag or touch-and-drag) to rotate. An optional, slow, automatic rotation can be implemented, which is then disabled upon first user interaction.
- **Easing:** Default easing and damping from `OrbitControls` (`enableDamping = true`).
- **Duration:** N/A (user-controlled).
- **`prefers-reduced-motion` Fallback:** Interaction is disabled. A high-quality static image or an animated GIF of the rotating galaxy is shown instead. If an animated GIF is used, it must be pausable. Alternatively, a simple image carousel showing the galaxy from different angles.

---

### 4. Star Lifecycle (`star-lifecycle`)

- **Description:** A scroll-driven animation that transitions a central visual through the stages of a star's life, from nebula to white dwarf.
- **Technique:** **`GSAP + ScrollTrigger`**. This animation is pinned to the viewport while the user scrolls through the corresponding text. The `scrub` property links the animation progress directly to the scrollbar position. The visual could be an SVG with morphing paths, a shader with animated uniforms in `react-three-fiber`, or a sequence of cross-fading images/Lottie files.
- **Trigger:** Scroll. The animation is pinned and scrubbed as the user scrolls through the "Stars" section.
- **Easing:** `linear`, as the animation timing should directly reflect the scroll position.
- **Duration:** The animation progresses over the entire scroll height of the "Stars" section.
- **`prefers-reduced-motion` Fallback:** The scroll-driven animation is replaced with a static infographic. A series of distinct images and their corresponding text are stacked vertically. Each stage is revealed with a simple fade-in as it enters the viewport.

---

### 5. Interactive Solar System (`solar-system`)

- **Description:** A 3D model of the solar system where users can hover over planets to see their names and click to view more details.
- **Technique:** **`react-three-fiber` + `@react-three/drei`**. Use `Mesh` objects for planets, with `onPointerOver` and `onClick` events. `drei/Html` can be used to display HTML labels in the 3D scene. A camera animation can be triggered on click to focus on a planet.
- **Trigger:**
    - **Hover:** `onPointerOver` to highlight the planet and show its name.
    - **Click:** `onClick` to trigger a camera zoom/pan towards the planet and display a detailed info card.
- **Easing:** `power3.inOut` for camera animations.
- **Duration:** Camera animation: `1.5s`.
- **`prefers-reduced-motion` Fallback:** The 3D scene is replaced by a 2D responsive grid or list. Each item in the grid/list represents a planet, showing an image and the same information that would be in the pop-up card.
