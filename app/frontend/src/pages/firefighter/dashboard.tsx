import React, { useState } from 'react';
import type { LocalLine, CreateContainmentLine } from '@/types/ContainmentLines';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { QuickActions } from '../../components/firefighter/quickActions';
import { NearbyReports } from '../../components/shared/nearbyReports';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { EnvironmentWidgets } from '../../components/firefighter/EnvironmentWidgets';
import { MapStatsOverlay } from '../../components/firefighter/mapStat';
import { FireMap } from '../../components/shared/DynamicFirefighterMap';
import { useContainmentLine } from '../../hooks/useContainmentLine';
import { useFireSelect } from '../../hooks/useFireSelect';
import { useRotate } from '../../hooks/useRotate';
import { PageHeader } from '../../components/layout/pageHeader';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { RotateHint } from '../../components/shared/RotateHint';
import { useMapLink } from '../../hooks/useMapLink';
import { NearbyResources } from '../../components/shared/NearbyResources';
import { useNearbyResources } from '../../hooks/useNearbyResources';
import { ResourceMapLegend } from '../../components/shared/ResourceMapLegend';

export default function FirefighterDashboard() {
  const [drawMode, setDrawMode] = useState(false);
  const [clearDrawings, setClearDrawings] = useState(0);
  const [showWater, setShowWater] = useState(true);
  const { userLocation, nearbyFires, environmentVariables } = useNearbyFires();
  const { nearbyResources } = useNearbyResources(userLocation);
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  const { showHint, dismiss } = useRotate();
  const [lines, setLines] = useState<LocalLine[]>([])
  const {
    submitLine,
    loading: savingLine,
    error: lineError,
    fetchLines,
    deleteLine
  } = useContainmentLine();
  const [showResources, setShowResources] = useState(true);

  const availableResources = nearbyResources.filter((r) => r.status === 'available');

  async function handleDrawComplete(wkt: string) {
    const localId = crypto.randomUUID();
    setLines(prev => [...prev, {
      localId, dbId: null, wkt, fireReportId: null, synced: false,
    }]);
    setDrawMode(false);

    try{
      const saved = await submitLine({wkt});
      if(!saved?.id){
        setLines(prev => prev.filter(l => l.localId !== localId))
        return;
      }
      setLines(prev => prev.map(l =>
        l.localId === localId ? {...l, dbId: saved.id, fireReportId: saved.fire_report_id, synced: true} : l
      ));
    }catch {
      setLines(prev => prev.filter(l => l.localId !== localId))
    }
  }
  useMapLink(handleSelectFire);

  function handleSelectResource(r: { id: string }) {
    setSelectedResourceId(r.id);
    setShowResources(true);
  }
  return (
    <FirefighterSideBar hideLoginRegister>
      <div className="flex flex-col p-2 md:p-6">
        <NotificationToastHost />
        <RotateHint show={showHint} onDismiss={dismiss} />
        <PageHeader
          title="Firefighter Dashboard"
          subtitle="Tshwane District • Real-time Monitoring"
          showIcons
        />

        {/* Main Grid container */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-3 md:gap-4 xl:grid-rows-1">
          <div className="xl:col-span-8 flex flex-col gap-3 md:gap-4">
            {/* Map */}
            <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-96 sm:h-104 md:h-136">
              <div className="p-3 md:p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                <span className="font-bold text-sm md:text-m tracking-wide text-text-primary/80">
                  LIVE FIRE MAP
                </span>
                <div className='flex items-center gap-4'>
                  <label className='flex items-center gap-2 cursor-pointer select-none'>
                    <span className='text-sm font-medium text-text-muted'>
                      Show Water
                    </span>
                    <button
                      type='button'
                      role='switch'
                      aria-checked={showWater}
                      onClick={() => setShowWater((w) => !w)}
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${showWater ? 'bg-ignite' : 'bg-carbon-stroke'}`}
                    >
                      <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-md transition-transform ${showWater ? 'translate-x-4' : 'translate-x-1'}`} />
                    </button>
                  </label>

                  <button
                    type="button"
                    onClick={() => setClearDrawings((c) => c + 1)}
                    className="text-sm font-medium text-text-muted hover:text-ignite transition-colors"
                  >
                  Clear Lines
                </button>
                </div>

              </div>
              <div className="flex-1 w-full h-full pt-12 md:pt-13">
                <FireMap
                  lat={userLocation.lat}
                  lng={userLocation.lng}
                  drawMode={drawMode}
                  onDrawComplete={handleDrawComplete}
                  lines={lines}
                  clearDrawings={clearDrawings}
                  selectedFireLocation={fireLocation}
                  onSelectFire={handleSelectFire}
                  onDeselect={clearSelect}
                  selectedFireId={fireLocation}
                  showWater={showWater}
                  resources={availableResources}
                  showResources={showResources}
                  selectedResourceId={selectedResourceId}
                  onSelectResource={handleSelectResource}
                />
              </div>
              <MapStatsOverlay nearbyFires={nearbyFires} />
            </div>
            <ResourceMapLegend />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-2 shrink-0">
              <div className="flex flex-col">
                <h1 className='sr-only'>
                  Firefighter Dashboard
                </h1>
                <h2 className='sr-only'>
                  Dashboard
                </h2>
                <h3 className="font-bold tracking-widest text-text-muted uppercase mb-3">
                  Environment Variables
                </h3>
                <EnvironmentWidgets variables={environmentVariables} />
              </div>
              <div className="flex flex-col">
                <h3 className="font-bold tracking-widest text-text-muted uppercase mb-3">
                  Quick Actions
                </h3>
                <QuickActions onStartDraw={() => setDrawMode(true)} />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 flex flex-col gap-3 xl:h-0 xl:min-h-full">
              <p className=" text-text-muted uppercase shrink-0">
                Nearby Reports
              </p>
              <div className="shrink-0 max-h-64 rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto">
                <NearbyReports nearbyFires={nearbyFires}  selectedFireId={fireLocation} onSelectFire={handleSelectFire}/>
              </div>

              <p className=" text-text-muted uppercase shrink-0">
                Available Resources
              </p>
              <div className="min-h-0 rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto">
                <NearbyResources resources={availableResources}  selectedResourceId={selectedResourceId} onSelectResource={(r) => setSelectedResourceId(r.id)}/>
              </div>
            </div>
        </div>
      </div>
    </FirefighterSideBar>
  );
}
