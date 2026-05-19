import React from 'react';
import { Wind, Droplets, Flame, Thermometer } from 'lucide-react';
import Button from '../components/Button';
import ReportCard from '../components/ReportCard';
import WeatherWidget from '../components/WeatherWidget';
import MapOverlay from '../components/MapOverlay';
import MapPopup from '../components/MapPopup';

export default function DashboardPage() {
  return (
    <div className="p-8 space-y-8 bg-[#080B12] min-h-screen text-[#EDEAE5]">
      
      {/* 1. BUTTONS */}
      <div className="space-y-2 max-w-sm">
        <h3 className="text-xs text-white/30 uppercase font-mono">01 · Buttons</h3>
      <Button variant="fire">
        <i className="ti ti-flame" aria-hidden="true" />
        Report Wildfire
        </Button>

        <Button variant="dark">Default Dark Button</Button>

        <Button variant="red">
        <i className="ti ti-shield-check" aria-hidden="true" />
        Verify Tactical
        </Button>

        <Button variant="ghost">Cancel Operation</Button>
    </div>
      {/* 2. INCIDENT RECORDS */}
      <div className="space-y-2 max-w-sm">
        <h3 className="text-xs text-white/30 uppercase font-mono">02 · ReportCard Component</h3>
        <ReportCard location="Northcliff Ridge" distance="2.3 km away" timeAgo="14 mins ago" />
      </div>

      {/* 3. WEATHER WIDGETS */}
      <div className="space-y-2 max-w-xs">
        <h3 className="text-xs text-white/30 uppercase font-mono">03 · WeatherWidget Component</h3>
        <div className="space-y-2">
            <WeatherWidget icon={<Wind size={16} />}        value="34 km/h"  label="Wind NW"      type="wind"     />
            <WeatherWidget icon={<Droplets size={16} />}    value="12%"      label="Humidity"     type="humidity" />
            <WeatherWidget icon={<Flame size={16} />}       value="Extreme"  label="Fire Danger"  type="danger"   />
            <WeatherWidget icon={<Thermometer size={16} />} value="38°C"     label="Temperature"  type="temp"     />
        </div>
      </div>

      {/* 4. MAP OVERLAYS */}
      <div className="space-y-2">
        <h3 className="text-xs text-white/30 uppercase font-mono">04 · MapOverlay Component</h3>
        <div className="flex flex-wrap gap-2">
          <MapOverlay label="Active Fires" count="3" subtext="In your area" />
          <MapOverlay label="Nearest Threat" count="2.7 km" subtext="km away" />
          <MapOverlay label="Pending Verification" count="9" subtext="Unverified" />
        </div>
      </div>

      {/* 5. MAP POPUP */}
      <div className="space-y-2 max-w-xs">
        <h3 className="text-xs text-white/30 uppercase font-mono">05 · MapPopup Component</h3>
        <MapPopup 
          title="Northcliff"
          actions={
            <>
              <Button variant="dark">Details</Button>
              <Button variant="dark">Tactics</Button>
            </>
          }
        >
          <div className="space-y-0.5 text-white/70">
            <p>Reported at: <span className="text-[#EDEAE5] font-mono">14 mins ago</span></p>
            <p>Est. size: <span className="text-[#EDEAE5] font-mono">2.4 Hectares</span></p>
            <p>Spread: <span className="text-[#EDEAE5] font-mono">Northeast</span></p>
          </div>
        </MapPopup>
      </div>

    </div>
  );
}