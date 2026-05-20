import { ChevronRight } from "lucide-react";

const mockReports = [
    { id: 1,  location: 'Pretoria West',    distance: '1.2 km',  status: 'Active',    time: '8 min ago'  },
    { id: 2,  location: 'Atteridgeville',   distance: '3.5 km',  status: 'Pending',   time: '15 min ago' },
    { id: 3,  location: 'Laudium',          distance: '5.1 km',  status: 'Contained', time: '32 min ago' },
    { id: 4,  location: 'Soshanguve',       distance: '8.7 km',  status: 'Active',    time: '41 min ago' },
    { id: 5,  location: 'Centurion',        distance: '12.3 km', status: 'Pending',   time: '1 hr ago'   },
    { id: 6,  location: 'Mamelodi',         distance: '14.6 km', status: 'Active',    time: '1 hr ago'   },
    { id: 7,  location: 'Garsfontein',      distance: '17.2 km', status: 'Contained', time: '2 hrs ago'  },
    { id: 8,  location: 'Hatfield',         distance: '6.4 km',  status: 'Pending',   time: '2 hrs ago'  },
    { id: 9,  location: 'Silverton',        distance: '9.8 km',  status: 'Active',    time: '3 hrs ago'  },
    { id: 10, location: 'Wonderboom',       distance: '11.0 km', status: 'Contained', time: '3 hrs ago'  },
    { id: 11, location: 'Eersterust',       distance: '13.3 km', status: 'Pending',   time: '4 hrs ago'  },
    { id: 12, location: 'Irene',            distance: '18.9 km', status: 'Active',    time: '4 hrs ago'  },
    { id: 13, location: 'Lyttelton',        distance: '15.7 km', status: 'Contained', time: '5 hrs ago'  },
    { id: 14, location: 'Mabopane',         distance: '22.1 km', status: 'Active',    time: '6 hrs ago'  },
    { id: 15, location: 'Olivenhoutsdrift', distance: '26.4 km', status: 'Pending',   time: '7 hrs ago'  },
];

const statusColor = (s: string) => ({
    Active: 'bg-ignite/20 text-flare border border-ignite/40',
    Pending: 'bg-torch/20 text-torch border border-torch/35',
    Contained: 'bg-humidity/20 text-humidity border border-humidity/35',
}[s] ?? 'bg-carbon-card text-neutral/50');
export function NearbyReports() {
    return(
        <div className="h-full overflow-y-auto flex flex-col p-2">
        {mockReports.map((report) => (
            <div key={report.id} className="flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors">
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