import dynamic from 'next/dynamic';
import { MapSkeleton } from '../ui/skeleton/MapSkeleton';

export const FireMap = dynamic(() => import('../reportfire/Firemap').then((mod) => mod.FireMap), {
  ssr: false,
  loading: () => <MapSkeleton />,
});
