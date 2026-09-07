import {
  Wind,
  Thermometer,
  Flame,
  Droplets,
  FileWarning,
  PenLine,
  TrendingUp,
  ClipboardPlus,
} from 'lucide-react';
import { ComponentsGroup, Labled } from './componentsGroup';
import { NearbyReports } from '../firefighter/nearbyReports';
import { StatCard } from '../firefighter/StatCard';
import { ActionCard } from '../firefighter/actionCard';
import { MapStatsOverlay } from '../firefighter/mapStat';
import { NearbyFire } from '../../types/FirefighterDashboard';

export function EnvironmentCards() {
  return (
    <div className="flex flex-wrap items-start gap-19">
      <ComponentsGroup title="Environment Stat Cards">
        <div className="grid grid-cols-2 gap-3 w-80">
          <StatCard icon={<Wind />} label="Wind NE" value="14 km/h" />
          <StatCard icon={<Thermometer />} label="Temperature" value="29°C" />
          <StatCard icon={<Flame />} label="Fire Danger" value="High" />
          <StatCard icon={<Droplets />} label="Humidity" value="38%" />
        </div>
      </ComponentsGroup>
    </div>
  );
}

export function ActionCards() {
  return (
    <ComponentsGroup title="Quick Action Cards">
      <div className="grid grid-cols-2 gap-3 w-96">
        <ActionCard
          icon={<ClipboardPlus />}
          title="View all reports"
          description="View team on map"
          onClick={() => {}}
        />
        <ActionCard
          icon={<FileWarning />}
          title="Report a fire"
          description="New fire location"
          onClick={() => {}}
        />
        <ActionCard
          icon={<PenLine />}
          title="Log containment line"
          description="Draw live on map"
          onClick={() => {}}
        />
        <ActionCard
          icon={<TrendingUp />}
          title="Simulate fires"
          description="View AI prediction"
          onClick={() => {}}
        />
      </div>
    </ComponentsGroup>
  );
}

const dummyFires: NearbyFire[] = [
  { location_text: 'Moreleta Park', distance: 2.4, time_ago: '10 min ago', status: 'verified' },
  { location_text: 'Faerie Glen', distance: 5.1, time_ago: '32 min ago', status: 'pending' },
  { location_text: 'Silver Lakes', distance: 8.7, time_ago: '1 hr ago', status: 'received' },
];

export function NearbyReport() {
  return (
    <div className="flex flex-wrap items-start gap-27">
      <ComponentsGroup title="Nearby Reports Panel">
        <div className="w-96 rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-stroke overflow-y-auto max-h-64">
          <NearbyReports nearbyFires={dummyFires} />
        </div>
      </ComponentsGroup>
    </div>
  );
}

export function MapOverlay() {
  return (
    <ComponentsGroup title="Map Stats Overlay">
      <div className="flex flex-wrap gap-2">
        <Labled caption="with data">
          <div className="relative w-72 h-96 bg-carbon-side/40 rounded-lg border border-carbon-stroke overflow-hidden">
            <MapStatsOverlay nearbyFires={dummyFires} />
          </div>
        </Labled>
      </div>
    </ComponentsGroup>
  );
}
