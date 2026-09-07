import { LocalLine } from '@/types/ContainmentLines';
import { CircleCheck, Pencil, CircleDashed, Trash2 } from 'lucide-react';
import { useMemo } from 'react';

interface LoggedLine {
  id?:string;
  line: string;
  direction: string;
  info: string;
  synced?: boolean;
  source?: LocalLine;
}

interface CardListProp {
  readonly cardData?: LoggedLine[];
  readonly lines?: LocalLine[];
  readonly selectedFireId?: string | null;
  onDeleteLine?: (line: LocalLine) => void;
}

// parses wkt linestring into [lon,lat] coord pairs
function parseWKTCoords(wkt: string): [number, number][]{
  try{
    const raw = wkt.replace(/LINESTRING\s*\(/i, '').replace(/\)/, '').trim(); // returns the four numbers of the wkt string
    if(!raw) return [];
    return raw.split(',').map((pair) => {
      const [lon, lat] = pair.trim().split(/\s+/).map(Number);
      return [lon, lat];
    })
  }catch{
    return [];
  }
}

function calculateLineLenM(coords: [number, number][]): number{
  if(coords.length < 2) return 0;

  const EARTH_RAD_M = 6371000;

  let totalDist = 0;

  for (let i = 0; i < coords.length - 1; i ++){
    const [lon1, lat1] = coords[i];
    const [lon2, lat2] = coords[i + 1];

    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
    const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

    const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) + Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

    totalDist += EARTH_RAD_M * c;
  }

  return Math.round(totalDist);
}

function calculateDirection(coords: [number, number][]): string {
  if(coords.length < 2) return 'Active Barrier';
  const [lon1, lat1] = coords[0];
  const [lon2, lat2] = coords[coords.length - 1];

  const y = Math.sin(((lon2 - lon1) * Math.PI)/180) * Math.cos((lat2 * Math.PI)/180);
  const x = Math.cos((lat1 * Math.PI) / 180) * Math.sin((lat2 * Math.PI) / 180) -
    Math.sin((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.cos(((lon2 - lon1) * Math.PI) / 180);

  const brng = ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;

  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const idx = Math.round(brng/45) % 8;
  return dirs[idx];
}

export function LoggedContainmentLine({ cardData = undefined, lines = [], selectedFireId = null, onDeleteLine = undefined}: CardListProp) {
  const displayItems = useMemo<LoggedLine[]>(() => {
    if (cardData && cardData.length > 0) return cardData;

    if(lines && lines.length > 0) {
      return lines.map((l, idx) => {
        const coords = parseWKTCoords(l.wkt);
        const distM = calculateLineLenM(coords);
        const dir = calculateDirection(coords);
        const formattedDist = distM >= 1000 ? `${(distM / 1000).toFixed(2)} km` : `${distM} m`

        return {
          id: l.localId,
          line: `Line ${String.fromCharCode(65 + (idx % 26))}`,
          direction: dir,
          info: `${l.synced ? 'Logged' : 'Unsaved'} ${formattedDist}`,
          synced: l.synced,
          source: l
        };
      });
    }

    return [];
  }, [cardData, lines])

  if(displayItems.length === 0){
    return (
      <div className='p-3 border border-dashed border-carbon-stroke rounded-xl text-center'>
        <span className='text-xs text-text-muted'>No containment lines logged for this fire</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1 p-1">
      {displayItems.map((items, idx) => (
        <div
          key={items.id ?? items.line ?? idx}
          className="flex items-center justify-between gap-1 p-1 border border-carbon-stroke rounded-xl"
        >
          <div className="flex items-center gap-2">
            <Pencil size={16} />
            <div className="flex flex-col items-start gap-0.5">
              <span className="text-xs text-text-primary">
                {items.line} - {items.direction}
              </span>
              <span className="text-xs text-text-muted">{items.info}</span>
            </div>
          </div>

          <div className='flex items-center gap-1 shrink-0'>
            {items.synced === false ? (
              <CircleDashed size={16} className='text-[#fcba3e]' />
            ) : (
              <CircleCheck size={16} className='text-[#0284c7]'/>
            )}

            {onDeleteLine && items.source && (
              <button
                type='button'
                onClick={() => onDeleteLine(items.source!)}
                className='btn btn-ghost btn-xs px-1 text-red-400 hover:bg-red-400/10'
                title='Remove this containment line'
              >
                <Trash2 size={14}/>
              </button>
            )}
            
          </div>
        </div>
      ))}
    </div>
  );
}
