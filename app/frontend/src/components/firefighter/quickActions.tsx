import React from 'react';
import { ActionCard } from './actionCard';
import { FileWarning, PenLine, TrendingUp, ClipboardPlus} from 'lucide-react'

export function QuickActions(){
    return (
        
        <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
            {/* Grid of action cards */}
            <ActionCard icon={<ClipboardPlus/>} title="View all reports" description="View team on map" /> {/* takes you to reported fires page */}
            <ActionCard icon={<FileWarning/>} title="Report a fire" description="New fire location" />
            <ActionCard icon={<PenLine/>} title="Log containment line" description="Draw live on map" /> 
            <ActionCard icon={<TrendingUp/>} title="Simulate fires" description="View AI prediction" /> {/* takes you to fire simulation page */}
        </div>
    );   
}
<ClipboardPlus />