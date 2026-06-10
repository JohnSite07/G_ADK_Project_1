'use client';

import React from 'react';
import BigBang from '@/components/BigBang';
import GalaxyCluster from '@/components/GalaxyCluster';
import CMBVisualization from '@/components/CMBVisualization';
import CosmicPieChart from '@/components/CosmicPieChart';
import BranchingFates from '@/components/BranchingFates';
import MotionWrapper from '@/components/MotionWrapper';

// A reusable section component for consistent layout
const Section: React.FC<{ title: string; subtitle: string; children: React.ReactNode }> = ({ title, subtitle, children }) => (
  <section className="min-h-screen w-full flex flex-col justify-center items-center py-20 px-4 md:px-8">
    <div className="max-w-4xl text-center mb-12">
      <h2 className="text-4xl md:text-5xl font-bold text-text-primary reveal">{title}</h2>
      <p className="text-lg md:text-xl text-text-secondary mt-4 reveal">{subtitle}</p>
    </div>
    <div className="w-full flex justify-center items-center">
      {children}
    </div>
  </section>
);

export default function Home() {
  return (
    <MotionWrapper>
      <main>
        {/* Section 1: The Overture - The BigBang component handles its own text inside the canvas */}
        <BigBang />

        {/* Section 2: The Expansion */}
        <Section
          title="The Universe is Expanding"
          subtitle="Space itself is stretching, carrying galaxies along for the ride, like raisins in a baking loaf of bread."
        >
          <GalaxyCluster />
        </Section>

        {/* Section 3: The First Light */}
        <Section
          title="An Echo of Creation"
          subtitle="The Cosmic Microwave Background is the afterglow of the Big Bang, visible in every direction."
        >
          <div className="w-full h-[500px] reveal">
            <CMBVisualization />
          </div>
        </Section>

        {/* Section 4: The Dark Universe */}
        <Section
          title="There's More Than Meets the Eye"
          subtitle="Everything we can see makes up only a tiny fraction of the universe."
        >
          <div className="reveal">
            <CosmicPieChart />
          </div>
        </Section>

        {/* Section 5: The End of Everything */}
        <Section
          title="How Will It All End?"
          subtitle="There are several leading theories for the ultimate fate of our universe. Explore the possibilities."
        >
          <div className="w-full max-w-4xl reveal">
            <BranchingFates />
          </div>
        </Section>

        {/* Section 6: Explore Further */}
        <section className="min-h-screen w-full flex flex-col justify-center items-center py-20 px-4 md:px-8 text-center">
           <div className="max-w-2xl">
            <h2 className="text-4xl md:text-5xl font-bold text-text-primary reveal">Explore Further</h2>
            <p className="text-lg text-text-secondary mt-4 reveal">
              This project is a creative work inspired by the wonders of cosmology. For scientifically rigorous information, please visit these reputable sources.
            </p>
            <div className="flex justify-center gap-6 mt-8 reveal">
              <a href="https://science.nasa.gov/astrophysics/" target="_blank" rel="noopener noreferrer" className="text-text-accent hover:text-text-primary transition-colors">NASA Astrophysics</a>
              <a href="https://www.esa.int/Science_Exploration/Space_Science" target="_blank" rel="noopener noreferrer" className="text-text-accent hover:text-text-primary transition-colors">ESA Science</a>
            </div>
             <p className="text-xs text-text-secondary mt-12 reveal">
                Built with Next.js, React, Tailwind CSS, GSAP, Three.js, and Visx.
            </p>
           </div>
        </section>

      </main>
    </MotionWrapper>
  );
}
