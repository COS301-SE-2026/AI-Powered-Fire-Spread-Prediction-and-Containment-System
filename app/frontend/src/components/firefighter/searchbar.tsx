interface TableSearchBarProps {
    readonly value: string;
    readonly onChange: (key: string) => void;
}

export function TableSearchBar({ value, onChange }: TableSearchBarProps) {
  return <label className="input border border-torch/30 rounded-xl focus-within:outline-ignite focus-within:border-none">
            <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
                <g
                    strokeLinejoin="round"
                    strokeLinecap="round"
                    strokeWidth="2.5"
                    fill="none"
                    stroke="currentColor"
                >
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.3-4.3" />
                </g>
            </svg>
            <input type="search" required placeholder="Search reported fires" aria-label="Search reported fires" value={value} onChange={(e) => onChange(e.target.value)}/>
        </label>
}