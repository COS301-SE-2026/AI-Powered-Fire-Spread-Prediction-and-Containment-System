import React from 'react';
import InfoCard from './InfoCard';

const principles = [
  {
    label: 'Button Labels',
    value: 'Verb + Result',
    desc: 'Use verbs as button lables, naming the result that will be achieved once the button is clicked, not the mechanism behind it.',
  },
  {
    label: 'Error Message',
    value: 'Explain, Don\u2019t Alarm',
    desc: 'Never say only "error" or "something went wrong". Expalain clearly what happened and avoid scary language whare it isn\u2019t warrented.',
  },
  {
    label: 'Active-Incident Errors',
    value: 'Fact + Fix Only',
    desc: 'During a live fire alert, the user is only told what went wrong and how to fix it. Everything else is stripped away.',
  },
  {
    label: 'Empty States',
    value: 'Purpose, Reason, Action',
    desc: 'State what the space is for, why it\u2019s currently empty and the one action the user can perform to fill it.',
  },
];

const context = [
  {
    label: 'Active Fire Alert',
    value: 'Urgent',
    desc: 'Straightforward and action-base. No decoration, no delay.',
  },
  {
    label: 'Prediction & Analysis',
    value: 'Measured',
    desc: 'Exact and confident without arrogance, The data makes the decisions.',
  },
  {
    label: 'System Error',
    value: 'Honest',
    desc: 'Specific about what is missing and what needs to be done in this situation.',
  },
  {
    label: 'Training a User',
    value: 'Patient',
    desc: 'Respectful and human. Acknowledge the dangers involved without alarming unnecessarily',
  },
  {
    label: 'Post-Incident Reports',
    value: 'Sober',
    desc: 'Fact-based documentation style. Losses are reported here, so it must stay respectful toward victims',
  },
  {
    label: 'Community-Facing',
    value: 'Warm',
    desc: 'Plain language, no unnecessary techical jargon. Show humanity and empathy.',
  },
];

export default function VoiceAndToneSection() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '48px' }}>
        <h2
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '28px',
            color: '#B0B8C8',
            fontWeight: 700,
            paddingBottom: '16px',
            borderBottom: '1px solid var(--color-carbon-stroke)',
          }}
        >
          Voice
        </h2>
      </div>

      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '18px',
          color: '#B0B8C8',
          maxWidth: '800px',
          lineHeight: '1.75',
          fontWeight: 300,
        }}
      >
        The voice of the project is a calm expert: firm and direct, but never cold. It belongs to a
        trained professional who is familiar with fires and can lead the user through the
        application. The users’ time is respected, and confidence comes through without arrogance
        tainting the voice. Fluff, excessive excitement, and unnecessary jargon are avoided; the
        voice makes its point calmly and lets the user feel confident in the decisions they make on
        the platform.
      </p>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}
      >
        {principles.map(({ label, value, desc }) => (
          <InfoCard key={label} label={label} value={value} desc={desc} />
        ))}
      </div>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}
      >
        {context.map(({ label, value, desc }) => (
          <InfoCard key={label} label={label} value={value} desc={desc} />
        ))}
      </div>
    </div>
  );
}
