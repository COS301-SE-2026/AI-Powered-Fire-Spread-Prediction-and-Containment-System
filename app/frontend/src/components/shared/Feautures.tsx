'use client';

import React from "react";

interface FeautureCard {
    id: string;
    number: string;
    title: string;
    description: string;
    colSpan: string;
    accentColor: string;
    badgeBg: string;
    badgeBorder: string;
    hoverBorder: string;
    tags: string[];
}

const featureData: FeautureCard[] = [
    { 
        id: 'fire-spread-prediction',
        number: '01',
        title: 'Calculate Fire Spread',
        description: 
            'Calculate the hourly spread of a fire up to 72 hours into the future.',
        colSpan: 'md:col-span-2',
        accentColor: 'text-primary',
        badgeBg: 'bg-primary/10',
        badgeBorder: 'border-primary/30',
        hoverBorder: 'hover:border-primary/50',
        tags: ['VECTOR RENDERING', 'GPU ACCELERATED']
    },
    { 
        id: 'offline-sync',
        number: '02',
        title: 'Offline Action Sync',
        description: 
            'Automatic background caching, and replay queues to keep incident reports and safe-point bookmarks when connection is lost.',
        colSpan: 'md:col-span-1',
        accentColor: 'text-secondary',
        badgeBg: 'bg-secondary/10',
        badgeBorder: 'border-secondary/30',
        hoverBorder: 'hover:border-secondary/50',
        tags: ['INDEXEDDB ENGINE']
    },
    { 
        id: 'telemetry',
        number: '03',
        title: 'Multi-Variable Telemetry',
        description: 
            'Live weather telemetry as well as a live map that shows the verified fire incidents near you.',
        colSpan: 'md:col-span-1',
        accentColor: 'text-torch',
        badgeBg: 'bg-torch/10',
        badgeBorder: 'border-torch/30',
        hoverBorder: 'hover:border-torch/50',
        tags: ['WEATHER', 'NEARBY']
    },
    { 
        id: 'fire-reporting',
        number: '04',
        title: 'Report Nearby Fires',
        description: 
            'Report fires nearby to help keep your community informed.',
        colSpan: 'md:col-span-2',
        accentColor: 'text-primary',
        badgeBg: 'bg-primary/10',
        badgeBorder: 'border-primary/30',
        hoverBorder: 'hover:border-primary/50',
        tags: ['GEOSPATIAL PIN', 'PHOTO UPLOAD']
    },
    { 
        id: 'custom-weather-prediction',
        number: '05',
        title: 'Purpose Built Weather Prediction',
        description: 
            'Predicts the weather using a custom built Neural Network.',
        colSpan: 'md:col-span-2',
        accentColor: 'text-secondary',
        badgeBg: 'bg-secondary/10',
        badgeBorder: 'border-secondary/30',
        hoverBorder: 'hover:border-secondary/50',
        tags: ['LSTM', 'REAL-TIME FORECAST']
    },
    { 
        id: 'containment-line',
        number: '06',
        title: 'Log Containment Lines',
        description: 
            'Log containment lines near fires to see how it effects the spread.',
        colSpan: 'md:col-span-1',
        accentColor: 'text-torch',
        badgeBg: 'bg-torch/10',
        badgeBorder: 'border-torch/30',
        hoverBorder: 'hover:border-torch/50',
        tags: ['TACTICAL TOOL', 'BARRIER SIMULATION']
    }
]

export function Features() {
    return (
        <div className='max-w-7xl mx-auto w-full'>
            {/* header */}
            <div className='text-center max-w-2xl mx-auto mb-16'>
                <span className='text-base font-mono uppercase tracking-widest text-torch mb-2 inline-block'>
                    Tactical Capabilities
                </span>
                <h2 className='text-3xl sm:text-5xl font-extrabold tracking-tight mb-4 text-text-primary'>
                    Engineerd for Extreme Conditions
                </h2>
                <p className='text-text-muted text-base sm:text-lg'>
                    Everything filed commanders, community leaders, and first responders need in one unified program.
                </p>
            </div>

            {/* feautures grid */}
            <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
                {featureData.map((item) => (
                    <div key={item.id} className={`${item.colSpan} p-8 rounded-2xl bg-carbon-card border border-carbon-stroke ${item.hoverBorder} transition-all group flex flex-col justify-between shadow-xl`}>
                        <div>
                            <div className={`w-12 h-12 rounded-lg ${item.badgeBg} border ${item.badgeBorder} flex items-center justify-center font-mono font-bold ${item.accentColor} mb-6`}>
                                {item.number}
                            </div>
                            <h3 className='text-2xl font-display font-bold text-text-primary mb-2'>
                                {item.title}
                            </h3>
                            <p className='text-text-muted text-sm leading-relaxed max-w-xl'>
                                {item.description}
                            </p>
                        </div>
                        <div className='mt-8 pt-4 border-t border-carbon-stroke/60 flex items-center justify-between text-xs font-mono text-flare'>
                            {item.tags.map((tag, idx) => (
                                <span key={idx} className={item.tags.length === 1 ? 'text-text-muted' : ''}>
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}