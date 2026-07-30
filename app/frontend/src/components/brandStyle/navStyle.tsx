const className =  "py-2.5 px-4 rounded-lg flex items-center text-sm font-medium tracking-wide text-text-primary/80 hover:text-text-primary hover:bg-smoke-hover active:scale-[0.98] transition-all";

export default function StyleGuideNav() {
  return (
    <nav className="flex flex-col gap-1 w-56 shrink-0 h-screen sticky top-0 px-4 py-8 border-r border-carbon-stroke bg-carbon-side">
      <a href="#colours" className={className}>Colours</a>
      <a href="#typography" className={className}>Typography</a>
      <a href="#logo" className={className}>Logo & Iconography</a>
      <a href="#components" className={className}>UI Components</a>
      <a href="#accessibility" className={className}>Accessibility</a>
      <a href="#principles" className={className}>Design Principles</a>
    </nav>
  );
}