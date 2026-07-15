import React from "react";

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

export function PageHeader({title, subtitle, actions}: Readonly<PageHeaderProps>){
    return(
        <header className="mb-4 flex items-center justify-between">
            <div>
                <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
                    {title}
                </h1>
                {subtitle && (
                    <p className="text-sm text-neutral/50 font-medium">
                        {subtitle}
                    </p>
                )}
            </div>
            {actions}
        </header>
    );
}