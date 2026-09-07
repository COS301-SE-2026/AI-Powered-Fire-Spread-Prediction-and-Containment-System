import { useEffect, useState } from 'react';
import { Pencil, CirclePlay, Pause, RotateCcw, AlertTriangle, Loader2, Square, Trash2, SquareActivity } from 'lucide-react';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { SimulationResults } from '../../components/firefighter/simulationResult';
import { FireMap } from '../../components/shared/DynamicFirefighterMap';
import { useContainmentLine } from '../../hooks/useContainmentLine';
import { useSimulation } from '../../hooks/useSimulation';
import { useFirefighterReports } from '../../hooks/useFirefighterReports';
import { PageHeader } from '../../components/layout/pageHeader';
import { useRotate } from '../../hooks/useRotate';
import { RotateHint } from '../../components/shared/RotateHint';

export default function Simulation() {
  const { reports: fires } = useFirefighterReports('');
  const [selectedFireId, setSelectedFireId] = useState<string | null>(null);
  const defaultLocation = { lat: -25.7479, lng: 28.2293 }; // Pretoria
  const [drawMode, setDrawMode] = useState(false);
  const [userLocation] = useState(defaultLocation);
  const [clearDrawings, setClearDrawings] = useState(0);

  const [containmentLines, setContainmentLines] = useState<string[]>([]);
  const { showHint, dismiss } = useRotate();
  const {
    submitLine,
    loading: savingLine,
    error: lineError,
  } = useContainmentLine();

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
      const steps = selectedFireId ? 288 : 4
      runSimulation(selectedFireId, steps, containmentLines);
  }

  function handleStop(){
    stopRunning();
  }

  function handleClear(){
    clearMap();
    setClearDrawings((prev) => prev + 1);
    setContainmentLines([]);
  }

  function handleReset() {
    seekToTick(0);
    pause();
  }

  useEffect(() => {
    clearMap();
  }, [selectedFireId, clearMap])

  const canClear = hasResult || containmentLines.length > 0 || currentTick > 0;

    const maxSlider = Math.max(totalTicks-1, 1);    // Timeline slider tracks currentTick when simulation is running. Manual drag seeks to specific task
    const totalHours = hasResult ? (maxSlider / 4) : 72;
    return (
        <FirefighterSideBar hideLoginRegister>
            <div className='p-2 landscape:p-2 flex flex-col h-full w-full gap-y-3 landscape:gap-y-2'>

                {/* Page header and subtitle */}
                <RotateHint show={showHint} onDismiss={dismiss} />
                <PageHeader title="Fire Simulation" subtitle="Simulate fire spread and prevention methods" showIcons />

        <div className="flex flex-col lg:flex-row gap-4 min-w-0">
          {/* left side of page: map + controls and buttons */}
          <div className="basis-full lg:basis-3/4 flex flex-col gap-4 min-w-0">
            {/* Fire Map */}
            <div className="rounded-2xl bg-carbon-side/80 border border-carbon-stroke backdrop-blur-sm shadow-2xl shadow-black/20 h-[50vh] landscape:h-[80vh] max-h-[420px] landscape:max-h-none overflow-hidden relative">
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
                  onDrawComplete={(line) => {
                    submitLine(line);
                    setDrawMode(false);
                  }}
                  onContainmentChange={setContainmentLines}
                  clearDrawings={clearDrawings}
                  predictions={predictions}
                  currentTick={currentTick}
                  selectedFireId={selectedFireId}
                  onSelectFire={setSelectedFireId}
                  showKey
                />
              </div>
          </div>

            {/* simulation vars and buttons */}
            <div className="flex flex-col lg:flex-row gap-3 items-stretch">
              {/* buttons to start simulation or draw page */}
              <div className="flex flex-col gap-3 shrink-0 w-full lg:w-80">
                <button
                  type="button"
                  onClick={() => setDrawMode((prev) => !prev)}
                  className="btn btn-primary btn-outline w-full flex items-center justify-center gap-2 rounded-xl text-sm font-semibold tracking-wide"
                >
                  <Pencil size={20} />
                  Draw Containment
                </button>

                {/* Run/Cancel */}
                <button
                  type="button"
                  onClick={isLoading? handleStop : handleRun}
                  disabled={hasResult && !isLoading && status !== 'error'}
                  className={`btn rounded-xl btn-outline w-full flex items-center justify-center gap-2 text-sm font-semibold disabled:opacity-30 disable:pointer-events-none ${
                    isLoading? 'btn-error' : 'btn-accent'}`}
                  title={isLoading ? 'Cancel Simulation Request' : undefined}
                >
                  {isLoading? (
                    <Square size={20}/>
                  ) : (
                    <CirclePlay size={24}/>
                  )}

                  {isLoading ? 'Cancel Simulation' : 'RUN'}
                </button>

                {/* Pause and Resume buttons */}
                <div className='flex gap-2'>
                  <button
                    onClick={isPlaying ? pause : play}
                    disabled={!hasResult || isLoading}
                    className='btn btn-accent rounded-xl btn-outline flex-1 disabled:opacity-30 disabled:pointer-events-none'
                  >
                    {isPlaying ? <Pause size={20}/> : <CirclePlay size={20}/>}
                    {isPlaying ? 'Pause' : 'Resume'}
                  </button>
                  <button
                    onClick={handleStop}
                    disabled={!hasResult || isLoading}
                    className='btn btn-error rounded-xl btn-outline flex-1 disabled:opacity-30 disabled:pointer-events-none'
                    title='Stop Simulation'
                  >
                    <Square size={20}/>
                    Stop
                  </button>
                </div>

                {/* Rerun and clear buttons */}
                <div className='flex gap-2'>
                  <button
                    onClick={handleRun}
                    disabled={!hasResult || isLoading}
                    className='btn btn-outline rounded-xl flex-1 text-neautral/60 disabled:opacity-30 disabled:pointer-events-none'
                    title='Re-run Simulation'
                  >
                    <RotateCcw size={20}/>
                    Re-run
                  </button>
                  <button
                    onClick={handleClear}
                    disabled={!canClear || isLoading}
                    className='btn btn-outline btn-info rounded-xl flex-1 disabled:opacity-30 disabled:pointer-events-none'
                  >
                    <Trash2 size={20}/>
                    Clear Map
                  </button>
                </div>
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
          <div className="basis-full lg:basis-1/4 rounded-2xl bg-carbon-side border border-carbon-stroke overflow-y-auto max-h-[40vh] lg:max-h-none">
            <SimulationResults
              // Pass live stats so panel can show burning/burned counts per tick
              containmentLines={containmentLines}
              selectedFireId={selectedFireId}
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