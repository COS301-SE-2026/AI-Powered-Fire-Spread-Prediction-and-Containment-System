import { ChevronRight } from "lucide-react";
import React, {useState, useEffect} from "react"
interface FireReport {
    id:string;
    reference_number : string;
    lat:number;
    lng:number;
    location_text: string;
    status: string;
    boundary_radius: number | null;
    submitted_at: string;
    size?: number;
    reporter_name?: string;

}
const timeAgo= (iso:string):string =>{
    const now = new Date();
    const then = new Date(iso);
    const diff = Math.floor((now.getTime()-then.getTime())/1000);
    
    if (diff<60) return 'Just now';

    //3600 is an hour
    if (diff<3600) return `${Math.floor(diff / 60)} min ago`;

    //86400 is a day
    if (diff<86400) return `${Math.floor(diff / 3600)} hr ago`;

    return `${Math.floor(diff/86400)} days ago`
}
const statusColor = (s: string) => ({
    Active: 'bg-ignite/20 text-flare border border-ignite/40',
    Pending: 'bg-torch/20 text-torch border border-torch/35',
    Contained: 'bg-humidity/20 text-humidity border border-humidity/35',
}[s] ?? 'bg-carbon-card text-neutral/50');
export function NearbyReports() {
    const [reports, setReports]= useState<FireReport[]>([]);
    const [loading, setLoading]= useState(true);
    const [error, setError]=useState<string | null>(null);
    const [userLocation, setUserLocation]= useState<{lat:number, lng:number} | null>(null);

    useEffect(() => {
        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition((pos)=>{
                setUserLocation({
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude,
                });
            },
            () =>{}
        );
        
        }
    },[]);
    useEffect(()=>{
        fetch('/api/guests/reported-fires')
        .then((res)=>{
            if(!res.ok) throw new Error('Failed to fetch');
            return res.json();
        })
        .then((data) => setReports(data))
        .catch((err)=> setError(err))
        .finally(() => setLoading(false));
    },[]);
    const getDistance =(lat:number , lng: number): string | null =>{
        if(!userLocation) return null;
        const R= 6371;
        const dLat=(lat - userLocation.lat)*Math.PI/180;
        const dLng=(lng- userLocation.lng)*Math.PI/180;
        //haversine formula 
        const a = 
        Math.sin(dLat/2)**2+
        Math.cos(userLocation.lat*Math.PI/180)*
        Math.cos(lat*Math.PI/180)*
        Math.sin(dLng/2)**2;
        const c = 2*Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const dist = R*c;
        return dist<1? `${(dist*1000).toFixed(0)} m` : `${(dist.toFixed(1))} km`;        
    };

    if(loading){
        return <div className="p-4 text-neutral/50">Loading nearby</div>
    }
    if (error) {
        return <div className="p-4 text-flare">Failed to load reports: {error}</div>;
    }
    if (reports.length === 0) {
        return <div className="p-4 text-neutral/50">No fire reports nearby.</div>;
    }
    const sorted = [...reports].sort(
    (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
    );
    return (
        <div className="h-full overflow-y-auto flex flex-col p-2">
            {sorted.map((report)=>{
                const distance = getDistance(report.lat, report.lng);
                const distanceText = distance ? `${distance} ` : ' ';
                return( 
                    <div 
                    key ={report.id}
                    className= "flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors" >
                        <div>
                            <p className="font-semibold text-sm">{report.location_text}</p>
                            <p className="tex-xs opacity-50">
                                {distanceText}{timeAgo(report.submitted_at)}
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className={`badge px-3 py-1 rounded-full ${statusColor(report.status)}`}>
                                {report.status}
                            </span>
                            <ChevronRight className="size-4 opacity-30"/>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
