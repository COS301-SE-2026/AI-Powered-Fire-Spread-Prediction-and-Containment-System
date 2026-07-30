import { ComponentsGroup } from "./componentsGroup";
import { StatusBadge } from "../admin/reportStatusBadge";

export function Table() {
    return (
        <ComponentsGroup title="Fire Reports Table">
            <div className="overflow-x-auto rounded-2xl border border-carbon-stroke w-full max-h-150">
                <table className="table table-pin-rows w-full">
                    <thead>
                        <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Ref</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Location</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Status</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Size</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Reported</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">Reporter</th>
                            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3 whitespace-nowrap">View</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className="[&>td]:border-t [&>td]:border-carbon-stroke hover:bg-carbon-card/50 even:bg-carbon-bg/80">
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">FR-1042</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">Moreleta Park</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap"><StatusBadge status="verified" /></td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">12.4 ha</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">28 Jul | 14:32</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">J. van Wyk</td>
                            <td className="px-4 py-3 whitespace-nowrap">
                                <button type="button" className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-stroke text-text-primary/50 hover:bg-carbon-card hover:text-text-primary transition-colors">
                                    View
                                </button>
                            </td>
                        </tr>
                        <tr className="[&>td]:border-t [&>td]:border-carbon-stroke hover:bg-carbon-card/50 even:bg-carbon-bg/80">
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">FR-1043</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">Faerie Glen</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap"><StatusBadge status="pending" /></td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">5.1 ha</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">28 Jul | 09:14</td>
                            <td className="px-4 text-sm text-text-primary whitespace-nowrap">A. Botha</td>
                            <td className="px-4 py-3 whitespace-nowrap">
                                <button type="button" className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-stroke text-text-primary/50 hover:bg-carbon-card hover:text-text-primary transition-colors">
                                    View
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </ComponentsGroup>
    );
}