import { LocalLine } from '@/types/ContainmentLines';
import { AlertTriangle, ArrowUp, BrainCircuit, Droplets, Flame, Thermometer, Wind } from 'lucide-react';
import { TICKS_PER_HOUR } from '@/types/simulation';
import { LoggedContainmentLine } from './containmentLineCard';
import { Prediction, SimulationStatus, ClusterPrediction, ForecastModelInfo } from '../../hooks/useSimulation';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { useFuelConditions } from '../../hooks/useFuelConditions';
import { Sparkline } from './Sparkline';

interface SimulationResultsProps {
  predictions?: Prediction[];
  clusterPredictions?: ClusterPrediction[];
  currentTick?: number;
  status?: SimulationStatus;
  containmentLines?: LocalLine[];
  selectedFireId?: string | null;
  onDeleteLine?: (line: LocalLine) => void;
  fireLat?: number | null;
  fireLng?: number | null;
}

const DIRECTIONS = ["N", 'NNE', "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
function compass(deg: number): string {
  return DIRECTIONS[Math.round((deg % 360) / 22.5) % 16];
}

const BAND_COLOR: Record<string, string> = {
  blue: 'text-sky-400',
  green: 'text-green-500',
  yellow: 'text-yellow-400',
  orange: 'text-orange-400',
  red: 'text-red-500'
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

function formatKm2(km2: number): string{
  if(km2 === 0) return '0';
  if(km2 < 0.01) return '< 0.01';
  if(km2 < 1) return km2.toFixed(2);
  return km2.toFixed(1);
}

const CHANNEL_LABELS: Record<string, string> = {
  temperature: 'Temperature',
  relative_humidity: 'Humidity',
  wind_u: 'Wind (east-west)',
  wind_v: 'Wind (north-south)',
}

function skillToolTip(model: ForecastModelInfo): string{
  const pct = (v: number | undefined) => `${Math.round((v ?? 0) * 100)}%`
  return [
    'Lower error than assuming weather stays the same:',
    ...Object.entries(model.skill_by_channel).map(
      ([ch, byHour]) => `${CHANNEL_LABELS[ch] ?? ch}: ${pct(byHour['1'])} at 1h, ${pct(byHour['4'])} at 4h`
    ),
  ].join('\n')
}

export function SimulationResults({
  predictions = [],
  clusterPredictions = [],
  currentTick = 0,
  status = 'idle',
  containmentLines = [],
  selectedFireId = null,
  onDeleteLine = undefined,
  fireLat = null,
  fireLng = null
}: SimulationResultsProps) {
  const { searchLocation } = useNearbyFires();

  const selectedPrediction = selectedFireId ? predictions.find(p => p.ref === selectedFireId) : undefined;

  const lat = selectedPrediction?.lat ?? fireLat ?? searchLocation.lat;
  const lng = selectedPrediction?.lng ?? fireLng ?? searchLocation.lng;

  const { conditions, loading: conditionsLoading } = useFuelConditions(lat, lng);

  const runs: { history: number[][], cell_size_m: number }[] = [...predictions, ...clusterPredictions];

  function affectedAreaKm(tick: number): number {
    return runs.reduce((sum, r) => {
      const grid = r.history[Math.min(tick, r.history.length - 1)];
      if(!grid) return sum;
      const c = countStates(grid);
      return sum + ((c.burning + c.burned) * r.cell_size_m ** 2) / 1000000;
    }, 0)
  }

  const areaNowKm = affectedAreaKm(currentTick);
  const areaHourAgoKm = affectedAreaKm(Math.max(currentTick - TICKS_PER_HOUR,0));
  const radiusKm = (areaKm2: number) => Math.sqrt(areaKm2 / Math.PI);
  const hoursBack = Math.min(currentTick, TICKS_PER_HOUR) / TICKS_PER_HOUR;
  const spreadSpeedKmh = hoursBack > 0
    ? Math.max(radiusKm(areaNowKm) - radiusKm(areaHourAgoKm), 0) / hoursBack : 0;
  const elapsedHours = currentTick / TICKS_PER_HOUR;

  const totals = runs.reduce(
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

  const hasResult = runs.length > 0;
  const upperBoundSpread = 15.0; // in km

  const bandColor = conditions ? BAND_COLOR[conditions.fdi_color] ?? 'text-text-primary' : '';

  const weatherRun = selectedPrediction ?? clusterPredictions[0] ?? predictions[0];
  const weatherHours = weatherRun?.weather_by_hour ?? [];
  const simHour = Math.floor(currentTick / TICKS_PER_HOUR);
  const hourWeather = weatherHours.length ? weatherHours[Math.min(simHour, weatherHours.length - 1)] : undefined;
  const beyondForecast = weatherHours.length > 0 && simHour > weatherHours.length - 1;
  const forecastModel = weatherRun?.forecast_model;
  const valYears = forecastModel?.val_years ?? [];

  return (
    <div className="w-full shrink-0 flex flex-col gap-3 px-2 py-3 overflow-auto">
      {/* Simulation header */}
      <div>
        <h1 className="text-xs uppercase tracking-widest text-text-muted font-semibold">
          Simulation - time area
        </h1>
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
        <div className='grid grid-cols-2 gap-2'>
          <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
            <span className='text-xs text-text-muted uppercase'>Elapsed</span>
            <span className='text-sm font-semibold text-text-primary'>+{elapsedHours.toFixed(1)} h</span>
          </div>
          <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
            <span className='text-xs text-text-muted uppercase'>Area Affected</span>
            <span className='text-sm font-semibold text-text-primary'>{formatKm2(areaNowKm)} km²</span>
          </div>
          <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
            <span className='text-xs text-text-muted uppercase'>Spread Speed</span>
            <span className='text-sm font-semibold text-text-primary'>{spreadSpeedKmh.toFixed(2)} km/h</span>
          </div>
          <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
            <span className='text-xs text-text-muted uppercase'>Active front</span>
            <span className='text-sm font-semibold text-text-primary'>{totals.burning} cells</span>
          </div>
        </div>
      )}

      {hourWeather && (
        <div>
          <div className='flex items-center justify-between'>
            <p className='text-sm uppercase py-2'>simulated weather</p>
            <span className='text-[10px] font-mono text-text-disabled'>
              {simHour === 0 ? 'now' : `+${simHour} h`}
              {beyondForecast && ' · held from last forecast hour'}
            </span>
          </div>

          <div className='grid grid-cols-3 gap-2'>
            <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <span className='flex items-center gap-1 text-xs text-text-muted uppercase'>
                <Thermometer size={12}/> TEMP
              </span>
              <span className='text-sm font-semibold text-text-primary'>{hourWeather.temperature_c.toFixed(1)}°C</span>
            </div>
            <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <span className='flex items-center gap-1 text-xs text-text-muted uppercase'>
                <Droplets size={12}/> RH
              </span>
              <span className='text-sm font-semibold text-text-primary'>{hourWeather.rel_humidity_pct.toFixed(0)}%</span>
            </div>
            <div className='flex flex-col p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <span className='flex items-center gap-1 text-xs text-text-muted uppercase'>
                <Wind size={12}/> {compass(hourWeather.wind_dir_deg)}
              </span>
              <span className='flex items-center gap-1 text-sm font-semibold text-text-primary'>
                <ArrowUp size={14} style={{ transform: `rotate(${hourWeather.wind_dir_deg + 180}deg)`}}/>
                {hourWeather.wind_speed_kmh.toFixed(0)} km/h
              </span>
            </div>
          </div>
        
        {weatherRun?.forecast_source === 'convlstm' && forecastModel ? (
          <div
            className='mt-2 flex items-center gap-1.5 text-xs text-text-muted'
            title={skillToolTip(forecastModel)}
          >
            <BrainCircuit size={12} className='shrink-0'/>
            <span>
              ConvLSTM forecast · {Math.round(forecastModel.mean_skill * 100)}% lower error than no-change
              {valYears.length > 0 && ` (tested on ${valYears[0]}-${valYears[valYears.length-1]})`}
            </span>
          </div>
        ) : weatherRun?.forecast_source === 'current_weather' ? (
          <p className='mt-2 text-xs text-text-disabled'>Using the current weather (forecast model unavailable)</p>
        ): null}
        </div>
      )}

      {/* Weather conditions */}
      <div>
        <div className='flex items-center justify-between'>
          <p className='text-sm uppercase py-2'>weather inputs</p>
          <span className='text-[0.625rem] font-mono text-text-disabled'>
            {selectedPrediction || fireLat ? 'at fire' : 'your location'}
          </span>
        </div>

        {conditionsLoading && !conditions ? (
          <p className='text-xs text-text-disabled'>Loading condtions...</p>
        ) : !conditions ? (
          <p className='text-xs text-text-disabled'>No environment data availiable</p>
        ): (
          <div className='grid grid-cols-2 gap-2'>
            <div className='flex items-center gap-2 p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <Wind size={16} className='text-text-muted shrink-0'/>
              <div className='flex flex-col min-w-0'>
                <span className='text-sm uppercase text-text-muted'>
                  Wind {compass(conditions.wind_direction)}
                </span>
                <span className='text-xs text-text-primary'>
                  {conditions.wind_speed.toFixed(0)} km/h
                  <span className='text-xs text-text-primary'> g{conditions.wind_gusts.toFixed(0)}</span>
                </span>
              </div>
            </div>

            <div className='flex items-center gap-2 p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <Thermometer size={16} className='text-text-muted'/>
              <div className='flex flex-col'>
                <span className='text-sm uppercase text-text-muted'>Temperature</span>
                <span className='text-xs text-text-primary'>
                  {conditions.temperature.toFixed(1)}°C
                </span>
              </div>
            </div>

            <div className='flex items-center gap-2 p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <Droplets size={16} className='text-text-muted'/>
              <div className='flex flex-col'>
                <span className='text-sm uppercase text-text-muted'>Humidity</span>
                <span className='text-xs text-text-primary'>
                  {conditions.humidity.toFixed(1)}%
                </span>
              </div>
            </div>

            <div className='flex items-center gap-2 p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
              <Flame size={16} className={`shrink-0 ${bandColor}`}/>
              <div className='flex flex-col'>
                <span className='text-sm uppercase text-text-muted'>FDI {conditions.fdi}</span>
                <span className={`text-xs font-semibold truncate ${bandColor}`}>
                  {conditions.fdi_band}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/*  */}
      {conditions && (
        <div>
          <p className='text-sm uppercase py-2'>fuel conditions</p>
          <div className='flex flex-col gap-2 p-2 rounded-lg bg-carbon-bg border border-carbon-stroke'>
            <div className='flex items-baseline justify-between'>
              <span
                className='text-xs text-text-muted'
                title='Keetch-Byram Drought Index - cumulative moisture deficit'
              >
                Drought Index (KBDI)
              </span>
              <span className='text-sm font-semibold text-text-primary'>
                {conditions.kbdi.toFixed(0)}
                <span className='text-text-muted text-xs'>/800</span>
              </span>
            </div>

            <Sparkline values={conditions.kbdi_series}/>
            <span className='text-sm text-text-disabled -mt-1'>30-day trend</span>

            <div className='flex justify-between text-xs pt-1 border-t border-carbon-stroke/50'>
              <span className='text-text-muted'>Last Rain</span>
              <span className='text-text-primary'>
                {conditions.days_since_rain === 0 ? 'today': `${conditions.days_since_rain}d ago`}
                {conditions.last_rain_mm > 0 && `• ${conditions.last_rain_mm}mm`}
              </span>
            </div>
            <div className='flex justify-between text-xs'>
              <span className='text-text-muted'>30-day total</span>
              <span className='text-text-primary'>{conditions.rain_30d_mm}mm</span>
            </div>

            <div className='flex flex-col gap-1 pt-1 border-t border-carbon-stroke/50'>
              {(
                [
                  ['Grass/veld', conditions.dryness_grass],
                  ['Shrub', conditions.dryness_shrub],
                  ['Plantation', conditions.dryness_plantation],
                ] as const
              ).map(([label, value]) => (
                <div key={label} className='flex items-center gap-2'>
                  <span className='text-sm text-text-muted w-20 shrink-0'>{label}</span>
                  <div className='flex-1 h-1.5 rounded-full bg-carbon-stroke overflow-hidden'>
                    <div
                      className='h-full rounded-full bg-ignite'
                      style={{width: `${value * 100}%`}}
                    />
                  </div>
                  <span className='text-sm text-text-primary w-8 text-right'>
                    {value.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tactical */}
      {conditions?.wind_shift && (
        <div>
          <p className='text-sm uppercase py-2'>tactical</p>
          <div className='flex gap-2 p-2 rounded-lg bg-yellow-400/10 border border-yellow-400/40'>
            <AlertTriangle size={16} className='text-yellow-400 shrink-0 mt-0.5'/>
            <div className='flex flex-col gap-0.5'>
              <span className='text-xs font-semibold text-yellow-400'>
                Wind shift in {conditions.wind_shift.in_hours}h
              </span>
              <span className='text-xs text-text-primary'>{conditions.wind_shift.message}</span>
            </div>
          </div>
        </div>
      )}

      {/* simulation results */}
      <div>
        <div className='flex items-center justify-between py-2'>
          <p className="text-sm uppercase py-2">predicted spread area</p>
          {hasResult && (
            <span className='text-sm uppercase font-mono text-text-muted bg-carbon-bg px-1.5 py-0.5 rounded border border-carbon-stroke'>
              {clusterPredictions.length > 0 ? 'Fire cluster' : predictions.length > 1 ? `Max Overall Spread (${predictions.length} Fires)` : 'Single Fire'}
            </span>
          )}
        </div>


        {!hasResult ? (
          <p className="text-xs text-text-disabled">Run the simulation to see spread data</p>
        ) : (
          <div className="flex flex-col gap-2">
            {[1, 3, 6, 12, 24, 48, 72].map((hour) => {
              // const p = predictions[0];
              const tickHour = hour * TICKS_PER_HOUR;
              const radiusses: number[] = [];

              for(const p of runs){
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
          onDeleteLine={onDeleteLine}
        />
      </div>
    </div>
  );
}
