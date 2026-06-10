'use client';

import { useEffect, ReactNode } from 'react';
import { ReactLenis } from '@studio-freight/react-lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register the GSAP plugin
gsap.registerPlugin(ScrollTrigger);

interface MotionWrapperProps {
  children: ReactNode;
}

/**
 * A wrapper component that provides global motion effects:
 * 1. Smooth scrolling using Lenis.
 * 2. Scroll-triggered reveal animations for elements with the `.reveal` class.
 */
const MotionWrapper = ({ children }: MotionWrapperProps) => {
  useEffect(() => {
    // Select all elements with the .reveal class
    const revealElements = gsap.utils.toArray('.reveal');

    // Create a matchMedia instance for responsive and accessibility-friendly animations
    const mm = gsap.matchMedia();

    // Animations for users who prefer motion
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      revealElements.forEach((el) => {
        gsap.fromTo(
          el as Element,
          {
            opacity: 0,
            y: 20, // Start 20px below its final position
          },
          {
            opacity: 1,
            y: 0, // End at its final position
            duration: 0.8,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: el as Element,
              start: 'top 80%', // Trigger when the top of the element is 80% from the top of the viewport
              toggleActions: 'play none none none', // Play the animation once when it enters the viewport
            },
          }
        );
      });
    });

    // Fallback for users who prefer reduced motion
    mm.add('(prefers-reduced-motion: reduce)', () => {
      revealElements.forEach((el) => {
        // Set the elements to their final state directly, without animation
        gsap.set(el as Element, { opacity: 1, y: 0 });
      });
    });

    // Cleanup function to revert animations and kill scroll triggers on component unmount
    return () => {
      mm.revert();
    };
  }, []);

  return <ReactLenis root>{children as any}</ReactLenis>;
};

export default MotionWrapper;
