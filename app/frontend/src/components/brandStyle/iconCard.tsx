import type { LucideIcon } from 'lucide-react';

interface IconCardProps {
    Icon: LucideIcon;
    name: string;
    usage: string;
}

export function IconCard({ Icon, name, usage }: Readonly<IconCardProps>) {
  return <div className="flex flex-col items-center gap-2 bg-carbon-card p-4 text-center">
            <Icon size={30} className="text-text-primary" strokeWidth={2} />
            <p className="font-mono text-sm text-flare">{name}</p>
            <p className="font-body text-sm text-smoke">{usage}</p>
        </div>
}