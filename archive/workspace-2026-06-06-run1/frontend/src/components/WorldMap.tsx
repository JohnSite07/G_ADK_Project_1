
import React, { useState } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup,
} from 'react-simple-maps';

// URL to the world map TopoJSON file
const geoUrl =
  'https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json';

// Define the type for our marker data
interface MarkerData {
  name: string;
  coordinates: [number, number];
  link: string;
}

// Placeholder data for natural attractions
const markers: MarkerData[] = [
  { name: 'Mount Everest, Nepal', coordinates: [86.925, 27.9881], link: 'https://en.wikipedia.org/wiki/Mount_Everest' },
  { name: 'Great Barrier Reef, Australia', coordinates: [145.8, -18.2871], link: 'https://en.wikipedia.org/wiki/Great_Barrier_Reef' },
  { name: 'Iguazu Falls, Brazil/Argentina', coordinates: [-54.4367, -25.6953], link: 'https://en.wikipedia.org/wiki/Iguazu_Falls' },
  { name: 'Galápagos Islands, Ecuador', coordinates: [-90.965, -0.9538], link: 'https://en.wikipedia.org/wiki/Gal%C3%A1pagos_Islands' },
  { name: 'Serengeti National Park, Tanzania', coordinates: [34.8333, -2.3333], link: 'https://en.wikipedia.org/wiki/Serengeti_National_Park' },
];

interface WorldMapProps {
  data?: MarkerData[];
}

const WorldMap: React.FC<WorldMapProps> = ({ data = markers }) => {
  const [activeMarker, setActiveMarker] = useState<MarkerData | null>(null);

  return (
    <div className="relative w-full h-full border-2 border-gray-200 rounded-lg overflow-hidden">
      <ComposableMap
        projectionConfig={{
          scale: 155,
          rotation: [-11, 0, 0],
        }}
        className="w-full h-full bg-blue-100"
      >
        <ZoomableGroup center={[0, 20]}>
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  style={{
                    default: {
                      fill: '#E9E3DA',
                      stroke: '#A9A9A9',
                      strokeWidth: 0.5,
                      outline: 'none',
                    },
                    hover: {
                      fill: '#D4C8B5',
                      outline: 'none',
                    },
                    pressed: {
                      fill: '#C0B39E',
                      outline: 'none',
                    },
                  }}
                />
              ))
            }
          </Geographies>
          {data.map((marker) => (
            <Marker
              key={marker.name}
              coordinates={marker.coordinates}
              onClick={() => setActiveMarker(marker === activeMarker ? null : marker)}
            >
              <g
                className="cursor-pointer transition-transform duration-300 ease-out hover:scale-125"
                transform="translate(-12, -24)"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" className="fill-current text-red-500 drop-shadow-md">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  <circle cx="12" cy="9" r="2.5" className="animate-pulse" />
                </svg>
              </g>
            </Marker>
          ))}
        </ZoomableGroup>
      </ComposableMap>
      {activeMarker && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white rounded-lg shadow-lg p-4 z-10 transition-all duration-300 ease-out w-64">
            <h3 className="font-bold text-lg mb-1">{activeMarker.name}</h3>
            <a
              href={activeMarker.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 visited:text-purple-600"
            >
              Learn More
            </a>
            <button
              onClick={() => setActiveMarker(null)}
              className="absolute top-1 right-1 text-gray-500 hover:text-gray-800 text-2xl leading-none"
            >
              &times;
            </button>
        </div>
      )}
    </div>
  );
};

export default WorldMap;
