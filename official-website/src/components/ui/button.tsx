"use client";

import { cn } from "@/lib/utils";
import { type ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "telegram";
type Size = "sm" | "md" | "lg";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
};

const variants: Record<Variant, string> = {
  primary:
    "bg-accent text-zinc-950 hover:bg-accent-hover active:scale-[0.98] shadow-[0_0_0_1px_color-mix(in_srgb,var(--accent)_40%,transparent)]",
  secondary:
    "border border-border bg-surface-elevated hover:border-accent/30 text-foreground active:scale-[0.98]",
  ghost: "hover:bg-surface-elevated text-muted hover:text-foreground active:scale-[0.98]",
  telegram:
    "bg-[#2AABEE] text-white hover:bg-[#229ED9] active:scale-[0.98] shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-5 text-sm font-medium",
  lg: "h-12 px-7 text-base font-medium",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-full transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);

Button.displayName = "Button";
