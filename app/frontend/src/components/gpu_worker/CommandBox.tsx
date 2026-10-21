import React, { useState } from 'react';
import { Check } from 'lucide-react';

export function CommandBox({ command }: { command : string }){
    const [copied, setCopied] = useState(false);
    const copy = async () => {
        try {
            await navigator.clipboard.writeText(command);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // user can still select-all the command
        }
    };

    return (
        <div className='relative rounded-sm border border-carbon-stroke bg-carbon-input p-3'>
            <pre className='font-mono text-xs text-text-primary whitespace-pre-wrap break-all pr-16 select-all'>{command}</pre>
            <button
                type='button'
                onClick={copy}
                className='absolute right-3 top-3 rounded-box border border-carbon-stroke bg-[#1a2030] hover:bg-smoke-hover px-3 py-1 text-xs font-medium text-text-primary transition-colors'            
            >
                {copied ? <span className='flex items-center gap-1 text-humidity'><Check className='size-3.5'/> Copied</span>: 'Copy'}
            </button>
        </div>
    );
}