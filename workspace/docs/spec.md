# Build Spec: "An Interactive Guide to the Universe"

## 1. Goal, Audience, and Success Criteria

*   **Goal:** To create a visually stunning, narrative-driven, and interactive single-page website that introduces fundamental concepts of cosmology to a general audience. The site should prioritize engagement and wonder over dense academic detail.
*   **Audience:** "Curious Learners" — individuals with a general interest in science, space, and technology, but without a formal background in astrophysics. They are looking for an accessible, engaging, and memorable learning experience.
*   **Success Criteria:**
    *   **Engagement:** Average time on page exceeds 5 minutes.
    *   **Completion:** Over 80% of users scroll to the final section of the narrative.
    *   **Sharing:** The site is shared on social media, design forums, and educational platforms as an example of great interactive content.

## 2. Sitemap & Content Outline

The site will be a single, vertically-scrolling page. Each scroll transition will guide the user through the next phase of the cosmic story.

*   **Section 1: The Overture**
    *   **Content:** A black screen with a single, glowing point of energy. Headline: "It all started from a single point." A brief, poetic intro about the Big Bang.
*   **Section 2: The Expansion**
    *   **Content:** The universe of stars and galaxies. Headline: "The Universe is expanding." A simple explanation of the expansion of spacetime, using the analogy of a loaf of raisin bread.
*   **Section 3: The First Light**
    *   **Content:** A screen that looks like static. Headline: "An echo of creation is all around us." An introduction to the Cosmic Microwave Background (CMB) as the "afterglow" of the Big Bang.
*   **Section 4: The Dark Universe**
    *   **Content:** A visualization of a galaxy. Headline: "There's more than meets the eye." An introduction to the concepts of Dark Matter and Dark Energy, the invisible forces that shape our cosmos.
*   **Section 5: The End of Everything**
    *   **Content:** A branching narrative point. Headline: "How will it all end?" A brief overview of the leading theories on the ultimate fate of the universe.
*   **Section 6: Explore Further**
    *   **Content:** A simple, clean section with links to reputable sources (NASA, ESA, academic sites), and credits for the data and tools used to build the site.

## 3. Interaction Inventory

Each section will feature a primary, scroll-driven interaction designed to visually explain its core concept.

1.  **The Big Bang Animation (Section 1):**
    *   **Interaction:** As the user scrolls down from the black screen, the single point of light violently expands, filling the screen with a hot, dense "soup" of particles. Continued scrolling causes this soup to cool and resolve into a field of stars and early galaxies.
    *   **What it Conveys:** The origin of the universe from a singularity and its rapid inflation and cooling.

2.  **3D Galaxy Cluster (Section 2):**
    *   **Interaction:** A 3D scene depicting a cluster of galaxies. As the user scrolls, the galaxies themselves don't grow, but the space between them expands, carrying them away from each other. A "ruler" overlay could appear to show the metric of space itself stretching.
    *   **What it Conveys:** The fundamental concept that space itself is expanding, not that objects are flying apart through static space.

3.  **CMB Data Visualization (Section 3):**
    *   **Interaction:** The screen starts as flickering "TV static." As the user scrolls, the static resolves into the iconic, colorful WMAP/Planck map of the CMB. The user can hover or click on different colored "hot" and "cold" spots to see tooltips explaining that these tiny temperature fluctuations were the seeds of all modern structure.
    *   **What it Conveys:** The CMB is real, observable data, and it contains the blueprint for the universe we see today.

4.  **Animated Cosmic Pie Chart (Section 4):**
    *   **Interaction:** A pie chart appears, showing "Visible Matter (5%)." As the user scrolls, two more slices dramatically animate into view, pushing the visible matter slice to a sliver: "Dark Matter (27%)" and "Dark Energy (68%)."
    *   **What it Conveys:** The shocking and counter-intuitive realization that everything we can see is a tiny fraction of what the universe is made of.

5.  **Branching Fate Animations (Section 5):**
    *   **Interaction:** The scroll journey pauses. Three buttons appear, labeled "The Big Freeze," "The Big Rip," and "The Big Crunch." Clicking a button plays a short, stylized 2D animation visualizing that potential fate.
    *   **What it Conveys:** The main scientific theories about the end of the universe, providing a sense of agency and a memorable conclusion to the journey.

## 4. Non-Functional Needs

*   **Performance:**
    *   **Load Time:** Initial load time under 3 seconds on a standard 4G connection.
    *   **Animation Smoothness:** All scroll-driven animations must maintain a consistent 60 frames per second.
    *   **Asset Optimization:** All images, 3D models, and videos must be compressed and optimized for web delivery.
*   **Accessibility:**
    *   **Keyboard Navigation:** The entire scroll-based narrative must be controllable via keyboard (arrow keys/spacebar).
    *   **Screen Readers:** All textual content must be readable, and all non-text content (animations, visualizations) must have descriptive `aria-label` attributes or fallback text.
    *   **Color Contrast:** Text must meet WCAG AA contrast standards.
*   **SEO:**
    *   The site must have a well-formed `<title>` tag and `<meta name="description">` to ensure it presents well in search results and when shared.
    *   A sitemap.xml should be provided to search engines.
*   **Device Support:**
    *   The experience should be fully responsive and functional on all modern web browsers (Chrome, Firefox, Safari, Edge) on both desktop and mobile devices.
    *   On mobile, complex 3D scenes may be replaced with pre-rendered video animations to ensure smooth performance.
