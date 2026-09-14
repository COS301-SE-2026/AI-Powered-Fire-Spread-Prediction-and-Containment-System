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
import { PageHeader } from '../../components/layout/pageHeader';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { RotateHint } from '../../components/shared/RotateHint';
import { useMapLink } from '../../hooks/useMapLink';
import { useFireSelect } from '../../hooks/useFireSelect';
import { useRotate } from '../../hooks/useRotate';

export default function FirefighterDashboard() {
  const [drawMode, setDrawMode] = useState(false);
  const [clearDrawings, setClearDrawings] = useState(0);
  const { userLocation, nearbyFires, environmentVariables } = useNearbyFires();
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
  return (
    <FirefighterSideBar hideLoginRegister>
      <div className="flex flex-col p-6">
        <NotificationToastHost />
        <PageHeader
          title="Firefighter Dashboard"
          subtitle="Tshwane District • Real-time Monitoring"
          showIcons
        />

        {/* Main Grid container */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">
          <div className="xl:col-span-8 flex flex-col gap-4">
            {/* Map */}
            <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-96 sm:h-104 md:h-136">
              <div className="p-3 md:p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                <span className="font-bold text-sm md:text-m tracking-wide text-text-primary/80">
                  LIVE FIRE MAP
                </span>
                <button
                  type="button"
                  onClick={() => setClearDrawings((c) => c + 1)}
                  className="text-xs font-medium text-text-primary/60 hover:text-ignite transition-colors"
                >
                  Clear Lines
                </button>
              </div>
              <div className="flex-1 w-full h-full pt-[53px]">
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
                />
              </div>
              <MapStatsOverlay nearbyFires={nearbyFires} />
            </div>
            <div className="grid grid-cols-2 gap-2 shrink-0">
              <div className="flex flex-col">
                <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase mb-3">
                  Environment Variables
                </h2>
                <EnvironmentWidgets variables={environmentVariables} />
              </div>
              <div className="flex flex-col">
                <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase mb-3">
                  Quick Actions
                </h2>
                <QuickActions onStartDraw={() => setDrawMode(true)} />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 flex flex-col gap-3 h-full">
              <h4 className=" text-text-muted uppercase">
                Nearby Reports
              </h4>
              <div
                className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto max-h-130">
                <NearbyReports nearbyFires={nearbyFires}  selectedFireId={fireLocation} onSelectFire={handleSelectFire}/>
              </div>
            </div>
        </div>
      </div>
    </FirefighterSideBar>
  );
}
