'use client';

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/router";
import EmberField from '../components/ui/EmberEffect';
import { LandingNavbar } from "@/components/shared/LandingNavbar";
import { Team } from "@/components/shared/Team";

export default function LandingPage() {
  const router = useRouter();

  return(
    <div className='relative min-h-screen w-full max-w-full bg-carbon-bg'>
      
      <div className='global-atmos'>
        <div className='ga-bloom-primary'/>
        <div className='ga-bloom-secondary'/>
        <div className='ga-bloom-tertiary'/>
        <EmberField density={45}/>
      </div>

      <LandingNavbar/>

      {/* Section for the top op landing page */}
      <section id='home' className="relative z-10 min-h-screen flex flex-col items-center justify-center text-center px-6 pt-32 pb-16 max-w-5xl mx-auto">
        
        <div className='relative mb-8 group'>
          <div className='absolute -inset-6 bg-gradient-to-tr from-primary/30 via-secondary/20 to-accent/10 rounded-full blur-3xl group-hover:scale-110 transition-transform duration-700 pointer-events-none '/>

          <Image
            src='/images/logo-large.png'
            alt="FireAway Large Logo"
            width={400}
            height={400}
            priority
            className='relative object-contain mx-auto drop-shadow-[0_0_40px_rgba(255,73,4,0.45)] transition-transform duration-500 group-hover:scale-110'
          />
        </div>

        <h1 className='text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6'>
          PREDICT THE FLAME. <br/>
          <span className='text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent'>
            PROTECT YOUR NEIGHBOURS.
          </span>
        </h1>

        <p className='text-text-muted text-base sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed font-body'>
          Machine Learning powered geospatial atmospheric and boundary forecasting built to give firefighters, community leaders, and farmers critical response time.
        </p>

        <div className='flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto'>
          <Link
            href='/start'
            className='w-full sm:w-auto btn btn-primary uppercase px-10 text-base font-display tracking-wider shadow-lg shadow-primary/25 text-lg hover:shadow-primary/45 transition-all text-white'
          >
            GET STARTED
          </Link>
          <Link
            href='#about'
            className='w-full sm:w-auto btn btn-ghost bg-carbon-side/70 border border-carbon-stroke hover:bg-carbon-stroke text-text-primary px-8 text-base font-display uppercase tracking-wide backdrop-blur-sm'
          >
            Learn More
          </Link>
        </div>
      </section>

      {/* Section for about of our project */}
      <section id='about' className="min-h-screen">

      </section>

      {/* Takes you to the help menu or a rough idea of how it works */}
      <section id='how-it-works' className="min-h-screen">

      </section>

      {/* Section on the features of our app*/}
      <section id='features' className="min-h-screen">

      </section>

      {/* Section on team and who we are */}
      <section id='team' className="min-h-screen p-12">
        <div className='w-full max-w-6xl mx-auto px-6'>
          {/* Section header */}
          <div className='text-center max-w-2xl mx-auto mb-16'>
            <span className='text-5xl font-display uppercase tracking-widest text-primary mb-2 inline-block'>
              The Team
            </span>
            <h2 className='text-3xl sm:text-5xl font-extrabold tracking-tight mb-4 text-text-primary'>
              Meet the people behind FireAway
            </h2>
          </div>
          <Team/>
        </div>
        
      </section>

      {/* General footer not sure what to add here yet*/}
      <footer className="footer sm:footer-horizontal footer-center bg-base-300 text-base-content p-4">
        <aside>
          <p>Copyright © {new Date().getFullYear()} - Group Elephant Limited</p>
        </aside>
      </footer>
    </div>
  )
}