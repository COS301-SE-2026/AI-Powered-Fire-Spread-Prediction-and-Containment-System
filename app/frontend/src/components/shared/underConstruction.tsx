import { useRouter } from "next/router";
import { ArrowLeft } from "lucide-react";

interface UnderConstructionProps {
  message?: string;
}

export function UnderConstruction({
  message = 'This page is still under development',
}: Readonly<UnderConstructionProps>) {
  const router = useRouter();
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-1 p-6 text-center">
      <img src="/images/logo-large.png" alt="FireAway" className="w-64 md:w-150 object-contain" />
      <img
        src="/images/Under_construction.png"
        alt="Coming Soon"
        className="w-full max-w-lg object-contain"
      />

      <p className="text-sm text-text-primary/50 max-w-sm">{message}</p>
      <button onClick={() => router.back()} className='mt-4 flex items-center gap-2 px-4 py-2 text-sm font-semibold hover:text-white rounded-lg hover:bg-smoke-hover transition-colors'>
        <ArrowLeft className='size-4' />
        Back
      </button>
    </div>
  );
}
