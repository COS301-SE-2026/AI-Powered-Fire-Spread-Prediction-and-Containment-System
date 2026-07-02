import React, { useState } from 'react';
import { ActionCard } from './actionCard';
import { FileWarning, PenLine, TrendingUp, ClipboardPlus} from 'lucide-react'
import { useRouter } from 'next/router';

export function QuickActions(){
    const router = useRouter();
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        
        <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
            {/* Grid of action cards */}
            <ActionCard icon={<ClipboardPlus/>} title="View all reports" description="View team on map" onClick={() => router.push("/firefighter/reported-fires")}/> {/* takes you to reported fires page */}
            <ActionCard icon={<FileWarning/>} title="Report a fire" description="New fire location" onClick={() => setIsModalOpen(true)}/>
            <ActionCard icon={<PenLine/>} title="Log containment line" description="Draw live on map" onClick={() => {}}/> {/* still need to figure out plan for drawing lines */}
            <ActionCard icon={<TrendingUp/>} title="Simulate fires" description="View AI prediction" onClick={() => router.push("/firefighter/simulation")}/> {/* takes you to fire simulation page */}
        </div>
    );   
}
<ClipboardPlus />