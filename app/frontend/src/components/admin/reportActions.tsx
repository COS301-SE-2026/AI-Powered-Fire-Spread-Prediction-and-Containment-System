import React from "react";
import { Card } from "./Card";

export function ReportActions() {
    return (
        <Card title="">
            <p className="text-text-muted text-sm">
                Review the fire report details and either verify it as a legitimate incident or reject it if it appears to be inaccurate or a false report.
            </p>
            <div className="flex flex-row gap-3 mt-3">
                <button className="flex-1 h-11 bg-ignite hover:bg-ignite/90 active:scale-[0.98] text-white font-display font-bold tracking-widest uppercase text-sm rounded-md transition-all shadow-lg shadow-ignite/20">
                    Verify 
                </button>
                <button className="flex-1 h-11 bg-ignite hover:bg-ignite/90 active:scale-[0.98] text-white font-display font-bold tracking-widest uppercase text-sm rounded-md transition-all shadow-lg shadow-ignite/20">
                    Reject 
                </button>
            </div>
        </Card>
    )
}