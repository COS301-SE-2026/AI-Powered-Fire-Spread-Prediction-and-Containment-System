import { Siren, CirclePlay, Headset } from 'lucide-react';
import { useRouter } from 'next/router';
import { PageHeader } from "../layout/pageHeader";
import { ActionCard } from "../firefighter/actionCard";

export default function HelpPage() {
  const faqs = [
    {
      id: '1',
      q: 'What exactly do I need to include when reporting a fire?',
      a: 'For the prediction model to be useful, please provide: (1) The exact GPS location (drop a pin or enable location services), (2) a recent photo or video showing the smoke column or flame front, (3) an estimate of the size (e.g., small bush, large field), and (4) whether structures or dwellings are immediately threatened.',
    },
    {
      id: '2',
      q: 'What if I accidentally report a controlled agricultural burn or a false alarm?',
      a: 'You can "Cancel" or "Update" the report within the app for 15 minutes after submission. Additionally, our administrators verify all reports against satellite hotspot data (VIIRS/MODIS) before activating official response protocols. If it’s a legal controlled burn, please flag it as "Prescribed Burn" when reporting.',
    },
    {
      id: '3',
      q: 'Can I report a fire if I have no cellphone signal or data?',
      a: 'The system requires a data connection to send the GPS and media. ',
    },
    {
      id: '4',
      q: 'Do I need an account to view the map or report a fire?',
      a: 'No. Both the live fire map and the fire reporting form are available to anonymous visitors. Creating a free account (Registered User) additionally gives you the AI spread-prediction overlay and proximity push notifications.',
    },
    {
      id: '5',
      q: 'How does a report get automatically verified?',
      a: "A report is auto-verified when either (1) two independent reports come in for the same location, or (2) it matches a NASA FIRMS satellite hotspot. Until then, it sits as 'Pending' and no alerts are sent. Firefighters and Administrators can also manually verify or reject a pending report.",
    },
    {
      id: '6',
      q: "What happens to a fire report once it's verified?",
      a: 'Verification automatically triggers the AI fire-spread simulation, publishes the fire to the live map for all users, and dispatches push notifications to registered users in the surrounding risk zone — all within seconds.',
    },
    {
      id: '7',
      q: 'What data does the AI use to predict how a fire will spread?',
      a: 'The simulation engine combines wind speed and direction, temperature, humidity, precipitation, and vegetation dryness with terrain slope and vegetation type to produce a probability grid for the 1, 3, 6, and 24-hour horizons.',
    },
    {
      id: '8',
      q: 'How reliable are the spread predictions?',
      a: 'The model is benchmarked against at least 20 historical fires and must achieve an Intersection-over-Union of 0.30 or better for its 6-hour prediction versus the actual burned area. If live data becomes stale (over an hour old), predictions are flagged as lower quality so you know to treat them cautiously.',
    },
    {
      id: '9',
      q: "What happens if wind or weather data isn't available when a fire is verified?",
      a: "The system never leaves you with a blank map. It falls back to the last known good data, and if the simulation still can't complete in time, it shows a wind-biased estimate around the ignition point rather than no prediction at all.",
    },
    {
      id: '10',
      q: 'Can I still use the app if my device loses signal in the field?',
      a: "Yes, for viewing. Map tiles and the most recent spread prediction are cached automatically while you're online, so you can still see the last known situation offline — you'll see an 'Offline' banner, and the app quietly refreshes once you're back on data. Submitting a new report still requires a live connection.",
    },
    {
      id: '11',
      q: "What can firefighters do that a regular registered user can't?",
      a: 'Firefighters get a tactical dashboard with AI-recommended containment spots, live wind direction, and their own GPS position on the map. They can also draw containment lines directly on the map — each one is logged with GPS coordinates and a timestamp, and automatically triggers the simulation to re-run around it.',
    },
  ];
  const router = useRouter();
  return (
    <>
      <div className="flex flex-col p-6">
        <PageHeader
          title="Help Menu"
          subtitle="Find answers, tutorials and support resources for the Fire Away system"
          showIcons
        />
      </div>
      <div className="flex flex-col p-6 gap-3  ">
        {/* Tutorials */}
        <details
          className="collapse bg-carbon-bg border border-carbon-card rounded-lg transition-all group"
          name="tutorial-accordion"
          open
        >
          <summary className="collapse-title font-semibold p-4 flex items-center gap-3 cursor-pointer hover:bg-carbon-card/30 rounded-t-lg transition-colors">
            <div className="size-10 rounded-lg bg-carbon-bg border border-carbon-card flex items-center justify-center text-white/60 group-hover:text-ignite group-hover:border-ignite/30 transition-colors shrink-0">
              <CirclePlay />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-white text-sm tracking-wide">Getting Started</span>
              <span className="text-xs text-white/50 font-medium">Learn the basics</span>
            </div>
            {/* Optional expand/collapse indicator */}
          </summary>
          <div className="collapse-content p-4 pt-0">
            <div className="flex flex-col md:flex-row gap-6 mt-4">
              {/* Large screenshot */}
              <div className="flex-1 bg-carbon-card rounded-lg border border-carbon-card overflow-hidden">
                <img
                  src="/images/firefighter_report_circled.png"
                  alt="Tutorial screenshot"
                  className="w-full h-auto object-cover"
                />
              </div>
              {/* Description next to it */}
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-white font-bold text-base mb-2">Step-by-step guide</h4>
                <p className="text-white/70 text-sm leading-relaxed">
                  You can report fires using the Report button. This takes you to a page where you
                  can report a fire by giving a description and a photo for verification.
                </p>
              </div>
            </div>
          </div>
          <div className="collapse-content p-4 pt-0">
            <div className="flex flex-col md:flex-row gap-6 mt-4">
              <div className="flex-1 bg-carbon-card rounded-lg border border-carbon-card overflow-hidden">
                <img
                  src="/images/dash_line_circled.png"
                  alt="Logging a containment line on the live fire map"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-white font-bold text-base mb-2">Log a containment line</h4>
                <p className="text-white/70 text-sm leading-relaxed">
                  From the dashboard's Live Fire Map, select "Log containment line" under Quick
                  Actions, then draw directly on the map to mark where a line has been established.
                  Use "Clear Lines" in the top-right corner if you need to undo and redraw.
                </p>
              </div>
            </div>
          </div>
          <div className="collapse-content p-4 pt-0">
            <div className="flex flex-col md:flex-row gap-6 mt-4">
              <div className="flex-1 bg-carbon-card rounded-lg border border-carbon-card overflow-hidden">
                <img
                  src="/images/sim_draw.png"
                  alt="Drawing a containment line in the Fire Simulation view"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-white font-bold text-base mb-2">
                  Simulate a containment strategy
                </h4>
                <p className="text-white/70 text-sm leading-relaxed">
                  Open "Simulate fires" from Quick Actions to reach the Fire Simulation view, then
                  tap "Draw Containment" to sketch a proposed containment line onto the predicted
                  spread map before running the model.
                </p>
              </div>
            </div>
          </div>
          <div className="collapse-content p-4 pt-0">
            <div className="flex flex-col md:flex-row gap-6 mt-4">
              <div className="flex-1 bg-carbon-card rounded-lg border border-carbon-card overflow-hidden">
                <img
                  src="/images/sim_run.png"
                  alt="Running the fire spread simulation"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-white font-bold text-base mb-2">Run the simulation</h4>
                <p className="text-white/70 text-sm leading-relaxed">
                  Once your containment line is drawn, tap "RUN" to simulate how it affects the
                  fire's predicted spread area, using the current weather inputs shown alongside the
                  map.
                </p>
              </div>
            </div>
          </div>
          <div className="collapse-content p-4 pt-0">
            <div className="flex flex-col md:flex-row gap-6 mt-4">
              <div className="flex-1 bg-carbon-card rounded-lg border border-carbon-card overflow-hidden">
                <img
                  src="/images/sim_time.png"
                  alt="Scrubbing the simulation timeline"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-white font-bold text-base mb-2">Step through the timeline</h4>
                <p className="text-white/70 text-sm leading-relaxed">
                  Drag the timeline slider at the bottom of the simulation panel to see how the
                  predicted spread area changes hour by hour, from now out to 24 hours ahead.
                </p>
              </div>
            </div>
          </div>
        </details>

        {/* Help center (I put the fire department link only) */}
        <ActionCard
          title="Help Center"
          description="Need professional suppport?"
          icon={<Headset />}
          onClick={() => router.push('https://www.fireservices.gov.za/Pages/Home.aspx')}
        />
      </div>
      {/* FAQ's */}
      <div className="px-6 space-y-3">
        {faqs.map((faq, index) => (
          <div
            key={faq.id}
            className="group hover:bg-white/5 border border-white/5 rounded-[var(--radius-md)] px-3 py-2.5 transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="font-display font-bold text-sm uppercase tracking-wide text-white/80 group-hover:text-white transition-colors">
                {faq.q}
              </span>
              <span className="text-white/40 group-hover:text-white/80">▼</span>
            </div>
            <div className="overflow-hidden max-h-0 group-hover:max-h-[500px] transition-all duration-300 ease-in-out">
              <p className="pt-2 text-white/70 text-sm">{faq.a}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-10 px-6 pb-6">
        <div className="border-t border-white/10 pt-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-white/70 text-sm">
          <div>
            <span className="font-display font-bold uppercase tracking-wide text-white/90 text-xs">
              <Siren className="w-8 h-8 text-brand-400" /> Emergency Contacts
            </span>
            <div className="mt-1 space-y-1">
              <p>
                <span className="font-medium text-white/80">National Fire Emergency:</span>{' '}
                <a
                  href="tel:10177"
                  className="text-brand-400 hover:text-brand-300 transition-colors"
                >
                  10177
                </a>{' '}
                (Toll-Free)
              </p>
              <p>
                <span className="font-medium text-white/80">City of Cape Town Fire & Rescue:</span>{' '}
                <a
                  href="tel:0214807700"
                  className="text-brand-400 hover:text-brand-300 transition-colors"
                >
                  021 480 7700
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
