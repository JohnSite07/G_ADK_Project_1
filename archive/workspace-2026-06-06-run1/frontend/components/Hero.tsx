
import React from 'react';

const Hero = () => {
  return (
    <div className="relative h-screen">
      <video
        className="absolute top-0 left-0 w-full h-full object-cover"
        src="/videos/hero-video.mp4"
        autoPlay
        loop
        muted
      />
      <div className="absolute inset-0 bg-black bg-opacity-50 flex flex-col justify-center items-center text-white">
        <h1 className="text-6xl font-serif">Answer the Call of the Wild.</h1>
        <p className="text-xl mt-4">Discover breathtaking natural escapes.</p>
      </div>
    </div>
  );
};

export default Hero;
