import {
  LayoutDashboard,
  Flame,
  Map,
  BookAlert,
  ShieldAlert,
  Settings,
  Wind,
  Thermometer,
  Droplets,
  UserCircle,
  User,
  LogOut,
  PlusCircle,
  AlertTriangle,
  TrendingUp,
  ChevronDown,
  ChevronRight,
  MicrochipIcon,
  HeartIcon,
  LineChartIcon,
  DownloadCloudIcon,
  Users,
  FileWarning,
  PenLine,
  Paperclip,
  Check,
  House,
  MessageCircleWarning,
  MessagesSquare,
  Info,
} from 'lucide-react';
import { IconCard } from './iconCard';

export function IconGrid() {
  return (
    <div className="overflow-hidden rounded-md border border-carbon-stroke">
      <div className="border-b border-carbon-stroke px-4 py-3">
        <p className="font-mono text-xs font-semibold uppercase tracking-widest text-smoke">
          Icon Library - Lucide React
        </p>
      </div>
      <div className="grid grid-cols-2 gap-px bg-carbon-stroke sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        <IconCard Icon={LayoutDashboard} name="Dashboard" usage="Dashboard nav" />
        <IconCard Icon={Flame} name="Flame" usage="Fire / alerts" />
        <IconCard Icon={Map} name="Map" usage="Map views" />
        <IconCard Icon={BookAlert} name="BookAlert" usage="Reports" />
        <IconCard Icon={ShieldAlert} name="ShieldAlert" usage="Admin / roles" />
        <IconCard Icon={Settings} name="Settings" usage="System settings" />
        <IconCard Icon={Wind} name="Wind" usage="Wind data" />
        <IconCard Icon={Thermometer} name="Thermometer" usage="Temperature" />
        <IconCard Icon={Droplets} name="Droplets" usage="Humidity" />
        <IconCard Icon={UserCircle} name="UserCircle" usage="User / login" />
        <IconCard Icon={User} name="User" usage="Registered user role" />
        <IconCard Icon={LogOut} name="LogOut" usage="Logout" />
        <IconCard Icon={PlusCircle} name="PlusCircle" usage="Add / report" />
        <IconCard Icon={AlertTriangle} name="AlertTriangle" usage="Danger / hazard" />
        <IconCard Icon={TrendingUp} name="TrendingUp" usage="Analytics" />
        <IconCard Icon={ChevronDown} name="ChevronDown" usage="Dropdown expand/collapse" />
        <IconCard Icon={ChevronRight} name="ChevronRight" usage="Navigate / view more" />
        <IconCard Icon={MicrochipIcon} name="MicrochipIcon" usage="Predictions completed" />
        <IconCard Icon={HeartIcon} name="HeartIcon" usage="Model health" />
        <IconCard Icon={LineChartIcon} name="LineChartIcon" usage="Prediction confidence" />
        <IconCard Icon={DownloadCloudIcon} name="DownloadCloudIcon" usage="Data source sync" />
        <IconCard Icon={Users} name="Users" usage="Unit position" />
        <IconCard Icon={FileWarning} name="FileWarning" usage="Report a fire" />
        <IconCard Icon={PenLine} name="PenLine" usage="Log containment line" />
        <IconCard Icon={Paperclip} name="Paperclip" usage="Attach evidence" />
        <IconCard Icon={Check} name="Check" usage="Confirmed / attached" />
        <IconCard Icon={House} name="House" usage="Home nav" />
        <IconCard Icon={MessageCircleWarning} name="MessageWarning" usage="Notifications" />
        <IconCard Icon={MessagesSquare} name="MessagesSquare" usage="Community" />
        <IconCard Icon={Info} name="Info" usage="Tooltip / help text" />
      </div>
    </div>
  );
}
