const mockReports = [
    { id: 1, location: 'Pretoria West', distance: '1.2 km', status: 'Active' },
    { id: 2, location: 'Atteridgeville', distance: '3.5 km', status: 'Pending' },
    { id: 3, location: 'Laudium', distance: '5.1 km', status: 'Contained' },
    { id: 4, location: 'Soshanguve', distance: '8.7 km', status: 'Active' },
    { id: 5, location: 'Centurion', distance: '12.3 km', status: 'Pending' },
];

export function NearbyReports () {
    const statusColor = (s) => ({
        Active: 'badge-error',
        Pending: 'bagde-warning',
        Contained: 'badge-success',
    }[s] ?? 'badge-ghost')

    return(
        <div className="overflow-x-auto">
        <table className="table table-zebra table-sm">
            <thead>
                <tr>
                    <th>Location</th>
                    <th>Distance</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {mockReports.map((report) => (
                    <tr key={report.id}>
                        <td>{report.location}</td>
                        <td>{report.distance}</td>
                        <td>
                            <span className={`badge bagde-sm ${statusColor(report.status)}`}>
                                {report.status}
                            </span>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
    );
}