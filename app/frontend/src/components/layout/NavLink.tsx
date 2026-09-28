import React from 'react';
import Link from 'next/link';

export function NavLink({
  icon: Icon,
  label,
  href,
  onClick,
}: Readonly<{ icon: React.ComponentType<{ className?: string }>; label: string; href?: string, onClick?: () => void; }>) {
  const content = (
    <>
      <Icon className="size-5 shrink-0 ml-1 lg:group-hover:ml-6 transition-all" />
      <span className="text-sm font-medium tracking-wide inline lg:hidden lg:group-hover:inline opacity-100 lg:opacity-0 lg: group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
        {label}
      </span>
    </>
  );

  const className =
    'py-2.5 px-4 w-full rounded-lg flex items-center justify-start lg:justify-center lg:group-hover:justify-start gap-4 hover:bg-smoke-hover active:scale-[0.98] transition-all text-left text-text-primary hover:text-text-primary';

  if (href){
    return (
      <Link href={href} className={className}>
        {content}
      </Link>
    )
  }

  return (
    <button type="button" onClick={onClick} className={className}>
      {content}
    </button>
  );
}
