
import React from 'react';
import WorldMap from './WorldMap';

const InteractiveMap = () => {
  return (
    <div className="py-20 bg-surface">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-serif text-center mb-12">Find Your Next Adventure</h2>
        <div className="bg-white rounded-lg shadow-lg h-96">
          <WorldMap />
        </div>
      </div>
    </div>
  );
};

export default InteractiveMap;
