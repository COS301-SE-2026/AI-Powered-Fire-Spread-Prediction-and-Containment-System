const nav_items = [
  {id: "colours", label: "Colour Pallette"},
  {id: "typography", label: "Typography"},
  {id: "logo", label: "Logo & Iconography"},
  {id: "components", label: "UI Components"},
  {id: "accessibility", label: "Accessibility"},
  {id: "principles", label: "Design Principles"},
];

interface StyleGuideNavProps {
  active: string;
  scrollTo: (id: string) => void;
}

export default function StyleGuideNav({ active, scrollTo }: StyleGuideNavProps) {
  return (
    <nav className="flex flex-col">
      {nav_items.map(({ id, label }) => (
        <button
          key={id}
          onClick={() => scrollTo(id)}
          className={`nav-item ${active === id ? "nav-item--active" : ""}`}
        >
          {label}
          </button>
      ))}
    </nav>
  );
}