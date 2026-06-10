
import React, { useState, useEffect, useMemo } from 'react';

const FATES = [
  {
    id: 'freeze',
    title: 'The Big Freeze',
    description: 'The universe continues to expand, and the stars slowly burn out, leaving a cold, dark, and empty void. All thermal energy dissipates, and particles slow to a complete stop.',
  },
  {
    id: 'rip',
    title: 'The Big Rip',
    description: 'The accelerating expansion of the universe becomes so powerful it overcomes all other forces. Galaxies, stars, planets, and even atoms are torn apart one by one.',
  },
  {
    id: 'crunch',
    title: 'The Big Crunch',
    description: 'The expansion of the universe eventually reverses. Pulled by gravity, all matter collapses back into an infinitely dense, hot point, likely triggering another Big Bang.',
  },
];

const PARTICLE_COUNT = 50;

// A simple hook to check for the user's motion preference.
// Kept in this file to be self-contained.
const usePrefersReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(query.matches);
    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };
    query.addEventListener('change', listener);
    return () => query.removeEventListener('change', listener);
  }, []);
  return prefersReducedMotion;
};

const BranchingFates = () => {
  const [activeFate, setActiveFate] = useState<'freeze' | 'rip' | 'crunch' | null>(null);
  const prefersReducedMotion = usePrefersReducedMotion();

  const handleFateClick = (fateId: 'freeze' | 'rip' | 'crunch') => {
    setActiveFate(fateId);
  };

  const handleReset = () => {
    setActiveFate(null);
  };

  const particles = useMemo(() => {
    return Array.from({ length: PARTICLE_COUNT }).map((_, i) => ({
      id: i,
      size: Math.random() * 5 + 2,
      startX: Math.random() * 100,
      startY: Math.random() * 100,
      delay: Math.random() * 2,
      duration: Math.random() * 5 + 5,
    }));
  }, []);

  const selectedFateDetails = FATES.find(f => f.id === activeFate);

  return (
    <div className="w-full bg-gray-900 text-white p-8 rounded-lg flex flex-col items-center justify-center min-h-[600px]">
      <style>
        {`
          @keyframes move-randomly {
            0% { transform: translate(0, 0); }
            25% { transform: translate(calc(var(--randX) * 15px), calc(var(--randY) * 15px)); }
            50% { transform: translate(calc(var(--randY) * -10px), calc(var(--randX) * -10px)); }
            75% { transform: translate(calc(var(--randX) * 10px), calc(var(--randY) * -15px)); }
            100% { transform: translate(0, 0); }
          }
          @keyframes rip-apart {
            0% { transform: translate(0, 0) scale(1); opacity: 1; }
            100% { transform: translate(calc(var(--randX) * 2000%), calc(var(--randY) * 2000%)) scale(3); opacity: 0; }
          }
          @keyframes crunch-in {
            0% { transform: translate(calc(var(--randX) * 250px), calc(var(--randY) * 250px)) scale(1.5); opacity: 1; }
            100% { transform: translate(0, 0) scale(0); opacity: 0; }
          }
          .particle-base {
            position: absolute;
            background: white;
            border-radius: 50%;
            will-change: transform, opacity;
          }
          .animate-freeze {
            animation: move-randomly 10s infinite linear;
            animation-delay: calc(var(--delay) * 1s);
          }
          /* We add a class after a delay in JS to pause the animation */
          .animate-freeze-stopped {
            animation-play-state: paused;
          }
          .animate-rip {
            animation: rip-apart 3s forwards ease-in;
            animation-delay: 0.2s;
          }
          .animate-crunch {
            animation: crunch-in 3s forwards ease-out;
            animation-delay: 0.2s;
          }
        `}
      </style>

      <div className="w-full max-w-4xl mx-auto text-center mb-8">
        <h2 className="text-4xl md:text-5xl font-bold mb-4">Branching Fates</h2>
        <p className="text-lg text-gray-400">The end of the universe is not one story, but many. Choose a path to see one possible fate.</p>
      </div>

      <div className="relative w-full h-[400px] bg-black rounded-md overflow-hidden mb-8 border border-gray-700">
        {!activeFate && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-gray-500">Select a fate to begin</p>
          </div>
        )}
        {activeFate && (prefersReducedMotion ? (
          <div className="p-8 text-center flex flex-col items-center justify-center h-full">
            <h3 className="text-2xl font-bold mb-4">{selectedFateDetails?.title}</h3>
            <p className="max-w-prose">{selectedFateDetails?.description}</p>
          </div>
        ) : (
          <div className="absolute inset-0" id="animation-canvas">
            {particles.map(p => (
              <div
                key={p.id}
                className={`particle-base 
                  ${activeFate === 'freeze' && 'animate-freeze'} 
                  ${activeFate === 'rip' && 'animate-rip'} 
                  ${activeFate === 'crunch' && 'animate-crunch'}
                `}
                style={{
                  width: `${p.size}px`,
                  height: `${p.size}px`,
                  top: `${p.startY}%`,
                  left: `${p.startX}%`,
                  '--randX': (Math.random() - 0.5) * 2,
                  '--randY': (Math.random() - 0.5) * 2,
                  '--delay': p.delay,
                  '--duration': p.duration,
                } as React.CSSProperties}
              />
            ))}
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        {!activeFate ? (
          FATES.map(fate => (
            <button
              key={fate.id}
              onClick={() => handleFateClick(fate.id as any)}
              className="px-6 py-3 font-semibold text-lg bg-indigo-600 hover:bg-indigo-500 rounded-md transition-all duration-200 disabled:bg-gray-600 disabled:cursor-not-allowed"
            >
              {fate.title}
            </button>
          ))
        ) : (
          <div className="flex flex-col items-center gap-4">
              <div className="flex flex-row items-center justify-center gap-4">
                {FATES.map(fate => (
                    <button
                        key={fate.id}
                        onClick={() => handleFateClick(fate.id as any)}
                        disabled={!!activeFate}
                        className="px-6 py-3 font-semibold text-lg bg-indigo-600 hover:bg-indigo-500 rounded-md transition-all duration-200 disabled:bg-gray-600 disabled:cursor-not-allowed"
                    >
                        {fate.title}
                    </button>
                ))}
              </div>
            <button
              onClick={handleReset}
              className="px-6 py-2 font-semibold bg-gray-700 hover:bg-gray-600 rounded-md transition-all duration-200 mt-4"
            >
              Reset
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BranchingFates;
