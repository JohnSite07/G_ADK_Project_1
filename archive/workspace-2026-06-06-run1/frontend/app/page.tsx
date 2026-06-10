
import Hero from "@/components/Hero";
import FeaturedLocations from "@/components/FeaturedLocations";
import InteractiveMap from "@/components/InteractiveMap";
import CTA from "@/components/CTA";

export default function Home() {
  return (
    <main>
      <Hero />
      <FeaturedLocations />
      <InteractiveMap />
      <CTA />
    </main>
  );
}
