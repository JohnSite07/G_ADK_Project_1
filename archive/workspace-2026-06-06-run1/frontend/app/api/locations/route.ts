
import { NextResponse } from 'next/server';
import type { Location } from '@/types';

const locations: Location[] = [
  {
    id: '1',
    name: 'Whispering Pines Forest',
    description: 'A tranquil escape into a world of towering trees and soft, mossy ground.',
    image: '/images/forest.jpg',
  },
  {
    id: '2',
    name: 'Crystal Creek Lake',
    description: 'Pristine waters reflecting the endless sky, perfect for a quiet paddle.',
    image: '/images/lake.jpg',
  },
  {
    id: '3',
    name: 'Crimson Peak Mountains',
    description: 'Challenge yourself with a rewarding hike to breathtaking vistas.',
    image: '/images/mountains.jpg',
  },
];

export async function GET() {
  return NextResponse.json(locations);
}
