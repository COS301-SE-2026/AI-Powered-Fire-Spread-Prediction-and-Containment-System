export function LandingNavbar() {
  return (
    <div className="p-8">
    <div className="navbar bg-base-100 shadow-sm bg-carbon-side/80 backdrop-blur-md rounded-xl border border-carbon-stroke">
      <div className="navbar-start">
        <div className="dropdown">
          <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {' '}
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h8m-8 6h16"
              />{' '}
            </svg>
          </div>
          <ul
            tabIndex={-1}
            className="menu menu-sm dropdown-content bg-base-100 rounded-box z-1 mt-3 w-52 p-2 shadow font-display uppercase tracking-wide text-lg"
          >
            <li>
              <a className='text-text-muted hover:text-text-primary'>Home</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>About</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>How it works</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>Features</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>Meet the team</a>
            </li>
          </ul>
        </div>
        <a className="btn btn-ghost text-xl">daisyUI</a>
      </div>
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1 font-display uppercase tracking-wide text-lg">
          <li>
              <a className='text-text-muted hover:text-text-primary'>Home</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>About</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>How it works</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>Features</a>
            </li>
            <li>
              <a className='text-text-muted hover:text-text-primary'>Meet the team</a>
            </li>
        </ul>
      </div>
      <div className="navbar-end">
        <a className='btn btn-primary uppercase text-text-primary font-display text-lg'>Get Started</a>
      </div>
    </div>
    </div>
  );
}
