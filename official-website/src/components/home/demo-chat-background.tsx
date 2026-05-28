"use client";

import { memo } from "react";

function DemoChatBackgroundInner() {
  return (
    <div
      className="demo-chat-bg pointer-events-none absolute inset-0 overflow-hidden rounded-[inherit]"
      aria-hidden
    >
      <div className="demo-chat-gradient absolute inset-0 rounded-[inherit]" />
    </div>
  );
}

export const DemoChatBackground = memo(DemoChatBackgroundInner);
