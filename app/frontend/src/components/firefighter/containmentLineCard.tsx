import { CircleCheck,Pencil } from "lucide-react";

interface LoggedLine {
    line: string
    direction: string;
    info: string;
}

interface CardListProp {
    readonly card_data?: LoggedLine[];
}

const mock_data: LoggedLine[] = [
    { line: "Line A", direction: "NW Flank",  info: "Logged 8 min ago · 320m" },
    { line: "Line B", direction: "East Ridge", info: "Logged 24 min ago · 580m" },
    { line: "Line C", direction: "South Perimeter", info: "Logged 1 hr ago · 210m" },
];

export function LoggedContainmentLine({card_data = mock_data}: CardListProp) {
  return <div className="flex flex-col gap-1 p-1">
            {card_data.map((items) =>(
                <div key={items.line} className="flex items-center justify-between gap-1 p-1 border border-carbon-stroke rounded-xl">
                    <div className="flex items-center gap-2">
                        <Pencil size={16}/>
                        <div className="flex flex-col items-start gap-0.5">
                            <span className="text-xs text-text-primary">{items.line} - {items.direction}</span>
                            <span className="text-xs text-text-muted">{items.info}</span>
                        </div>
                    </div>

                    <div>
                        <CircleCheck size={16}/>
                    </div>
                </div>
            ))}
        </div>
}