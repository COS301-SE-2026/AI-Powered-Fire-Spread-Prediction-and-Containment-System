interface ScoreBadgeProps {
    score: number | null;
}

function getDotColor(score: number): string {
    if (score >= 70){
        return 'bg-success';
    }
    if (score >= 40){
        return 'bg-warning';
    }
    return 'bg-error';
}

export function ScoreBadge({ score }: ScoreBadgeProps){
    let label = 'New';
    let dot = 'bg-text-muted';

    if (score !== null){
        label = `${Math.round(score)}%`;
        dot = getDotColor(score);
    }
    return (
        <span data-testid="score-badge" className="inline-flex items-center gap-2 text-sm font-semibold tabular-nums text-text-primary">
            <span className={`size-2 rounded-full ${dot}`} />
            {label}
        </span>
    );
}