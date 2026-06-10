
# QA Report for "An Interactive Guide to the Universe"

**Decision: REJECTED**

The build was successful, but a review against the project specifications (`spec.md`, `motion-spec.md`) has revealed two high-priority (P1) accessibility issues and several lower-priority technical debt items. The site cannot be approved until the P1 issues are resolved.

---

## P0 (Blocker) Issues

*None.*

## P1 (High) Issues

### 1. Missing Reduced Motion Fallback in Big Bang Animation

*   **File:** `frontend/components/BigBang.tsx`
*   **Problem:** The component does not respect the user's `prefers-reduced-motion` setting. It plays the full, scroll-driven 3D animation for all users, which can be an accessibility issue. The motion spec explicitly requires a cross-fade fallback.
*   **Fix:** Use `gsap.matchMedia()` to detect the user's preference. Keep the existing animation for `(prefers-reduced-motion: no-preference)`. For `(prefers-reduced-motion: reduce)`, implement a simple alternative, such as cross-fading between a "point" image and a "starfield" image, or simply displaying the final starfield.

### 2. Missing Reduced Motion Fallback in Galaxy Cluster Animation

*   **File:** `frontend/components/GalaxyCluster.tsx`
*   **Problem:** Similar to the Big Bang component, the 3D galaxy cluster animation plays for all users, ignoring the `prefers-reduced-motion` setting. The motion spec requires a pre-rendered video or static images as a fallback.
*   **Fix:** Use `gsap.matchMedia()`. In the `(prefers-reduced-motion: reduce)` block, return a simple component that renders a placeholder `<div>` or an `<img>` tag instead of the `Canvas` component.

---

## P2 (Medium) Issues

### 1. Type-Checking Disabled in `GalaxyCluster.tsx`

*   **File:** `frontend/components/GalaxyCluster.tsx`
*   **Problem:** The file uses `// @ts-nocheck` to bypass a build error. This suppresses all type-checking and creates technical debt.
*   **Fix:** Remove `// @ts-nocheck`. The original error was `Object literal may only specify known properties, and 'pixelRatio' does not exist in type 'GLProps'`. The prop is valid, but the type definition is likely incorrect due to dependency mismatches. Cast the `gl` prop object to `any` as a more targeted temporary fix: `gl={{ antialias: true, pixelRatio: ... } as any}`. The long-term fix is to resolve the package dependency conflicts.

### 2. Type Cast Workaround in `MotionWrapper.tsx`

*   **File:** `frontend/components/MotionWrapper.tsx`
*   **Problem:** The `children` prop is cast to `any` (`children as any`) to work around a `React.ReactNode` type incompatibility with the `@studio-freight/react-lenis` library. This is also technical debt resulting from dependency conflicts.
*   **Fix:** This is a known issue from the build process. While not a blocker, it should be documented and addressed in the future, ideally by upgrading dependencies (e.g. `react-lenis` has been renamed to `lenis`) and resolving the peer dependency conflicts that necessitated `npm install --legacy-peer-deps`.
