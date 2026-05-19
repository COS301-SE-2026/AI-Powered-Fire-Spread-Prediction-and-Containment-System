import { ChevronRight } from "lucide-react";

const mockReports = [
    { id: 1, location: 'Pretoria West', distance: '1.2 km', status: 'Active', time: "1 hr ago" },
    { id: 2, location: 'Atteridgeville', distance: '3.5 km', status: 'Pending', time: "1 hr ago" },
    { id: 3, location: 'Laudium', distance: '5.1 km', status: 'Contained', time: "1 hr ago" },
    { id: 4, location: 'Soshanguve', distance: '8.7 km', status: 'Active', time: "1 hr ago" },
    { id: 5, location: 'Centurion', distance: '12.3 km', status: 'Pending', time: "1 hr ago" },
];

const statusColor = (s: string) => ({
    Active: 'bg-ignite/20 text-flare border border-ignite/30',
    Pending: 'bg-torch/20 text-torch border border-torch/30',
    Contained: 'bg-humidity/20 text-humidity border border-humidity/30',
}[s] ?? 'bg-carbon-card text-neutral/50');
export function NearbyReports() {
    return(
        <div className="flex flex-col gap-2">
        {mockReports.map((report) => (
            <div key={report.id} className="flex items-center justify-between bg-base-200 rounded-lg px-4 py-5 hover:bg-base-300 cursor-pointer transition-colors">
                <div>
                    <p className="font-semibold text-sm">{report.location}</p>
                    <p className="text-xs opacity-50">{report.distance} · {report.time}</p>
                </div>

                <div className="flex items-center gap-2">
                    <span className={`badge px-3 py-1 rounded-full ${statusColor(report.status)}`}>
                        {report.status}
                    </span>
                    <ChevronRight className="size-4 opacity-30" />
                </div>
        </div>
        ))}
        </div>
    );
}