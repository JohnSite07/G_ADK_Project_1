"use client";

import * as THREE from 'three';
import React, { useRef, useMemo, useLayoutEffect, FC, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Billboard, Grid, Plane } from '@react-three/drei';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const GALAXY_COUNT = 500;
const GALAXY_CLUSTER_RADIUS = 50;

function createGalaxyTexture(): THREE.CanvasTexture | null {
  if (typeof document === 'undefined') return null;
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;

  const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
  gradient.addColorStop(0.2, 'rgba(255, 220, 180, 1)');
  gradient.addColorStop(0.5, 'rgba(255, 180, 120, 0.4)');
  gradient.addColorStop(1, 'rgba(200, 150, 100, 0)');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);

  return new THREE.CanvasTexture(canvas);
}

interface GalaxyProps {
    position: THREE.Vector3;
    initialScale: number;
    texture: THREE.CanvasTexture | null;
}

const Galaxy: FC<GalaxyProps> = ({ position, initialScale, texture }) => {
  const planeRef = useRef<THREE.Mesh>(null!);

  useFrame(() => {
    if (planeRef.current && planeRef.current.parent && planeRef.current.parent.parent) {
      const parentScale = planeRef.current.parent.parent.scale.x;
      planeRef.current.scale.setScalar(initialScale / parentScale);
    }
  });

  return (
    <Billboard position={position}>
      <Plane ref={planeRef} args={[1, 1]}>
        <meshBasicMaterial
          map={texture}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </Plane>
    </Billboard>
  );
};

interface GalaxiesProps {
    texture: THREE.CanvasTexture | null;
}

const Galaxies: FC<GalaxiesProps> = ({ texture }) => {
  const galaxies = useMemo(() => {
    const temp: { id: number; position: THREE.Vector3; initialScale: number }[] = [];
    for (let i = 0; i < GALAXY_COUNT; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      const r = Math.pow(Math.random(), 1.5) * GALAXY_CLUSTER_RADIUS;
      
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      
      const initialScale = 0.5 + Math.random() * 1.5;

      temp.push({
        id: i,
        position: new THREE.Vector3(x, y, z),
        initialScale,
      });
    }
    return temp;
  }, []);

  if (!texture) return null;

  return (
    <>
      {galaxies.map((galaxy) => (
        <Galaxy key={galaxy.id} position={galaxy.position} initialScale={galaxy.initialScale} texture={texture} />
      ))}
    </>
  );
};

const Scene = () => {
  const groupRef = useRef<THREE.Group>(null!);
  const texture = useMemo(() => createGalaxyTexture(), []);

  useLayoutEffect(() => {
    if (!groupRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        groupRef.current!.scale,
        { x: 1, y: 1, z: 1 },
        {
          x: 5, y: 5, z: 5,
          scrollTrigger: {
            trigger: '.scroll-container',
            start: 'top top',
            end: '+=150%',
            scrub: true,
            pin: true,
            anticipatePin: 1,
          },
          ease: 'none',
        }
      );
    });
    return () => ctx.revert();
  }, []);

  return (
    <>
      <group ref={groupRef}>
        <Galaxies texture={texture} />
        <Grid
          infiniteGrid
          sectionSize={10}
          sectionColor={"#404040"}
          fadeDistance={150}
          fadeStrength={1}
        />
      </group>
    </>
  );
};

const ReducedMotionFallback = () => (
    <div className="w-full h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center p-8 border border-gray-700 rounded-lg">
            <h2 className="text-2xl md:text-4xl font-bold mb-2">The Expansion of Space</h2>
            <p className="text-sm md:text-base max-w-prose">
                The animation of galaxies expanding has been disabled due to your browser's
                prefers-reduced-motion setting. This scene demonstrates how spacetime itself
                stretches, causing galaxies to move away from each other.
            </p>
        </div>
    </div>
);

const GalaxyCluster = () => {
    const [isReducedMotion, setIsReducedMotion] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useLayoutEffect(() => {
        const ctx = gsap.context(() => {
            const mm = gsap.matchMedia();
            mm.add(
                {
                    isReduced: '(prefers-reduced-motion: reduce)',
                    isNotReduced: '(prefers-reduced-motion: no-preference)',
                },
                (context) => {
                    const { isReduced } = context.conditions as { isReduced: boolean };
                    setIsReducedMotion(isReduced);
                }
            );
        }, containerRef);
        return () => ctx.revert();
    }, []);

    if (isReducedMotion) {
        return <ReducedMotionFallback />;
    }

  return (
    <div ref={containerRef} className="scroll-container relative w-full h-[250vh] bg-black touch-none">
      <div className="sticky top-0 h-screen w-full">
        <Canvas
          gl={{ antialias: true, pixelRatio: (typeof window !== 'undefined') ? Math.min(2, window.devicePixelRatio) : 1 } as any}
          camera={{ position: [0, 0, 80], fov: 75 }}
        >
          <color attach="background" args={['#000000']} />
          <Scene />
        </Canvas>
      </div>
      <div className="absolute top-[45%] left-1/2 -translate-x-1/2 -translate-y-1/2 text-white text-center p-4 rounded-lg pointer-events-none">
        <h2 className="text-2xl md:text-4xl font-bold mb-2">The Fabric of Spacetime</h2>
        <p className="text-sm md:text-base">Scroll down to see space itself expand.</p>
      </div>
    </div>
  );
};

export default GalaxyCluster;
