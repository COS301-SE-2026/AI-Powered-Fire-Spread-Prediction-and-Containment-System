interface LayerSwitchProps {
    readonly label: string;
    readonly checked: boolean;
    readonly onChange: () => void;
    readonly className?: string;
}

export function LayerSwitch({
    label,
    checked,
    onChange,
    className = '',
}: {
    readonly label: string;
    readonly checked: boolean;
    readonly onChange: () => void;
    readonly className?: string;
}) {
    return (
        <label className={`flex items-center gap-2 cursor-pointer select-none ${className}`}>
            <span className='text-sm font-medium text-text-muted'>{label}</span>
            <button
                type='button'
                role='switch'
                aria-checked={checked}
                onClick={onChange}
                className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${checked ? 'bg-ignite' : 'bg-carbon-stroke'}`}
            >
                <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-md transition-transform ${checked ? 'translate-x-4' : 'translate-x-1'}`}/>
            </button>
        </label>
    );
}