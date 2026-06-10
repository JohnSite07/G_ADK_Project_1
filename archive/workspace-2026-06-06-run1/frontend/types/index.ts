
export interface Location {
  id: string;
  name: string;
  description: string;
  image: string;
}

export interface Marker {
  id: string;
  name: string;
  coordinates: [number, number];
}
