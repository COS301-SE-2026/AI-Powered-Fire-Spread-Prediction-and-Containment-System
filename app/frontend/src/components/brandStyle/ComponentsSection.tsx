import Button from '../Button';
import ReportDetailsForm from '../reportfire/Reportdetailsform';
import { QuickActions } from '../firefighter/quickActions';
import { EnvironmentWidgets } from '../firefighter/weatherStats';
import { NearbyReports } from '../firefighter/nearbyReports';
import { statusBadge } from '../admin/statusBadge';

export default function ComponentsSection() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '48px' }}>

      {/* Buttons */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Buttons
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
            <Button variant="dark"  className="h-11 min-h-[44px] px-4">View Map</Button>
            <Button variant="red"   className="h-11 min-h-[44px] px-4">Reject</Button>
            <Button variant="ghost" className="h-11 min-h-[44px] px-4">Cancel</Button>
            <Button variant="fire"  className="h-11 min-h-[44px] px-4" disabled>Unavailable</Button>
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>dark · red · ghost · fire (disabled) — min touch target 44px</p>
          </div>
        </div>
      </div>

      {/* Badges */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Status Badges
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)', display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
            {(['pending', 'approved', 'rejected', 'revoked'] as const).map((status) => {
              const badge = statusBadge[status];
              return (
                <span
                  key={status}
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${badge.bg} ${badge.text} ${badge.border}`}
                >
                  {status}
                </span>
              );
            })}
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>pending · approved · rejected · revoked — used on report and admin cards</p>
          </div>
        </div>
      </div>

      {/* Environment Widgets */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Environment Widgets
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)' }}>
            <EnvironmentWidgets />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Wind · Temperature · Fire Danger · Humidity — used on the Firefighter Dashboard</p>
          </div>
        </div>
      </div>

      {/* Nearby Reports */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Nearby Reports
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)' }}>
            <NearbyReports />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Scrollable list · each row shows location, distance, time, and a Badge · used on Firefighter Dashboard</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Quick Actions
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)' }}>
            <QuickActions />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Action grid on the Firefighter Dashboard · each action maps to a primary workflow</p>
          </div>
        </div>
      </div>

      {/* Report Form */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Report Details Form
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)' }}>
            <ReportDetailsForm />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Location · Description · Attach Evidence · Submit — inputs use carbon-input background with carbon-stroke border</p>
          </div>
        </div>
      </div>

    </div>
  );
}