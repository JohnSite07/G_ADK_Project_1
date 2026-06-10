
import React, { useRef, useMemo, useLayoutEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Component for the Big Bang animation scene
const BigBangScene = () => {
  const pointsRef = useRef<THREE.Points>(null!);
  const materialRef = useRef<any>(null!);
  const singularityRef = useRef<THREE.Mesh>(null!);

  const particleCount = 8000;
  const radius = 75;

  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    const r = radius;
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.acos((Math.random() * 2) - 1);
      const phi = Math.random() * 2 * Math.PI;
      const r_i = Math.cbrt(Math.random()) * r;

      const x = r_i * Math.sin(theta) * Math.cos(phi);
      const y = r_i * Math.sin(theta) * Math.sin(phi);
      const z = r_i * Math.cos(theta);

      pos[i * 3] = x;
      pos[i * 3 + 1] = y;
      pos[i * 3 + 2] = z;
    }
    return pos;
  }, [particleCount, radius]);

  useLayoutEffect(() => {
    if (!pointsRef.current || !materialRef.current || !singularityRef.current) return;

    const mm = gsap.matchMedia();

    mm.add(
      {
        isFullMotion: '(prefers-reduced-motion: no-preference)',
        isReducedMotion: '(prefers-reduced-motion: reduce)',
      },
      (context) => {
        const { isFullMotion } = context.conditions as { isFullMotion: boolean };

        if (isFullMotion) {
          // Full scroll-driven animation for users without reduced motion preference
          const timeline = gsap.timeline({
            scrollTrigger: {
              trigger: '.big-bang-container',
              start: 'top top',
              end: '+=200vh',
              scrub: 1,
              pin: true,
            },
          });

          // Initial states
          gsap.set(singularityRef.current.material, { opacity: 1 });
          gsap.set(pointsRef.current.scale, { x: 0.01, y: 0.01, z: 0.01 });
          gsap.set(materialRef.current, { size: 0.1 });

          // Singularity fades and universe expands
          timeline.to(singularityRef.current.material, { opacity: 0, duration: 0.5, ease: 'power2.inOut' }, 0);
          timeline.to(pointsRef.current.scale, { x: 1, y: 1, z: 1, duration: 2, ease: 'power2.inOut' }, 0);

          // Particle size and color evolution
          const hotSoupColor = new THREE.Color('#ff9933');
          const coolStarsColor = new THREE.Color('#ffffff');
          const tweenColor = hotSoupColor.clone();
          materialRef.current.color = tweenColor;

          timeline.to(materialRef.current, { size: 20.0, duration: 1.5, ease: 'power2.inOut' }, 0);
          timeline.to(
            tweenColor,
            {
              r: coolStarsColor.r,
              g: coolStarsColor.g,
              b: coolStarsColor.b,
              duration: 2,
              ease: 'power2.inOut',
              onUpdate: () => {
                materialRef.current.color.copy(tweenColor);
              },
            },
            0.5
          );
          timeline.to(materialRef.current, { size: 0.35, duration: 2, ease: 'power2.inOut' }, 0.5);

          return () => {
            timeline.kill();
            ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
          };
        } else {
          // Fallback cross-fade animation for reduced motion
          // Set final state of particles, but hide them initially
          gsap.set(pointsRef.current.scale, { x: 1, y: 1, z: 1 });
          gsap.set(materialRef.current, { size: 0.35, opacity: 0 });
          materialRef.current.color = new THREE.Color('#ffffff');

          // Singularity starts visible
          gsap.set(singularityRef.current.material, { opacity: 1 });

          const tl = gsap.timeline();
          tl.to(singularityRef.current.material, { opacity: 0, duration: 2, ease: 'power2.inOut' }).to(
            materialRef.current,
            { opacity: 1, duration: 2, ease: 'power2.inOut' },
            '<'
          );

          return () => {
            tl.kill();
          };
        }
      }
    );

    return () => mm.revert();
  }, [positions]);

  return (
    <>
      <color attach="background" args={['black']} />
      <mesh ref={singularityRef}>
        <sphereGeometry args={[0.2, 24, 24]} />
        <meshBasicMaterial color="white" toneMapped={false} transparent />
      </mesh>
      <Points ref={pointsRef} positions={positions}>
        <PointMaterial ref={materialRef} transparent depthWrite={false} sizeAttenuation />
      </Points>
    </>
  );
};

const BigBang = () => {
  return (
    <div className="big-bang-container h-[300vh] w-full bg-black">
      <div className="sticky top-0 h-screen w-full">
        <Canvas camera={{ position: [0, 0, 100], fov: 75 }}>
          <BigBangScene />
        </Canvas>
      </div>
    </div>
  );
};

export default BigBang;
