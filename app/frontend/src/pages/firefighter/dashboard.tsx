import React, { useState } from 'react';
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

export default function FirefighterDashboard() {
  const [drawMode, setDrawMode] = useState(false);
  const [clearDrawings, setClearDrawings] = useState(0);
  const { userLocation, nearbyFires, environmentVariables } = useNearbyFires();
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  const { showHint, dismiss } = useRotate();
  const {
    submitLine,
    loading: savingLine,
    error: lineError,
  } = useContainmentLine(() => setDrawMode(false));

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
            <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-96 sm:h-104 md:h-120">
              <div className="p-3 md:p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                <span className="font-bold text-sm md:text-m tracking-wide text-text-primary/80">
                  LIVE FIRE MAP
                </span>
                <button
                  type="button"
                  onClick={() => setClearDrawings((c) => c + 1)}
                  className="text-sm font-medium text-text-muted hover:text-ignite transition-colors"
                >
                  Clear Lines
                </button>
              </div>
              <div className="flex-1 w-full h-full pt-12 md:pt-13">
                <FireMap
                  lat={userLocation.lat}
                  lng={userLocation.lng}
                  drawMode={drawMode}
                  onDrawComplete={submitLine}
                  clearDrawings={clearDrawings}
                  selectedFireLocation={fireLocation}
                  onSelectFire={handleSelectFire}
                  onDeselect={clearSelect}
                />
              </div>
              <MapStatsOverlay nearbyFires={nearbyFires} />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-2 shrink-0">
              <div className="flex flex-col">
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
          <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>
            <h3 className="font-bold tracking-widest text-text-muted uppercase shrink-0">
              Nearby Reports
            </h3>
            <div
              className="rounded-2xl bg-carbon-side/40 border border-carbon-card overflow-y-auto max-h-96">
              <NearbyReports nearbyFires={nearbyFires} selectedFireId={fireLocation} onSelectFire={handleSelectFire} />
            </div>
          </div>
        </div>
      </div>
    </FirefighterSideBar>
  );
}
