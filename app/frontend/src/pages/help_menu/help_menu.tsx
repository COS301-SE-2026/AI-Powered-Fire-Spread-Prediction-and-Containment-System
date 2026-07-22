import { SideBarLayout } from '../../components/demoSidebar';
import { PageHeader } from '../../components/pageHeader';
import { ActionCard } from '../../components/firefighter/actionCard';
import {Siren, CirclePlay, Headset} from 'lucide-react'
import { useRouter } from 'next/router';
export default function HelpPage() {
const faqs=[
  {
    q:"What exactly do I need to include when reporting a fire?",
    a:"For the prediction model to be useful, please provide: (1) The exact GPS location (drop a pin or enable location services), (2) a recent photo or video showing the smoke column or flame front, (3) an estimate of the size (e.g., small bush, large field), and (4) whether structures or dwellings are immediately threatened."
  },
  {
    q:"What if I accidentally report a controlled agricultural burn or a false alarm?",
    a:'You can "Cancel" or "Update" the report within the app for 15 minutes after submission. Additionally, our administrators verify all reports against satellite hotspot data (VIIRS/MODIS) before activating official response protocols. If it’s a legal controlled burn, please flag it as "Prescribed Burn" when reporting.',
  },
  {
    q:"Can I report a fire if I have no cellphone signal or data?",
    a:'The system requires a data connection to send the GPS and media. ',
  },
  {
    q:"Will the system send me an alert if a fire is spreading toward my house?",
    a:'Yes. If you have registered your residential or farm coordinates in your profile, the system will send geo-fenced push notifications and SMS warnings if the 72-hour predicted perimeter intersects with your property.',
  },
  {
    q:"How far into the future does the system predict the fire spread?",
    a:'The system runs predictive simulations up to 72 hours (3 days) ahead. However, we highly recommend relying on the 6-to-12-hour forecast for tactical ground operations, as atmospheric conditions (especially wind shifts) become increasingly unpredictable beyond that window in South African summers.',
  },
]
  const router = useRouter();
  return (
    
    <SideBarLayout>
      <div className='flex flex-col p-6'>
        <PageHeader
        title="Help Menu"
        subtitle='Find answers, tutorials and support resources for the Fire Away system'
        >
        </PageHeader>
      </div>
      <div className='grid grid-cols-2 '>
        <ActionCard
        title='Tutorials'
        icon={<CirclePlay/>}
        description='Want to learn how this works?'
        onClick={() => router.push('/components/underConstruction')}
        />
        <ActionCard
        title='Help Center'
        icon={<Headset/>}
        description='Need support?'
        onClick={() => router.push('/components/underConstruction')}
        />
      </div>
      <div className='px-6 space-y-3'>
        {faqs.map((faq,index)=>(
          <div 
          key={index}
          className="group hover:bg-white/5 border border-white/5 rounded-[var(--radius-md)] px-3 py-2.5 transition-colors cursor-pointer">
          <div className="flex items-center justify-between">
            <span className="font-display font-bold text-sm uppercase tracking-wide text-white/80 group-hover:text-white transition-colors">{faq.q}</span>
            <span className="text-white/40 group-hover:text-white/80">▼</span>
          </div>
          <div className="overflow-hidden max-h-0 group-hover:max-h-[500px] transition-all duration-300 ease-in-out">
            <p className="pt-2 text-white/70 text-sm">{faq.a}</p>
          </div>
        </div>))}
      </div>
      <div className="mt-10 px-6 pb-6">
        <div className="border-t border-white/10 pt-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-white/70 text-sm">
          <div>
            <span className="font-display font-bold uppercase tracking-wide text-white/90 text-xs">
              <Siren className='w-8 h-8 text-brand-400'/> Emergency Contacts 
            </span>
            <div className="mt-1 space-y-1">
              <p>
                <span className="font-medium text-white/80">National Fire Emergency:</span>{' '}
                <a href="tel:10177" className="text-brand-400 hover:text-brand-300 transition-colors">
                  10177
                </a>
                {' '}(Toll-Free)
              </p>
              <p>
                <span className="font-medium text-white/80">City of Cape Town Fire & Rescue:</span>{' '}
                <a href="tel:0214807700" className="text-brand-400 hover:text-brand-300 transition-colors">
                  021 480 7700
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </SideBarLayout>  
  );
}