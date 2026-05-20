import React, { Children, useState } from 'react';
import { BookAlert, Map, LayoutDashboard, Settings, LogOut,
    ShieldAlert, Flame, User, UserCircle,
    ChevronDown, BookAlertIcon, CheckSquare,
    Bell, Users, PlusCircle,
    Icon

} from 'lucide-react';

const NavLink = ({ icon: Icon, label}: { icon: any, label: string}) => (
    <button className="py-2.5 px=4 w-full rounded-lg flex items-center justify-center group-hover:justify-start gap-4 hover:bg-smoke-hover active:scale-[0.98] transition-all text-left text-neutral/80 hoverLtext-neutral">
        <Icon className="size-5 shrink-0 ml-1 group-hover:ml-6 transition-all"/>
        <span className="text-sm font-medium tracking-wide hidden group-hover:inline opacity-0 group-hover:opacity-100 tranistion-opacity duration-200 whitespace-nowrap">
            {label}
        </span>
    </button>
);

const SideBarDropdown = ({ title, icon: Icon, defaultOpen = false, children }: { 
    title: string; 
    icon: React.ElementType;
    defaultOpen?: boolean;
    children: React.ReactNode;
}) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return(
        <li className="w-full flex flex-col">
            <button onClick={() => setIsOpen(!isOpen)} className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active-scale[0.98] transition-all w-full text-left">
                <Icon className={`size-6 shrink-0 transition-colors ${isOpen ? 'text-ignite' : 'text-neutral/70 group-hover:text-ignite'}`} />

                <span className="test-sm font-semibold tracking-wide text-neutral flex-1 hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                    {title}
                </span>

                <ChevronDown className={`size-4 text-neutral/50 hidden group-hover:block transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}/>
            </button>

            {/* dropdown content */}
            <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-96 opacity-100 ml-1' : 'max-h-0 opacity-0'}`}>
                <div className="flex flex-col space-y-1 w-full">
                    {children}
                </div>
            </div>
        </li>
    );
};
