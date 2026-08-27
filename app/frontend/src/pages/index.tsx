'use client';

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/router";
import EmberField from '../components/ui/EmberEffect';
import { LandingNavbar } from "@/components/shared/LandingNavbar";

export default function LandingPage() {
  const router = useRouter();

  return(
    <div className='relative min-h-screen w-full max-w-full bg-carbon-bg'>
      <LandingNavbar/>

      {/* Section for the top op landing page */}
      <section id='home' className="min-h-screen">

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
      <section id='team' className="min-h-screen">

      </section>

      {/* Takes you to the login/register page */}
      <section id='get-started' className="min-h-screen">

      </section>

      {/* General footer not sure what to add here yet*/}
      <footer>

      </footer>
    </div>
  )
}