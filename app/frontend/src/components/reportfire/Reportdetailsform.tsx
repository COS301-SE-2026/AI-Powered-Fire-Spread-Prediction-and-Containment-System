import { useRef, useState, useEffect } from "react";
import { Crosshair, Paperclip, Check, AlertTriangle } from "lucide-react";
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
  "w-full bg-white/10 border rounded-md text-sm text-white placeholder-white/30 focus:outline-none focus:border-[#E84500] focus:bg-white/15 transition-colors";

export default function ReportDetailsForm({ location = "", onSubmit }: Props) {
  const [editableLocation, setEditableLocation] = useState(location);
  const [description, setDescription] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [errors, setErrors] = useState<{ location?: string; photo?: string }>({});
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditableLocation(location);
    if (location && location !== "Click the map to drop a pin") {
      setErrors((prev) => ({ ...prev, location: undefined }));
    }
  }, [location]);

  function reset() {
    setEditableLocation("Click the map to drop a pin");
    setDescription("");
    setPhoto(null);
    setErrors({});
    if (fileRef.current) fileRef.current.value = "";
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: { location?: string; photo?: string } = {};

    if (!editableLocation.trim() || editableLocation === "Click the map to drop a pin") {
      newErrors.location = "Please select an incident location on the map or type an address.";
    }

    const isDesktop = typeof window !== "undefined" && window.innerWidth >= 768;
    if (isDesktop && !photo) {
      newErrors.photo = "Field evidence attachment is mandatory on desktop. Please upload a telemetry image.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    onSubmit?.({ location: editableLocation, description, photo });
    reset();
  }

  function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;

    if (file) {
      if (!file.type.startsWith("image/")) {
        setErrors((prev) => ({
          ...prev,
          photo: "Invalid file type. Only image files (PNG, JPG, WEBP) are permitted.",
        }));
        setPhoto(null);
        if (fileRef.current) fileRef.current.value = "";
        return;
      }

      setPhoto(file);
      setErrors((prev) => ({ ...prev, photo: undefined }));
    }
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

        {/* Location Section */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-semibold text-white">Location</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={editableLocation}
              onChange={(e) => {
                setEditableLocation(e.target.value);
                if (e.target.value.trim()) setErrors((prev) => ({ ...prev, location: undefined }));
              }}
              placeholder="Drop a pin or type your address"
              className={`${baseInput} h-10 px-3 ${
                errors.location ? "border-error/60 focus:border-error" : "border-white/20"
              }`}
            />
            <button
              type="button"
              title="Use my current location"
              className="h-10 w-10 shrink-0 flex items-center justify-center bg-white/10 hover:bg-white/15 border border-white/20 text-white rounded-md transition-colors"
            >
              <Crosshair size={15} />
            </button>
          </div>
          {errors.location && (
            <div className="flex items-center gap-1.5 text-error text-xs font-medium mt-0.5">
              <AlertTriangle size={13} />
              <span>{errors.location}</span>
            </div>
          )}
        </div>

        {/* Description Section */}
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
            className={`${baseInput} border-white/20 px-3 py-2.5 leading-relaxed resize-none`}
          />
        </div>

        {/* ── FIXED ATTACH EVIDENCE CONTAINER (HARD LOCKED TO DESKTOP ONLY) ── */}
        <div className="hidden md:flex md:flex-col gap-1.5">
          <label className="text-sm font-semibold text-white">Attach Evidence</label>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handlePhotoChange}
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className={`h-10 w-full flex items-center justify-center gap-2 rounded-md border text-sm transition-colors duration-150 ${
              photo
                ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                : errors.photo
                ? "bg-error/10 border-dashed border-error/50 text-error/80 hover:bg-error/15"
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
          {errors.photo && (
            <div className="flex items-center gap-1.5 text-error text-xs font-medium mt-0.5">
              <AlertTriangle size={13} />
              <span>{errors.photo}</span>
            </div>
          )}
        </div>

        {/* Submit Button Section */}
        <div className="pt-4 border-t border-white/10 mt-1">
          <Button type="submit" variant="fire" className="w-full">
            Submit Fire Report
          </Button>
        </div>

      </div>
    </form>
  );
}