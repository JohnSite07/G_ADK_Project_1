
import React from 'react';
import WorldMap from './components/WorldMap';

function App() {
  return (
    <div className="bg-gray-100 min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-6xl h-[600px] bg-white rounded-xl shadow-2xl p-6">
        <h1 className="text-3xl font-bold text-center mb-4 text-gray-800">
          Key Natural Attractions of the World
        </h1>
        <p className="text-center text-gray-600 mb-6">
          Click on the pins to learn more about these amazing locations.
        </p>
        <WorldMap />
      </div>
    </div>
  );
}

export default App;
