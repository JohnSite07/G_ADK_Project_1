
'use client';

import * as THREE from 'three';
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Line } from '@react-three/drei';

interface PlanetProps {
  position: [number, number, number];
  color: string;
  size: number;
  onClick: () => void;
  orbitRadius: number;
  orbitSpeed: number;
}

const Planet: React.FC<PlanetProps> = ({
  position,
  color,
  size,
  onClick,
  orbitRadius,
  orbitSpeed,
}) => {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame(({ clock }) => {
    const elapsedTime = clock.getElapsedTime();
    const angle = elapsedTime * orbitSpeed;
    const x = Math.cos(angle) * orbitRadius;
    const z = Math.sin(angle) * orbitRadius;
    if (meshRef.current) {
        meshRef.current.position.x = x;
        meshRef.current.position.z = z;
    }
  });

  return (
    <mesh ref={meshRef} onClick={onClick} position={position}>
      <sphereGeometry args={[size, 32, 32]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
};

const Sun = () => {
    return (
        <mesh>
            <sphereGeometry args={[2, 32, 32]} />
            <meshBasicMaterial color="yellow" />
            <pointLight intensity={100} decay={0.1} />
        </mesh>
    )
}

interface OrbitLineProps {
    radius: number;
}

const OrbitLine: React.FC<OrbitLineProps> = ({ radius }) => {
    const points = [];
    for (let i = 0; i < 64; i++) {
        const angle = (i / 64) * 2 * Math.PI;
        const x = radius * Math.cos(angle);
        const z = radius * Math.sin(angle);
        points.push(new THREE.Vector3(x, 0, z));
    }
    points.push(points[0]);

    return(
        <Line points={points} color="#333333" lineWidth={1} />
    )
}


export const SolarSystem = () => {
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);

  const handlePlanetClick = (planetName: string) => {
    setSelectedPlanet(planetName);
    console.log(`Clicked on ${planetName}`);
  };

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <Canvas camera={{ position: [0, 20, 50], fov: 45 }}>
        <ambientLight intensity={0.1} />
        <Sun/>
        <Planet
          position={[5, 0, 0]}
          color="orange"
          size={0.5}
          onClick={() => handlePlanetClick('Mercury')}
          orbitRadius={5}
          orbitSpeed={0.5}
        />
        <OrbitLine radius={5} />
        <Planet
          position={[10, 0, 0]}
          color="tan"
          size={0.8}
          onClick={() => handlePlanetClick('Venus')}
          orbitRadius={10}
          orbitSpeed={0.35}
        />
        <OrbitLine radius={10} />
        <Planet
          position={[15, 0, 0]}
          color="blue"
          size={1}
          onClick={() => handlePlanetClick('Earth')}
          orbitRadius={15}
          orbitSpeed={0.2}
        />
        <OrbitLine radius={15} />

        <Planet
          position={[20, 0, 0]}
          color="red"
          size={0.7}
          onClick={() => handlePlanetClick('Mars')}
          orbitRadius={20}
          orbitSpeed={0.15}
        />
        <OrbitLine radius={20} />
        <Stars
          radius={100}
          depth={50}
          count={5000}
          factor={4}
          saturation={0}
          fade
        />
        <OrbitControls />
      </Canvas>
      {selectedPlanet && (
        <div style={{ position: 'absolute', top: '10px', left: '10px', color: 'white', backgroundColor: 'rgba(0,0,0,0.5)', padding: '10px', borderRadius: '5px' }}>
            Selected: {selectedPlanet}
        </div>
      )}
    </div>
  );
};

export default SolarSystem;
