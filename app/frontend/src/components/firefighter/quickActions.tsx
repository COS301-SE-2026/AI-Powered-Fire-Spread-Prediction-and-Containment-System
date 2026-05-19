import React from 'react';
import { ActionCard } from './actionCard';
import { Users, FileWarning, PenLine, TrendingUp } from 'lucide-react'

export function QuickActions(){
    return (
        
        <div className="grid grid-cols-2 grid-rows-2 gap-3">
            {/* Grid of action cards */}
            <ActionCard icon={<Users/>} title="Unit position" description="View team on map" />
            <ActionCard icon={<FileWarning/>} title="Report a fire" description="New fire location" />
            <ActionCard icon={<PenLine/>} title="Log containment line" description="Draw live on map" />
            <ActionCard icon={<TrendingUp/>} title="Spread Simulation" description="View AI prediction" />
        </div>
    );   
}
