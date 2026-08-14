import { LogoCard } from "./logoCard";

export function LogoGrid() {
  return <div className="grid grid-cols-2 gap-3">
            <LogoCard src="/images/logo-large.png" filename="logo-large.png" note="Wordmark + icon (expanded sidebar)" imgHeight="h-35"/>
            <LogoCard src="/images/logo-small.png" filename="logo-small.png" note="Icon only (collapsed sidebar)" imgHeight="h-35"/>
            <LogoCard src="/images/logo-monochrome.png" filename="logo-monochrome.png" note="Single colour (print/watermark use)" imgHeight="h-35"/>
            <LogoCard src="/images/logo-inverse.png" filename="logo-inverse.png" note="White background (light mode or emails)" imgHeight="h-105" bg="bg-white"/>  
        </div>
}