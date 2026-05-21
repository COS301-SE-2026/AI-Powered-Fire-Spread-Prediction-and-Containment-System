import {
  LayoutDashboard, Flame, Map, BookAlert, ShieldAlert, Settings,
  Wind, Thermometer, Droplets, UserCircle, LogOut, PlusCircle,
  AlertTriangle, Radio, Navigation,
} from 'lucide-react';

export default function LogoSection() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

      {/* Logo variants */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>

        {/* Large logo */}
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ height: '160px', backgroundColor: 'var(--color-carbon-side)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src="/images/logo-large.png" alt="Fireaway large logo" style={{ height: '80px', objectFit: 'contain' }} />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-card)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#EDEAE5', marginBottom: '2px' }}>logo-large.png</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Sidebar expanded · min-width 120px</p>
          </div>
        </div>

        {/* Small logo */}
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ height: '160px', backgroundColor: 'var(--color-carbon-side)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src="/images/logo-small.png" alt="Fireaway small logo" style={{ height: '48px', objectFit: 'contain' }} />
          </div>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-card)', borderTop: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#EDEAE5', marginBottom: '2px' }}>logo-small.png</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>Sidebar collapsed · 40×48px</p>
          </div>
        </div>

      </div>

      {/* Placement rules */}
      <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderBottom: '1px solid var(--color-carbon-stroke)' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            Placement & Sizing Rules
          </p>
        </div>
        {[
          'Always place on dark backgrounds - carbon-side (#0C0F1A) or darker',
          'Show icon-only when sidebar is collapsed (92px wide)',
          'Show wordmark + icon when sidebar is expanded (256px wide)',
          'Never rotate, stretch, or recolour the logo',
          'Minimum clear space: equal to the height of the flame icon on all sides',
        ].map((rule, i, arr) => (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              padding: '12px 16px',
              backgroundColor: i % 2 === 0 ? 'var(--color-carbon-card)' : 'var(--color-carbon-input)',
              borderBottom: i < arr.length - 1 ? '1px solid var(--color-carbon-stroke)' : 'none',
            }}
          >
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '13px', color: '#A0A8B8', lineHeight: 1.5 }}>{rule}</p>
          </div>
        ))}
      </div>

      {/* Icon library */}
      <div>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '16px' }}>
          Icon Library - Lucide React
        </p>
        <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderBottom: '1px solid var(--color-carbon-stroke)' }}>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '13px', color: '#A0A8B8', lineHeight: 1.6 }}>
              All icons use the Lucide React library at 24×24px in nav and 20×20px inline.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '1px', backgroundColor: 'var(--color-carbon-stroke)' }}>
            {[
              { Icon: LayoutDashboard, name: 'LayoutDashboard', usage: 'Dashboard nav'    },
              { Icon: Flame,           name: 'Flame',           usage: 'Fire / alerts'    },
              { Icon: Map,             name: 'Map',             usage: 'Map views'        },
              { Icon: BookAlert,       name: 'BookAlert',       usage: 'Reports'          },
              { Icon: ShieldAlert,     name: 'ShieldAlert',     usage: 'Admin / roles'    },
              { Icon: Settings,        name: 'Settings',        usage: 'System settings'  },
              { Icon: Wind,            name: 'Wind',            usage: 'Wind data'        },
              { Icon: Thermometer,     name: 'Thermometer',     usage: 'Temperature'      },
              { Icon: Droplets,        name: 'Droplets',        usage: 'Humidity'         },
              { Icon: UserCircle,      name: 'UserCircle',      usage: 'User / login'     },
              { Icon: LogOut,          name: 'LogOut',          usage: 'Logout'           },
              { Icon: PlusCircle,      name: 'PlusCircle',      usage: 'Add / report'     },
              { Icon: AlertTriangle,   name: 'AlertTriangle',   usage: 'Danger / hazard'  },
              { Icon: Radio,           name: 'Radio',           usage: 'Comms / dispatch' },
              { Icon: Navigation,      name: 'Navigation',      usage: 'Location / route' },
            ].map(({ Icon, name, usage }) => (
              <div
                key={name}
                style={{
                  padding: '16px',
                  backgroundColor: 'var(--color-carbon-card)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px',
                  textAlign: 'center',
                }}
              >
                <Icon size={24} color="#EDEAE5" strokeWidth={2} />
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#EDEAE5', lineHeight: 1.3 }}>{name}</p>
                <p style={{ fontFamily: 'var(--font-body)', fontSize: '10px', color: '#5A6278' }}>{usage}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}