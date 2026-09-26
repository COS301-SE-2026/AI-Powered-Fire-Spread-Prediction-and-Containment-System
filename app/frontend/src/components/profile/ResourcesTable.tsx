import React from 'react';
import { useRouter } from 'next/router';
import { ResourceTable, Status  } from '../../types/Resource';
import { ResourceDropdown } from './ResourceDropdown';
import { FormatDate } from '../../lib/FormatDate';
import { RESOURCE_GROUPS, GROUP_BY_RESOURCE } from '../../lib/ResourceGroups';


interface MyResourcesTableProps {
  readonly resources: ResourceTable[];
  readonly filter: 'All' | Status;
  readonly onStatusChange: (resourceId: string, status: Status) => void;
}

export function MyResourcesTable({ resources, filter, onStatusChange }: MyResourcesTableProps) {
  const filtered = resources
    .filter((r) => filter === 'All' || r.status === filter)
    .sort((a, b) => new Date(b.availableFrom).getTime() - new Date(a.availableFrom).getTime());

  const router = useRouter();

  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-carbon-stroke">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-16 py-3">
              Resource
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Capacity
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Location
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Available From
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Contact
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Status
            </th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-sm font-bold text-error">
                No requests found
              </td>
            </tr>
          ) : (
            filtered.map((resources) => {
                const group = RESOURCE_GROUPS[GROUP_BY_RESOURCE[resources.resource]];
                const Icon = group.icon;
                return (
                <tr
                    key={resources.id}
                    className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-surface-hover even:bg-carbon-bg/80"
                >
                <td className="px-4 text-sm text-text-primary">
                    <div className="flex items-center gap-5">
                      <span
                        className="flex size-7 shrink-0 items-center justify-center rounded-lg"
                        style={{ background: group.color }}
                      >
                        <Icon className="size-4 text-carbon-bg" />
                      </span>
                      {resources.resource === 'other' ? resources.otherResource : resources.resource}
                    </div>
                  </td>
                    <td className="px-4 text-sm text-text-primary">{resources.resource === 'other' ? resources.otherResource : resources.resource}</td>
                    <td className="px-4 text-sm text-text-primary">{resources.capacity} {resources.capacityUnit === 'other' ? resources.otherCapacity : resources.capacityUnit}</td>
                    <td className="px-4 text-sm text-text-primary">{resources.location}</td>
                    <td className="px-4 text-sm text-text-primary">{FormatDate(resources.availableFrom)}</td>
                    <td className="px-4 text-sm text-text-primary">{resources.contact}</td>
                    <td className="px-4 py-3">
                    <ResourceDropdown id={resources.id} status={resources.status} onStatusChange={onStatusChange} />
                    </td>
                </tr>
                );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
