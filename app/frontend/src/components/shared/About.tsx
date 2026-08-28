'use client';

import React from 'react';

const benchmarks = [
    {
        value: '< 30s',
        label: 'Simulation Latency',
        detail: 'Fast Cellular Automaton inference delivered immediatly upon incident verification.'
    },
    {
        value: '10m²',
        label: 'Spatial Resolution',
        detail: 'High-precision probability grids computed across various time steps.'
    },
    {
        value: '100%',
        label: 'Action Auditability',
        detail: 'Complete offline logging and synchronization for tactical containment barriers.'
    },
    {
        value: '99.9%',
        label: 'Mission Availiablity',
        detail: 'Resilient architecture designed for low-connectivity rural and field deployments.'
    }
]

const users = [
    {
        title: 'Community & Landowners',
        description: 'Instant anonymous fire reporting, live fire radius inspection, and proximity based evactuation alerts.',
        tag: 'PUBLIC SAFETY',
        border: 'border-primary/40'
    },
    {
        title: 'Firefighters',
        description: 'Tactical dashboard, with interactive maps, barrier logging, and a dynamic AI fire spread simulation.',
        tag: 'TACTICAL OPS',
        border: 'border-secondary/40'
    },
    {
        title: 'Incident Coordinators',
        description: 'Role-based access control, multi-source NASA FIRMS verification, and complete incident archives.',
        tag: 'INCIDENT COMMAND',
        border: 'border-torch/40'
    }
]

export function About() {
    return(
        <div className='max-w-7xl mx-auto w-full'>
            <div className='text-center max-w-3xl mx-auto mb-16'>
                <span className='text-base font-mono uppercase tracking-widest text-torch mb-3 inline-block'>
                    Our Mission & Standards
                </span>
                <h2 className='text-3xl sm:text-5xl font-extrabold tracking-tight mb-4 text-text-primary font-display'>
                    BRIDGING SATELLITE TELEMETRY & TACTICAL INTERVENTION
                </h2>
                <p className='text-text-muted text-base sm:text-lg'>
                    Developed with safe and efficient emergency responses in mind.
                </p>
            </div>

            <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-20'>
                {benchmarks.map((item,idx) => (
                    <div key={idx} className='p-6 rounded-2xl bg-carbon-card border border-carbon-stroke hover:border-primary/40 transition-colors shadow-lg'>
                        <span className='font-display font-extrabold text-4xl sm:text-5xl text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary block mb-2'>
                            {item.value}
                        </span>
                        <h3 className='font-display font-bold text-lg text-text-primary mb-1'>
                            {item.label}
                        </h3>
                        <p className='text-text-muted text-xs leading-relaxed font-body'>
                            {item.detail}
                        </p>
                    </div>
                ))}
            </div>

            <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
                {users.map((item, idx) => (
                    <div key={idx} className={`p-8 rounded-2xl bg-carbon-side/60 border ${item.border} flex flex-col justify-between shadow-xl backdrop-blur-sm`}>
                        <div>
                            <span className='text-sm font-mono font-bold px-2.5 py-1 rounded bg-carbon-bg border border-carbon-stroke text-flare mb-6 inline-block tracking-wider'>
                                {item.tag}
                            </span>
                            <h3 className='font-display font-bold text-2xl text-text-primary mb-3'>
                                {item.title}
                            </h3>
                            <p className='text-text-muted text-sm leading-relaxed font-body'>
                                {item.description}
                            </p>
                        </div>
                        <div className='mt-6 pt-6 border-t border-carbon-stroke/40 text-base font-mono text-text-disabled uppercase'>
                            END-TO-END COORDINATION
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}