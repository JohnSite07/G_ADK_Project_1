
import React from 'react';

const locations = [
  {
    name: 'Whispering Pines Forest',
    description: 'A tranquil escape into a world of towering trees and soft, mossy ground.',
    image: '/images/forest.jpg',
  },
  {
    name: 'Crystal Creek Lake',
    description: 'Pristine waters reflecting the endless sky, perfect for a quiet paddle.',
    image: '/images/lake.jpg',
  },
  {
    name: 'Crimson Peak Mountains',
    description: 'Challenge yourself with a rewarding hike to breathtaking vistas.',
    image: '/images/mountains.jpg',
  },
];

const FeaturedLocations = () => {
  return (
    <div className="py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-serif text-center mb-12">Featured Locations</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {locations.map((location, index) => (
            <div key={index} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <img src={location.image} alt={location.name} className="w-full h-64 object-cover" />
              <div className="p-6">
                <h3 className="text-2xl font-serif mb-2">{location.name}</h3>
                <p className="text-text-muted mb-4">{location.description}</p>
                <button className="px-6 py-2 bg-primary text-white rounded-full">Discover</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeaturedLocations;
