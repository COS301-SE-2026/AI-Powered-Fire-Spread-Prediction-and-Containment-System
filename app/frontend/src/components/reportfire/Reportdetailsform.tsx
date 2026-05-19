import { useRef, useState, useEffect } from "react";
import { Crosshair, Paperclip, Check } from "lucide-react";
import Button from "../Button";

export type ReportFormData = {
  location: string;
  description: string;
  photo: File | null;
};

type Props = {
  location?: string;
  onSubmit?: (data: ReportFormData) => void;
};

const baseInput =
  "w-full bg-white/10 border border-white/20 rounded-md text-sm text-white placeholder-white/30 focus:outline-none focus:border-[#E84500] focus:bg-white/15 transition-colors";

export default function ReportDetailsForm({ location = "", onSubmit }: Props) {
  const [editableLocation, setEditableLocation] = useState(location);
  const [description, setDescription] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditableLocation(location);
  }, [location]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit?.({ location: editableLocation, description, photo });
  }

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col">
      
      {/* ── HEADER MODULE SECTION ── */}
      <h2
        className="text-xl font-bold mb-4"
        style={{ fontFamily: "var(--font-display)", color: "var(--color-primary-content)" }}
      >
        Report details
      </h2>

      {/* ── FORM ELEMENTS PANEL BODY WITH COHESIVE INTER-SPACE ── */}
      <div className="flex flex-col gap-5">
        
        {/* Location */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-semibold text-white">Location</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={editableLocation}
              onChange={(e) => setEditableLocation(e.target.value)}
              placeholder="Drop a pin or type your address"
              className={`${baseInput} h-10 px-3`}
            />
            <button
              type="button"
              title="Use my current location"
              className="h-10 w-10 shrink-0 flex items-center justify-center bg-white/10 hover:bg-white/15 border border-white/20 text-white rounded-md transition-colors"
            >
              <Crosshair size={15} />
            </button>
          </div>
        </div>

        {/* Description */}
        <div className="flex flex-col gap-1.5">
          <label className="flex items-baseline gap-2">
            <span className="text-sm font-semibold text-white">Description</span>
            <span className="text-xs text-white/40">optional</span>
          </label>
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="E.g., Surface line fire spreading northeast toward residential properties..."
            className={`${baseInput} px-3 py-2.5 leading-relaxed resize-none`}
          />
        </div>

        {/* Attach Evidence */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-semibold text-white">Attach Evidence</label>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className={`h-10 w-full flex items-center justify-center gap-2 rounded-md border text-sm transition-colors ${
              photo
                ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                : "bg-white/5 border-dashed border-white/20 text-white/50 hover:bg-white/10 hover:text-white/80"
            }`}
          >
            {photo ? (
              <>
                <Check size={14} strokeWidth={2.5} />
                <span className="truncate max-w-[200px] font-mono text-xs">{photo.name}</span>
              </>
            ) : (
              <>
                <Paperclip size={14} />
                <span>Attach Image</span>
              </>
            )}
          </button>
        </div>

        {/* Submit */}
        <div className="pt-4 border-t border-white/10 mt-1">
          <Button type="submit" variant="fire" className="w-full">
            Submit Fire Report
          </Button>
        </div>

      </div>
    </form>
  );
}