
# QA Review Report

## 1. Summary

The initial QA review reveals several **blocking issues** that prevent the application from being built or deployed. The `npm run build` command fails, and the CI/CD pipeline is incorrectly configured.

Beyond these blockers, there are significant gaps between the current implementation and the product specification, particularly concerning the core interactive features, performance, and accessibility. The project is not ready for a staging deployment.

---

## 2. Prioritized Issues

### P0: Blocker - Build Failure

*   **Issue:** The application fails to build. The `npm run build` command exits with an error: `Module not found: Can't resolve 'prop-types'`.
*   **Analysis:** This is a missing dependency required by `react-simple-maps`. The use of the `--legacy-peer-deps` flag during installation likely masked this missing requirement, leading to a build-time failure.
*   **Fix:** Install the missing dependency by running `npm install prop-types` in the `frontend` directory.

### P0: Blocker - Invalid CI/CD Configuration

*   **Issue:** The GitHub Actions workflow in `.github/workflows/ci-cd.yml` is fundamentally broken and will fail.
*   **Analysis:**
    1.  **No Dockerfile:** The workflow attempts to build and publish a Docker image (`docker build ...`) from the `frontend` directory but no `Dockerfile` exists in the repository.
    2.  **Incorrect Deployment Strategy:** The workflow tries to deploy the frontend to a Google Cloud Storage bucket for static hosting, but the project is a dynamic Next.js application containing API routes. A static export (`next export`) is not appropriate. The entire application should be deployed as a single server-side container to Cloud Run.
*   **Fix:**
    1.  Create a `Dockerfile` in the `frontend` directory that properly builds and runs the Next.js application.
    2.  Remove the `Deploy Frontend to GCS` step from the CI/CD workflow.
    3.  Ensure the `Build and Push Docker Image` and `Deploy Backend to Cloud Run` steps correctly build and deploy the entire Next.js application as a single service.

### P1: High - Core Interaction Features Missing

*   **Issue:** None of the key animations and interactions defined in `docs/spec.md` are implemented. This is a major deviation from the core "feel" of the product.
*   **Analysis:**
    *   The hero section lacks the **parallax scroll effect**.
    *   The **Featured Locations** section does not have the "fade-in and slide-up" reveal animation.
    *   The **Interactive Map pins** do not have the "subtle pulse animation" or the "scale up" on hover/click.
*   **Fix:** Implement these interactions. This can be done with CSS animations or a library like `framer-motion`. Handlers for `prefers-reduced-motion` must be included.

### P1: High - Interactive Map is Incomplete

*   **Issue:** The map is not interactive as specified. Users cannot click on pins to get more information.
*   **Analysis:** The `WorldMap.tsx` component renders markers with static text but lacks click handlers or a mechanism to display a pop-up/info card.
*   **Fix:** Add state and click event handlers to the map markers. On click, render an info card component with the location's name and a link, as required by the spec.

### P1: High - Performance & Asset Risks

*   **Issue:** The project has significant, unaddressed performance risks.
*   **Analysis:**
    1.  **Missing Assets:** The hero video (`/videos/hero-video.mp4`) and all location images (`/images/*.jpg`) are referenced but do not exist in the repository. Unoptimized, they will violate the 3MB page weight limit.
    2.  **External Dependencies:** The map's topology JSON is fetched from `raw.githubusercontent.com` on every load. This is unreliable and slow.
*   **Fix:**
    1.  Add compressed and optimized video and image files to the `public` directory.
    2.  Download the `world-110m.json` file and serve it locally from the `public` directory.

### P2: Medium - Accessibility Gaps

*   **Issue:** The site does not meet the WCAG 2.1 AA requirements from the spec.
*   **Analysis:**
    *   The map markers are not keyboard-focusable or navigable.
    *   The hero `<video>` is missing a `<track>` element for subtitles or descriptions for non-hearing users.
*   **Fix:** Make map markers focusable and interactive via the keyboard. Add appropriate ARIA attributes. Provide a text-based alternative to the map. Add a captions track to the video.
