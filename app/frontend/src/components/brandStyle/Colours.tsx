export default function Colours() {
  return (
    <div className="cs-root">

      {/*colours*/}
      <div className="cs-colours">
        <div className="cs-colour-card">
          <div className="cs-colour" style={{ backgroundColor: 'var(--color-ignite)'}} />
          <div className="cs-colour-body">
            <p className="cs-colour-name">Ignite</p>
            <p className="cs-colour-role">Primary - buttons, links, active states</p>
          </div>
        </div>

        <div className="cs-colour-card">
          <div className="cs-colour" style={{ backgroundColor: 'var(--color-torch)'}} />
          <div className="cs-colour-body">
            <p className="cs-colour-name">Torch</p>
            <p className="cs-colour-role">Accent - warnings, pending states</p>
          </div>
        </div>
         <div className="cs-colour-card">
          <div className="cs-colour" style={{ backgroundColor: 'var(--color-contained)'}} />
          <div className="cs-colour-body">
            <p className="cs-colour-name">Contained</p>
            <p className="cs-colour-role">Accent - success, contained states</p>
          </div>
        </div>
         <div className="cs-colour-card">
          <div className="cs-colour cs-colour--dark" style={{ backgroundColor: 'var(--color-carbon-side)'}} />
          <div className="cs-colour-body">
            <p className="cs-colour-name">Sidebar</p>
            <p className="cs-colour-role">Background - sidebar and nav</p>
          </div>
        </div>
         <div className="cs-colour-card">
          <div className="cs-colour cs-colour--dark" style={{ backgroundColor: 'var(--color-carbon-card)'}} />
          <div className="cs-colour-body">
            <p className="cs-colour-name">Card</p>
            <p className="cs-colour-role">Background - cards and panels</p>
          </div>
        </div>
        <div className="cs-colour-card">
        <div className="cs-colour" style={{ backgroundColor: 'var(--color-text-primary)'}} />
        <div className="cs-colour-body">
          <p className="cs-colour-name">Text</p>
          <p className="cs-colour-role">Text - headings and body</p>
        </div>
      </div>
      <div className="cs-colour-card">
      <div className="cs-colour" style={{ backgroundColor: 'var(--color-text-muted)'}} />
      <div className="cs-colour-body">
        <p className="cs-colour-name">Muted</p>
        <p className="cs-colour-role">Text - secondary and labels</p>
      </div>
    </div>

  </div>
      
      {/* Contrasts*/}
      <div className="cs-contrast">
        <div className="cs-contrast-header">
          <p className="cs-contrast-title">Contrast Ratios - WCAG AA</p>
        </div>

      <div className="cs-contrast-row cs-contrast-row--even cs-contrast-row--bordered">
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-text-primary)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-carbon-bg)'}} />
          </div>
          <p className="cs-contrast-pair">Text on Base</p>
          <p className="cs-contrast-ratio">16.4:1</p>
          <p className="cs-contrast-result cs-contrast-result--pass">Pass</p>
        </div> 
      
      <div className="cs-contrast-row cs-contrast-row--odd cs-contrast-row--bordered">
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--text-muted)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-carbon-bg)'}} />
          </div>
          <p className="cs-contrast-pair">Muted on Base</p>
          <p className="cs-contrast-ratio">8.58:1</p>
          <p className="cs-contrast-result cs-contrast-result--pass">Pass</p>
        </div> 
      <div className="cs-contrast-row cs-contrast-row--even cs-contrast-row--bordered">
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-ignite)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-carbon-bg)'}} />
          </div>
          <p className="cs-contrast-pair">Ignite on Base</p>
          <p className="cs-contrast-ratio">6:1</p>
          <p className="cs-contrast-result cs-contrast-result--pass">Pass</p>
        </div> 
      <div className="cs-contrast-row cs-contrast-row--odd cs-contrast-row--bordered">
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-torch)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-carbon-card)'}} />
          </div>
          <p className="cs-contrast-pair">Torch on Card</p>
          <p className="cs-contrast-ratio">9.62:1</p>
          <p className="cs-contrast-result cs-contrast-result--pass">Pass</p>
        </div>
      <div className="cs-contrast-row cs-contrast-row--even cs-contrast-row--bordered">
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-contained)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-carbon-card)'}} />
          </div>
          <p className="cs-contrast-pair">Contained on Card</p>
          <p className="cs-contrast-ratio">5.42:1</p>
          <p className="cs-contrast-result cs-contrast-result--pass">Pass</p>
        </div> 
      <div className="cs-contrast-row cs-contrast-row--odd" >
        <div className="cs-contrast-chips">
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-text-primary)'}} />
            <span className="cs-chip" style={{ backgroundColor: 'var(--color-ignite)'}} />
          </div>
          <p className="cs-contrast-pair">Text on Ignite</p>
          <p className="cs-contrast-ratio">3.97:1</p>
          <p className="cs-contrast-result cs-contrast-result--warn">Fail</p>
        </div>
      </div>

    </div>
  );
}
      