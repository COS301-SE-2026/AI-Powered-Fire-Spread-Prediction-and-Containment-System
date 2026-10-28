import dynamic from 'next/dynamic';
import { MapSkeleton } from '../ui/skeleton/MapSkeleton';

export const FireMap = dynamic(() => import('../firefighter/FireMap').then((mod) => mod.FireMap), {
  ssr: false,
  loading: () =>  <MapSkeleton />
});
