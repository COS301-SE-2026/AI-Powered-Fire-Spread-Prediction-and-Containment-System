import { EnvironmentWidgets } from './EnvironmentWidgets';
import { LoggedContainmentLine } from './containmentLineCard';
import { Prediction, SimulationStatus } from '../../hooks/useSimulation';
import { useNearbyFires } from '../../hooks/useNearbyFires';

interface SimulationResultsProps {
  predictions?: Prediction[];
  currentTick?: number;
  status?: SimulationStatus;
  containmentLines?: string[];
  selectedFireId?: string | null;
}

function countStates(grid: number[] | undefined) {
  if (!grid) return { burning: 0, burned: 0, unburned: 0, total: 0 };
  let burning = 0;
  let burned = 0;
  for (const cell of grid) {
    if (cell == 1) burning++;
    else if (cell == 2) burned++;
  }
  return { burning, burned, unburned: grid.length - burning - burned, total: grid.length };
}

export function SimulationResults({
  predictions = [],
  currentTick = 0,
  status = 'idle',
  containmentLines = [],
  selectedFireId = null,
}: SimulationResultsProps) {
  const { environmentVariables } = useNearbyFires();

  const totals = predictions.reduce(
    (acc, p) => {
      const c = countStates(p.history[currentTick]);
      return {
        burning: acc.burning + c.burning,
        burned: acc.burned + c.burned,
        unburned: acc.unburned + c.unburned,
      };
    },
    { burning: 0, burned: 0, unburned: 0 }
  );

  const hasResult = predictions.length > 0;
  const upperBoundSpread = 15.0; // in km

  return (
    <div className="w-full shrink-0 flex flex-col gap-3 px-2 py-3 overflow-auto">
      {/* Simulation header */}
      <div>
        <h3 className="text-xs uppercase tracking-widest text-text-muted font-semibold">
          Simulation - time area
        </h3>
        <p className="text-xs text-text-disabled">
          {status === 'idle' && 'Not yet run'}
          {status === 'loading' && 'Running simulation...'}
          {status === 'playing' && `Tick ${currentTick} - Playing`}
          {status === 'paused' && `Tick ${currentTick} - Paused`}
          {status === 'error' && 'Simulation failed'}
        </p>
      </div>

      {/* Live burn stats for current tick */}
      {hasResult && (
        <div className="flex gap-3">
          <div className="flex flex-col">
            <span className="text-xs text-text-muted uppercase">Burning</span>
            <span className="text-sm font-semibold text-ignite">
              {totals.burning}
              cells
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-text-muted uppercase">Burned</span>
            <span className="text-sm font-semibold text-green-500/70">
              {totals.burned}
              cells
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-text-muted uppercase">Unburned</span>
            <span className="text-sm font-semibold text-green-500/70">
              {totals.unburned}
              cells
            </span>
          </div>
        </div>
      )}

      {/* Weather conditions */}
      <div>
        <p className="text-sm uppercase py-2">weather inputs</p>
        <EnvironmentWidgets variables={environmentVariables} />
      </div>

      {/* simulation results */}
      <div>
        <div className='flex items-center justify-between py-2'>
          <p className="text-sm uppercase py-2">predicted spread area</p>
          {hasResult && (
            <span className='text-sm uppercase font-mono text-text-muted bg-carbon-bg px-1.5 py-0.5 rounded border border-carbon-stroke'>
              {predictions.length > 1 ? `Max Overall Spread (${predictions.length} Fires)` : `Single Fire`}
            </span>
          )}
        </div>
          

        {!hasResult ? (
          <p className="text-xs text-text-disabled">Run the simulation to see spread data</p>
        ) : (
          <div className="flex flex-col gap-2">
            {[1, 3, 6, 12, 24, 48, 72].map((hour) => {
              // const p = predictions[0];
              const tickHour = hour * 4;
              const radiusses: number[] = [];

              for(const p of predictions){
                const realTick = Math.min(tickHour, p.history.length - 1);
                const grid = p.history[realTick];

                let affectedCells = 0;
                if (grid) {
                  for (const cell of grid) {
                    if (cell === 1 || cell == 2) affectedCells++;
                  }
                }

                const areaPerCell = p.cell_size_m ** 2;
                const currentSquareMeters = affectedCells * areaPerCell;
                const currentRadius = Math.sqrt(currentSquareMeters / Math.PI); // in meters
                const currRadius = currentRadius / 1000; // convert to km

                radiusses.push(currRadius);
              }
              
              const maxRadius = radiusses.length > 0 ? Math.max(...radiusses) : 0;
              const barWidth = Math.min((maxRadius / upperBoundSpread) * 100, 100);

              return (
                <div key={hour} className="flex items-center gap-2">
                  <span className="text-xs text-text-muted w-8 shrink-0">{hour}h</span>
                  <div className="flex-1 h-2 rounded-full bg-carbon-stroke overflow-hidden">
                    <div
                      className="h-full rounded-full bg-ignite"
                      style={{ width: `${barWidth}%` }}
                    />{' '}
                    {/* bar for results calculated by dividing max hectar from predicted fire by current times hectar estimate */}
                  </div>
                  <span className="text-xs text-text-primary shrink-0">
                    {maxRadius.toFixed(1)}/{upperBoundSpread} km
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* logged containment lines */}
      <div>
        <p className="text-sm uppercase py-2">containment lines logged</p>
        <LoggedContainmentLine 
          lines={containmentLines}
          selectedFireId={selectedFireId}
        />
      </div>
    </div>
  );
}
