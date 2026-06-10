
import React, { useRef, useEffect, useState } from 'react';
import { Pie } from '@visx/shape';
import { Group } from '@visx/group';
import { scaleOrdinal } from '@visx/scale';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// --- Data, Types, and Colors ---
interface CosmicData {
  label: string;
  value: number;
}

const finalComposition: CosmicData[] = [
  { label: 'Visible Matter', value: 5 },
  { label: 'Dark Matter', value: 27 },
  { label: 'Dark Energy', value: 68 },
];

const colors: { [key: string]: string } = {
  'Visible Matter': 'var(--color-glow-primary)',
  'Dark Matter': 'var(--color-glow-secondary)',
  'Dark Energy': 'var(--color-glow-tertiary)',
  'Placeholder': 'transparent',
};

const getValue = (d: CosmicData) => d.value;

// --- React Component ---
const CosmicPieChart: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pieData, setPieData] = useState<CosmicData[]>([]);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // 1. Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleMediaChange = () => {
      if (mediaQuery.matches) {
        setPrefersReducedMotion(true);
        setPieData(finalComposition); // Render final state immediately
      } else {
        setPrefersReducedMotion(false);
        // Set initial animated state
        setPieData([
          { label: 'Visible Matter', value: 5 },
          { label: 'Placeholder', value: 95 },
        ]);
      }
    };

    handleMediaChange(); // Initial check
    mediaQuery.addEventListener('change', handleMediaChange);
    return () => mediaQuery.removeEventListener('change', handleMediaChange);
  }, []);

  // 2. Setup GSAP animation
  useEffect(() => {
    if (prefersReducedMotion || !containerRef.current || pieData.length === finalComposition.length) {
      return;
    }

    const animationProxy = {
      darkMatter: 0,
      darkEnergy: 0,
    };

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: containerRef.current,
        start: "top 75%", // Trigger when 75% of the element is in view
        toggleActions: "play none none none",
      },
      onUpdate: () => {
        // On each frame, update the React state to re-render the pie
        setPieData([
          { label: 'Visible Matter', value: 5 },
          { label: 'Dark Matter', value: animationProxy.darkMatter },
          { label: 'Dark Energy', value: animationProxy.darkEnergy },
          { label: 'Placeholder', value: Math.max(0, 95 - animationProxy.darkMatter - animationProxy.darkEnergy) }
        ]);
      },
      onComplete: () => {
        // Set final, clean data without placeholder
        setPieData(finalComposition);
      }
    });

    // The main animation tween
    tl.to(animationProxy, {
      darkMatter: 27,
      darkEnergy: 68,
      duration: 1.5,
      ease: "elastic.out(1, 0.5)",
    });

    // Cleanup GSAP instances on component unmount
    return () => {
      tl.scrollTrigger?.kill();
      tl.kill();
    };
  }, [prefersReducedMotion, pieData.length]);

  // SVG and Chart Dimensions
  const width = 320;
  const height = 320;
  const margin = 20;
  const radius = Math.min(width, height) / 2 - margin;
  const donutThickness = 50;

  // Ordinal color scale
  const getColor = scaleOrdinal({
    domain: finalComposition.map(d => d.label).concat(['Placeholder']),
    range: finalComposition.map(d => colors[d.label]).concat([colors['Placeholder']]),
  });

  return (
    <div ref={containerRef} className="relative flex flex-col items-center justify-center p-4 rounded-lg text-white" aria-label="Pie chart showing the composition of the universe">
      <svg width={width} height={height}>
        <Group top={height / 2} left={width / 2}>
          <Pie
            data={pieData}
            pieValue={getValue}
            outerRadius={radius}
            innerRadius={radius - donutThickness}
            padAngle={0.015}
            pieSort={null} // Important: preserve data order
          >
            {(pie) => (
              pie.arcs.map((arc, index) => {
                const arcPath = pie.path(arc) ?? '';
                const arcFill = getColor(arc.data.label) ?? 'gray';
                return (
                  <g key={`arc-${arc.data.label}-${index}`} className="pie-slice">
                    <path d={arcPath} fill={arcFill} />
                  </g>
                );
              })
            )}
          </Pie>
        </Group>
      </svg>
      <div className="mt-6 flex flex-col text-sm space-y-2 w-full px-4">
        {finalComposition.map((data) => (
          <div key={data.label} className="flex items-center">
            <div className="w-3 h-3 rounded-full mr-3" style={{ backgroundColor: colors[data.label] }} />
            <span className="text-gray-300">{data.label}:</span>
            <span className="ml-auto font-mono">{data.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CosmicPieChart;
