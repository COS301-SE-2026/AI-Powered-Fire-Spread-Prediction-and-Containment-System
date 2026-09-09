import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';

const navItems = [
    { label: 'Home', href: '#home', id: 'home'},
    { label: 'About', href: '#about', id: 'about'},
    { label: 'Features', href: '#features', id: 'features'},
    { label: 'Meet the Team', href: '#team', id: 'team'}
]

export function LandingNavbar() {
    const [activeSection, setActiveSection] = useState('home');

    useEffect(() => {
        const sectionElements = navItems
        .map((item) => document.getElementById(item.id))
        .filter((el): el is HTMLElement => el !== null);

        const observerOptions: IntersectionObserverInit = {
            root: null,
            rootMargin: '-20% 0px -60% 0px',
            threshold: 0,
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if(entry.isIntersecting){
                    setActiveSection(entry.target.id);
                }
            });
        }, observerOptions)

        sectionElements.forEach((el) => observer.observe(el));

        return () => {
            sectionElements.forEach((el) => observer.unobserve(el))
        }
    }, []);


  return (
    <div className='fixed top-0 left-0 right-0 z-50 '>
    <div className='navbar bg-base-100 shadow-sm bg-carbon-side/80 backdrop-blur-md rounded-xl border border-carbon-stroke'>
      <div className='navbar-start'>
        <div className='dropdown'>
          <div tabIndex={0} role='button' className='btn btn-ghost lg:hidden'>
            <svg
              xmlns='http://www.w3.org/2000/svg'
              className='h-5 w-5'
              fill='none'
              viewBox='0 0 24 24'
              stroke='currentColor'
            >
              {' '}
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth='2'
                d='M4 6h16M4 12h8m-8 6h16'
              />{' '}
            </svg>
          </div>

          <ul
            tabIndex={-1}
            className='menu menu-sm dropdown-content bg-base-100 rounded-box z-1 mt-3 w-52 p-2 shadow font-display uppercase tracking-wide text-lg'
          >
            {navItems.map((item) => {
                const isActive = activeSection === item.id;
                return(
                    <li key={item.id}>
                        <Link
                            href={item.href}
                            className={`transition-colors ${
                                isActive ? 'text-text-primary font-bold bg-carbon-stroke/50' : 'text-text-muted hover:text-text-primary'
                            }`}
                        >
                            {item.label}
                        </Link>
                    </li>
                );
            })}
          </ul>
        </div>
        <Link
            href='#home'
            className='flex items-center gap-2.5 px-2 py-1 group rounded-lg hover:opacity-90'
        >
            <Image
                src='/images/logo-small.png'
                alt='FireAway logo'
                width={36}
                height={36}
                priority
                className='object-contain transition-transform group-hover:scale-105'
            />
            <span className='font-display font-bold text-xl uppecase tracking-wider text-text-primary group-hover:text-primary transition-colors'>
                FIREAWAY
            </span>
        </Link>
      </div>
      <div className='navbar-center hidden lg:flex'>
        <ul className='menu menu-horizontal px-1 font-display uppercase tracking-wide text-lg'>
          {navItems.map((item) => {
                const isActive = activeSection === item.id;
                return(
                    <li key={item.id}>
                        <Link
                            href={item.href}
                            className={`transition-colors ${
                                isActive ? 'text-text-primary font-bold bg-carbon-stroke/50' : 'text-text-muted hover:text-text-primary'
                            }`}
                        >
                            {item.label}
                        </Link>
                    </li>
                );
            })}
        </ul>
      </div>
      <div className='navbar-end'>
        <Link
            href='/start'
            className='btn btn-primary uppercase text-text-primary font-display text-lg'
        >
            Get Started
        </Link>
      </div>
    </div>
    </div>
  );
}