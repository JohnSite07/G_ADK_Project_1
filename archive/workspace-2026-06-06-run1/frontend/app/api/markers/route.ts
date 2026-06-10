
import { NextResponse } from 'next/server';
import type { Marker } from '@/types';

const markers: Marker[] = [
  { id: '1', name: "Buenos Aires", coordinates: [-58.3816, -34.6037] },
  { id: '2', name: "La Paz", coordinates: [-68.1193, -16.4897] },
  { id: '3', name: "Brasilia", coordinates: [-47.8825, -15.7942] },
  { id: '4', name: "Santiago", coordinates: [-70.6693, -33.4489] },
  { id: '5', name: "Bogota", coordinates: [-74.0721, 4.7110] },
  { id: '6', name: "Quito", coordinates: [-78.4678, -0.1807] },
  { id: '7', name: "Georgetown", coordinates: [-58.1551, 6.8013] },
  { id: '8', name: "Asuncion", coordinates: [-57.5759, -25.2637] },
  { id: '9', name: "Paramaribo", coordinates: [-55.2038, 5.8520] },
  { id: '10', name: "Montevideo", coordinates: [-56.1645, -34.9011] },
  { id: '11', name: "Caracas", coordinates: [-66.9036, 10.4806] },
  { id: '12', name: "Lima", coordinates: [-77.0428, -12.0464] }
];

export async function GET() {
  return NextResponse.json(markers);
}
