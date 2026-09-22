import { Sparkles, Check, X } from 'lucide-react';
import type { SuggestedContainmentLine } from '@/types/ContainmentLines';

interface SuggestedLineCardProps {
    suggestion: SuggestedContainmentLine;
    onAccept: () => void;
    onDismiss: () => void;
    accepting?: boolean;
}

export function SuggestedLineCard({
    suggestion,
    onAccept,
    onDismiss,
    accepting = false,
}: SuggestedLineCardProps) {
    const { 
        length_m: lengthM,
        build_time_min: buildTimeMin,
        margin_min: marginMin,
    } = suggestion;
    return (
        <div className="flex flex-col gap-2 p-3 border border-purple-400/40 rounded-xl bg-purple-400/10">
            <div className="flex items-center gap-2">
                <Sparkles size={16} className="text-purple-400 shrink-0" />
                <span className="text-xs font-semibold text-purple-300 uppercase tracking-wide">
                    Suggested containment line
                </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-text-primary">
                <div className="flex flex-col">
                    <span className="text-text-muted">Length</span>
                    <span>
                        {lengthM >= 1000 ? `${(lengthM / 1000).toFixed(2)} km` : `${lengthM.toFixed(0)} m`}
                    </span>
                </div>
                <div className="flex flex-col">
                    <span className="text-text-muted">Build time</span>
                    <span>{buildTimeMin.toFixed(0)} min</span>
                </div>
                <div className="flex flex-col">
                    <span className="text-text-muted">Margin</span>
                    <span className={marginMin < 30 ? 'text-yellow-400' : 'text-green-400'}>
                        {marginMin.toFixed(0)} min
                    </span>
                </div>
            </div>

            <div className="flex gap-2 pt-1">
                <button
                    type="button"
                    onClick={onAccept}
                    disabled={accepting}
                    className="btn btn-xs btn-outline flex-1 flex items-center justify-center gap-1 disabled:opacity-50"
                >
                    <Check size={14} />
                    {accepting ? 'Adding...' : 'Accept & rerun'}
                </button>
                <button
                    type="button"
                    onClick={onDismiss}
                    disabled={accepting}
                    className="btn btn-xs btn-ghost flex-1 flex items-center justify-center gap-1 disabled:opacity-50"
                >
                    <X size={14} />
                    Dismiss
                </button>
            </div>
        </div>
    );
}