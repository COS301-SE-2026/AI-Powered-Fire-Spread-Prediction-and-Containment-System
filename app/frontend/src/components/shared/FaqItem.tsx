'use client';

import React, { useId, useState } from 'react';

interface FaqItemProps {
    readonly question: string;
    readonly answer: React.ReactNode;
}

export default function FaqItem({ question, answer }: Readonly<FaqItemProps>){
    const [open, setOpen] = useState(false);
    const panelId = useId();

    return (
        <div className={`border border-white/5 rounded-[var(--radius-md)] transition-colors ${open ? 'bg-white/5' : 'hover:bg-white/5'}`}>
            <button
                type='button'
                onClick={() => setOpen((o) => !o)}
                aria-expanded={open}
                aria-controls={panelId}
                className='w-full flex items-center justify-between gap-4 px-3 py-2.5 text-left cursor-pointer'
            >
                <span className={`font-display font-bold text-sm uppercase tracking-wide transition-colors ${open ? 'text-white' : 'text-white/80'}`}>
                    {question}
                </span>
                <span
                    aria-hidden='true'
                    className={`shrink-0 transition-transform duration-300 ${open ? 'rotate-180 text-white/80' : 'text-white/40'}`}
                >
                    ▼
                </span>
            </button>
            <div
                id={panelId}
                className={`overflow-hidden transition-all duration-300 ease-in-out ${open ? 'max-h-[31.25rem]' : 'max-h-0'}`}
            >
                <p className='px-3 pb-2.5 text-white/70 text-sm'>{answer}</p>
            </div>
        </div>
    );
}