import React from 'react';
import { RoleRequest, RoleStatus } from '../../types/RoleRequest';
import { statusBadge, BadgeStyle } from './statusBadge';

interface RoleRequestTableProps {
  requests: RoleRequest[];
  filter: 'All' | RoleStatus;
  onView: (request: RoleRequest) => void;
}

export function RoleRequestsTable({ requests, filter, onView }: RoleRequestTableProps) {
  const filtered = requests.filter((req) => filter === 'All' || req.status === filter);

  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-carbon-stroke max-h-170">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              Name
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              Email
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              Role
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              Date
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              Status
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase px-4 py-3">
              View
            </th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-sm font-bold text-error ">
                No requests found
              </td>
            </tr>
          ) : (
            filtered.map((req) => {
              const badge: BadgeStyle = statusBadge[req.status] ?? statusBadge.none;
              const badgeClasses = badge.bg
                ? `${badge.bg} ${badge.text} ${badge.border}`
                : 'bg-carbon-card text-text-primary/50';

              return (
                <tr
                  key={req.request_id}
                  className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-smoke-hover even:bg-carbon-bg/80"
                >
                  <td className="px-4 text-sm text-text-primary">
                    {req.user.name} {req.user.surname}
                  </td>
                  <td className="px-4 text-sm text-text-primary">{req.user.email ?? '-'}</td>
                  <td className="px-4 text-sm text-text-primary capatilize">
                    {req.requested_role}
                  </td>
                  <td className="px-4 text-sm text-text-primary">
                    {new Date(req.created_at).toLocaleDateString('en-ZA', {
                      day: 'numeric',
                      month: 'short',
                    })}
                    {' | '}
                    {new Date(req.created_at).toLocaleTimeString('en-ZA', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${badgeClasses}`}
                    >
                      {req.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => onView(req)}
                      data-testid={`view-request-${req.request_id}`}
                      className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors"
                    >
                      View
                    </button>
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
