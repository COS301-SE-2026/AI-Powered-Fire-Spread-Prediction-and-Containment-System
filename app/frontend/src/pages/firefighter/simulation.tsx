import { useState } from 'react';
import { Pencil, CirclePlay, Pause, RotateCcw, AlertTriangle, Loader2, Square, Trash2 } from 'lucide-react';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { SimulationResults } from '../../components/firefighter/simulationResult';
import { FireMap } from '../../components/shared/DynamicFirefighterMap';
import { useContainmentLine } from '../../hooks/useContainmentLine';
import { useSimulation } from '../../hooks/useSimulation';
import { useFirefighterReports } from '../../hooks/useFirefighterReports';

export default function Simulation() {
  const { reports: fires } = useFirefighterReports('');
  const [selectedFireId, setSelectedFireId] = useState<string | null>(null);
  const defaultLocation = { lat: -25.7479, lng: 28.2293 }; // Pretoria
  const [drawMode, setDrawMode] = useState(false);
  const [userLocation] = useState(defaultLocation);
  const [clearDrawings] = useState(0);
  const {
    submitLine,
    loading: savingLine,
    error: lineError,
  } = useContainmentLine(() => setDrawMode(false));

  const {
    status,
    error,
    runSimulation,
    predictions,
    currentTick,
    seekToTick,
    play,
    pause,
    totalTicks,
    stopRunning,
    clearMap
  } = useSimulation();

  const isLoading = status === 'loading';
  const isPlaying = status === 'playing';
  const hasResult = totalTicks > 0;

  function handleRun() {
      runSimulation(selectedFireId, 288);
  }

  function handleStop(){
    stopRunning();
  }

  function handleClear(){
    clearMap();
  }

  function handleReset() {
    seekToTick(0);
    pause();
  }

    const maxSlider = Math.max(totalTicks-1, 1);    // Timeline slider tracks currentTick when simulation is running. Manual drag seeks to specific task
    const totalHours = hasResult ? (maxSlider / 4) : 72;
    return (
        <FirefighterSideBar>
            <div className='p-4 flex flex-col h-full w-full gap-y-3'>

                {/*Page header and subtitle*/}
                <header className='mb-6'>
                    <h1 className='text-page-title font-display font-bold tracking-wider text-text-primary uppercase'>Fire Simulation</h1>
                    <p className='font-body text-body text-text-primary/50'>Simulate fire spread and prevention methods</p>
                </header>

        <div className="flex flex-row gap-4 min-w-0">
          {/* left side of page: map + controls and buttons */}
          <div className="basis-3/4 flex flex-col gap-4">
            {/* Fire Map */}
            <div className="rounded-2xl bg-carbon-side/80 border border-carbon-stroke backdrop-blur-sm shadow-2xl shadow-black/20 h-[70vh] overflow-hidden relative">
              <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                <span className="font-bold text-lg tracking-wide text-neutral/80 uppercase">
                  LIVE FIRE MAP
                </span>

                {/* Live tick badge */}
                {hasResult && (
                  <span className="text-xs font-mono text-ignite/80 bg-ignite/10 border border-ignite/30 px-2 py-1 rounded-md">
                    TICK {currentTick + 1} / {totalTicks}
                  </span>
                )}
              </div>

              {/* Loading overlay */}
              {isLoading && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-carbon-bg/70 backdrop-blur-sm gap-3">
                  <Loader2 className="animate-spin text-ignite" size={40} />
                  <span className="text-neutral/70 text-sm font-mono uppercase tracking-widest">
                    Running Simulation...
                  </span>
                </div>
              )}

              {/* Error overlay */}
              {status === 'error' && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-carbon-bg/80 backdrop-blur-sm gap-3 p-6">
                  <AlertTriangle className="text-red-400" size={36} />
                  <p className="text-red-400 text-sm font-mono text-center max-w-xs">
                    {error ?? 'Simulation failed. Check the backend is running'}
                  </p>
                  <button
                    onClick={handleRun}
                    className="btn btn-sm btn-outline text-neutral/70 mt-2"
                  >
                    Retry
                  </button>
                </div>
              )}

              <div className='w-full h-full'>
                <FireMap
                  lat={userLocation.lat}
                  lng={userLocation.lng}
                  drawMode={drawMode}
                  onDrawComplete={submitLine}
                  clearDrawings={clearDrawings}
                  predictions={predictions}
                  currentTick={currentTick}
                  selectedFireId={selectedFireId}
                  onSelectFire={setSelectedFireId}
                />
              </div>
          </div>

            {/* simulation vars and buttons */}
            <div className="flex gap-2 items-stretched">
              {/* buttons to start simulation or draw page */}
              <div className="flex flex-col gap-6 shrink-0 h-auto justify-between">
                <button
                  type="button"
                  onClick={() => setDrawMode(true)}
                  className="btn btn-primary rounded-lg btn-outline btn-wide btn-xl p-2 flex-1"
                >
                  <Pencil size={28} />
                  Draw Containment
                </button>

                {/* Run/pause/resume/cancel/clear button */}
                {isLoading ? (
                  <button
                    type="button"
                    onClick={handleStop}
                    className='btn btn-error rounded-lg btn-outline p-2 w-full flex items-center justify-center gap-2'
                    title='Cancel Simulation Request'
                    >
                      <Square size={20}/>
                      Cancel Simulation
                    </button>
                ): !hasResult || status === 'idle' || status === 'error' ? (
                  <button
                    onClick={handleRun}
                    disabled={isLoading}
                    className="btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1 disabled-opacity-50"
                  >
                    {isLoading ? (
                      <Loader2 className="animate-spin" size={24} />
                    ) : (
                      <CirclePlay size={24} />
                    )}
                    {isLoading ? 'Running...' : 'RUN'}
                  </button>
                ) : isPlaying ? (
                  <div className='flex gap-2 flex-1 w-full'>
                    <button
                      onClick={pause}
                      className="btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1"
                    >
                    <Pause size={24} />
                      Pause
                    </button>
                    <button
                      onClick={handleStop}
                      className='btn btn-error rounded-lg btn-outline p-2 flex-1'
                      title='Stop Simulation'
                    >
                      <Square size={20}/>
                      Stop
                    </button>
                  </div>
                  

                ) : (
                  <div className="flex gap-2 flex-1">
                    <button
                      onClick={play}
                      className="btn btn-accent rounded-lg btn-outline btn-xl p-2 flex-1"
                    >
                      <CirclePlay size={22} />
                      Resume
                    </button>
                    <button
                      onClick={handleRun}
                      className="btn btn-outline rounded-lg btn-xl p-2 flex-1 text-neutral/60"
                      title="Re-run simulation"
                    >
                      <RotateCcw size={18} />
                    </button>
                    <button
                      onClick={handleClear}
                      className='btn btn-outline btn-info rounded-lg p-2 flex-1'
                    >
                      <Trash2 size={18}/>
                      Clear map
                    </button>
                  </div>
                )}
              </div>

              {/* input variables */}
              <div className="border border-carbon-stroke w-full rounded-2xl bg-carbon-side">
                <div className="flex flex-col gap-3 p-2">
                  <p className="text-sm uppercase tracking-wide text-text-muted font-semibold">
                    Simulation Timeline
                  </p>

                  {/* Timeline slider */}
                  <div className="flex flex-col gap-1 p-2">
                    <div className="flex flex-row items-center justify-between">
                      <span className="text-sm text-text-muted p-1">
                        {hasResult ? `Tick ${currentTick + 1} of ${totalTicks}` : 'Not yet run'}
                      </span>
                    </div>

                    <div className="w-full">
                      <input
                        type="range"
                        min={0}
                        max={maxSlider}
                        step={1}
                        className="range range-xs w-full disabled:opacity-30"
                        value={currentTick}
                        disabled={!hasResult}
                        onChange={(e) => seekToTick(Number(e.target.value))}
                      />

                      <div className="flex justify-between px-2.5 mt-2 text-sm">
                        <span>0h</span>
                        <span>{Math.round(totalHours / 4)}h</span>
                        <span>{Math.round(totalHours / 2)}h</span>
                        <span>{Math.round((totalHours * 3) / 4)}h</span>
                        <span>{totalHours}h</span>
                      </div>
                    </div>
                  </div>

                  {/* Select a fire to run simulation on */}
                  <div className="border-t border-carbon-stroke/40 pt-3">
                    <p className="text-xs uppercase tracking-wide text-text-muted/60 font-semibold mb-2">
                      Target Fire
                    </p>
                    <select
                      className="select select-sm select-bordered rounded-lg bg-carbon-bg text-neutral-content w-full"
                      value={selectedFireId ?? ''}
                      onChange={(e) => setSelectedFireId(e.target.value || null)}
                    >
                      <option value="">All verified fires</option>
                      {fires
                        .filter((f) => f.status === 'verified')
                        .map((f) => (
                          <option key={f.ref} value={f.ref} className="bg-carbon-bg text-neutral">
                            {f.location ?? f.ref}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Simulation results */}
          <div className="basis-1/4 rounded-2xl bg-carbon-side border border-carbon-stroke overflow-y-auto">
            <SimulationResults
              // Pass live stats so panel can show burning/burned counts per tick
              predictions={predictions}
              currentTick={currentTick}
              status={status}
            />
          </div>
        </div>
      </div>
    </FirefighterSideBar>
  );
}
