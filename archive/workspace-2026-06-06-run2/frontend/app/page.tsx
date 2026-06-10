
import HeroStarfield from "@/components/HeroStarfield";
import BigBangExpansion from "@/components/BigBangExpansion";
import GalaxyViewer from "@/components/GalaxyViewer";
import StarLifecycle from "@/components/StarLifecycle";
import SolarSystem from "@/components/SolarSystem";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <section id="hero" className="h-screen w-full relative">
        <HeroStarfield />
        <div className="mx-auto max-w-6xl px-4 h-full flex flex-col justify-center relative z-10">
          <h1 className="text-7xl font-bold text-text-primary">The Story of Everything</h1>
          <p className="text-xl font-light text-text-secondary mt-4">A journey from the beginning of the universe to the worlds we know.</p>
        </div>
      </section>

      <section id="big-bang" className="h-screen w-full">
        <div className="mx-auto max-w-6xl px-4 h-full flex items-center justify-center">
          <div className="w-1/2">
            <h2 className="text-5xl font-bold text-text-primary mb-8">In the Beginning...</h2>
            <p className="text-lg text-text-secondary">The universe started from a hot, dense point. Its rapid expansion, inflation, and subsequent cooling allowed the first atoms to form.</p>
          </div>
          <div className="w-1/2 flex items-center justify-center">
            <BigBangExpansion />
          </div>
        </div>
      </section>

      <section id="galaxies" className="h-screen w-full flex flex-col items-center justify-center text-center">
        <h2 className="text-5xl font-bold text-text-primary mb-4">Islands of Stars</h2>
        <p className="text-lg text-text-secondary max-w-3xl mb-8">Gravity formed the first galaxies. We'll explore the main types and our home, the Milky Way.</p>
        <GalaxyViewer />
      </section>

      <section id="stars" className="h-[300vh] w-full relative">
        <div className="sticky top-0 h-screen flex flex-col items-center justify-center text-center">
          <h2 className="text-5xl font-bold text-text-primary mb-4">Cosmic Engines</h2>
          <p className="text-lg text-text-secondary max-w-3xl mb-8">A star's lifecycle: from a nebula's birth to its death as a white dwarf, neutron star, or black hole.</p>
          <StarLifecycle />
        </div>
      </section>

      <section id="planets" className="h-screen w-full flex flex-col items-center justify-center text-center">
        <h2 className="text-5xl font-bold text-text-primary mb-4">Worlds Beyond Our Own</h2>
        <p className="text-lg text-text-secondary max-w-3xl mb-8">A look at our Solar System and the search for exoplanets.</p>
        <SolarSystem />
      </section>

      <footer className="w-full bg-surface py-12">
        <div className="mx-auto max-w-6xl px-4 text-center text-text-muted">
          <p className="text-lg">The story is still being written.</p>
        </div>
      </footer>
    </main>
  );
}
