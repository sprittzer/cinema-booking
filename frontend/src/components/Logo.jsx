import { Clapperboard } from "lucide-react";

export default function Logo() {
  return (
    <div className="logo">
      <span className="logo-mark">
        <Clapperboard size={18} />
      </span>
      <span className="logo-text">НеКино</span>
    </div>
  );
}
