
"use client";

import React, { useLayoutEffect, useRef, useState, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface CMBVisualizationProps {
  imageUrl?: string;
  hotspots?: Hotspot[];
}

interface Hotspot {
  x: number; // percentage
  y: number; // percentage
  title: string;
  description: string;
}

const defaultHotspots: Hotspot[] = [
  { x: 50, y: 50, title: "Cold Spot", description: "An unusually large and cold area in the CMB. Its origin is still a subject of debate among cosmologists." },
  { x: 25, y: 30, title: "Galaxy Cluster", description: "A foreground signal from a massive galaxy cluster, demonstrating the Sunyaev-Zel'dovich effect." },
  { x: 70, y: 65, title: "CMB Asymmetry", description: "The slight temperature difference between the two hemispheres of the CMB, suggesting large-scale structural anomalies." },
];

const CMBVisualization: React.FC<CMBVisualizationProps> = ({
  imageUrl = "https://wmap.gsfc.nasa.gov/media/1010/1010_TT_4096.png",
  hotspots = defaultHotspots,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hotspotsRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setIsReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "Anonymous"; // Required for canvas operations on images from other domains
    img.src = imageUrl;
    img.onload = () => {
      imageRef.current = img;
      setIsImageLoaded(true);
    };
    img.onerror = () => {
      console.error("Failed to load image.");
    };
  }, [imageUrl]);

  useLayoutEffect(() => {
    if (!isImageLoaded || !canvasRef.current || !containerRef.current || !hotspotsRef.current) return;
    
    const image = imageRef.current;
    if (!image) return;

    const canvas = canvasRef.current;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    if (!context) return;

    let { width, height } = containerRef.current.getBoundingClientRect();
    canvas.width = width;
    canvas.height = height;

    const pixelation = { value: isReducedMotion ? 1 : 80 };

    const draw = (pixelSize: number) => {
      if (!image) return;
      const size = Math.max(1, Math.floor(pixelSize));
      
      const imgWidth = image.width;
      const imgHeight = image.height;
      
      // Maintain aspect ratio
      const canvasAspect = canvas.width / canvas.height;
      const imgAspect = imgWidth / imgHeight;
      let drawWidth, drawHeight, offsetX, offsetY;

      if (canvasAspect > imgAspect) {
        drawHeight = canvas.height;
        drawWidth = drawHeight * imgAspect;
        offsetX = (canvas.width - drawWidth) / 2;
        offsetY = 0;
      } else {
        drawWidth = canvas.width;
        drawHeight = drawWidth / imgAspect;
        offsetX = 0;
        offsetY = (canvas.height - drawHeight) / 2;
      }

      context.clearRect(0, 0, canvas.width, canvas.height);
      
      if (size === 1) {
        context.drawImage(image, offsetX, offsetY, drawWidth, drawHeight);
        return;
      }
      
      // This is a simplified approach for demonstration. A more performant version
      // would use an offscreen canvas to sample colors.
      context.drawImage(image, 0, 0, 1, 1); // Ensure image data is available for getImageData
      context.drawImage(image, offsetX, offsetY, drawWidth, drawHeight);

      for (let y = 0; y < drawHeight; y += size) {
        for (let x = 0; x < drawWidth; x += size) {
          const canvasX = Math.floor(offsetX + x);
          const canvasY = Math.floor(offsetY + y);
          const pixel = context.getImageData(canvasX, canvasY, 1, 1).data;
          context.fillStyle = `rgba(${pixel[0]}, ${pixel[1]}, ${pixel[2]}, ${pixel[3] / 255})`;
          context.fillRect(canvasX, canvasY, size, size);
        }
      }
    };

    draw(pixelation.value);

    if (isReducedMotion) {
      gsap.to(hotspotsRef.current, { autoAlpha: 1, duration: 0.5 });
      return;
    }

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top top',
        end: '+=100%',
        pin: true,
        scrub: true,
        anticipatePin: 1,
      },
    });

    tl.to(pixelation, {
      value: 1,
      ease: 'sine.out',
      onUpdate: () => draw(pixelation.value),
    })
    .to(hotspotsRef.current, {
      autoAlpha: 1,
      duration: 0.3,
    }, '-=0.3'); // Fade in hotspots towards the end of the scroll

    return () => {
      tl.kill();
      ScrollTrigger.getAll().forEach(st => st.kill());
    };

  }, [isImageLoaded, isReducedMotion]);

  return (
    <section ref={containerRef} className="relative w-full h-screen bg-black">
      <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full" />
      <div ref={hotspotsRef} className="absolute top-0 left-0 w-full h-full opacity-0">
        {hotspots.map((spot, index) => (
          <div
            key={index}
            className="absolute group"
            style={{ left: `${spot.x}%`, top: `${spot.y}%` }}
          >
            <div className="w-3 h-3 bg-cyan-400 rounded-full cursor-pointer transition-transform duration-300 group-hover:scale-150" />
            <div className="absolute bottom-full mb-2 w-64 p-3 bg-gray-900 bg-opacity-80 text-white rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none -translate-x-1/2 left-1/2">
              <h4 className="font-bold text-cyan-400">{spot.title}</h4>
              <p className="text-sm text-gray-300">{spot.description}</p>
              <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-x-8 border-x-transparent border-t-[8px] border-t-gray-900/80"></div>
            </div>
          </div>
        ))}
      </div>
      {!isImageLoaded && (
         <div className="absolute inset-0 flex items-center justify-center bg-black text-white">
            <p>Loading Visualization...</p>
         </div>
      )}
    </section>
  );
};

export default CMBVisualization;
