import { ReactNode } from 'react';

interface ColourGroupProps {
    title: string;
    children: ReactNode;
    columns: 3 | 4;
}

export function ColourGroup({ title, children, columns }: ColourGroupProps) {
    let gridClass = "";

    if (columns === 3){
        gridClass = "grid grid-cols-1 sm:grid-cols-3";
    } else {
        gridClass = "grid grid-cols-2 sm:grid-cols-4";
    }

    return (
        <div className="mb-8">
            <h3 className="mb-4">{title}</h3>
            <div className={`${gridClass} gap-4`}>
                {children}
            </div>
        </div>
    );
}