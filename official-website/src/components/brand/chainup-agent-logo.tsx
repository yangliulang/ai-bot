import { cn } from "@/lib/utils";

type ChainUpAgentLogoProps = {
  size?: number;
  className?: string;
  /** plate: rounded tile with border; glyph: mark only */
  variant?: "plate" | "glyph";
};

function LogoGlyph() {
  return (
    <>
      <path
        d="M16 9V6.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <circle cx="16" cy="5.25" r="1.2" fill="#6ee7b7" />

      <rect
        x="9.5"
        y="9"
        width="13"
        height="14"
        rx="4"
        stroke="currentColor"
        strokeWidth="2"
      />

      <rect x="12" y="13" width="2.25" height="2.25" rx="0.5" fill="currentColor" />
      <rect x="17.75" y="13" width="2.25" height="2.25" rx="0.5" fill="currentColor" />

      <path
        d="M11.5 19.5 14.25 17.25 17 18.25 20.5 15.75"
        stroke="#6ee7b7"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </>
  );
}

export function ChainUpAgentLogo({
  size = 32,
  className,
  variant = "plate",
}: ChainUpAgentLogoProps) {
  const isPlate = variant === "plate";

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 32 32"
      width={size}
      height={size}
      fill="none"
      aria-hidden={isPlate}
      aria-label={isPlate ? undefined : "ChainUp Agent"}
      role={isPlate ? undefined : "img"}
      className={cn("shrink-0 text-accent", className)}
    >
      {isPlate && (
        <>
          <rect width="32" height="32" rx="8" className="fill-surface" />
          <rect
            x="0.5"
            y="0.5"
            width="31"
            height="31"
            rx="7.5"
            stroke="currentColor"
            strokeOpacity="0.32"
          />
        </>
      )}
      <LogoGlyph />
    </svg>
  );
}
