import React from 'react';
import Link from 'next/link';
import { LucideIcon } from 'lucide-react';

interface NavLinkProps {
  icon: LucideIcon | React.ElementType;
  label: string;
  href?: string;
}

export function NavLink({
  icon: Icon,
  label,
  href,
}: Readonly<NavLinkProps>) {
  const content = (
    <>
      <Icon className="size-5 shrink-0 ml-1 group-hover:ml-6 transition-all" />
      <span className="text-sm font-medium tracking-wide hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
        {label}
      </span>
    </>
  );

  const className =
    'py-2.5 px-4 w-full rounded-lg flex items-center justify-center group-hover:justify-start gap-4 hover:bg-smoke-hover active:scale-[0.98] transition-all text-left text-text-primary hover:text-text-primary';

  return href ? (
    <Link href={href} className={className}>
      {content}
    </Link>
  ) : (
    <button type="button" className={className}>
      {content}
    </button>
  );
}
