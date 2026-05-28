"use client";

import { memo } from "react";

const NODES = [
  { cx: 12, cy: 28, label: "NLU" },
  { cx: 38, cy: 18, label: "Agent" },
  { cx: 62, cy: 32, label: "Gateway" },
  { cx: 86, cy: 22, label: "Coobit" },
  { cx: 48, cy: 52, label: "Confirm" },
] as const;

const EDGES: [number, number][] = [
  [0, 1],
  [1, 2],
  [2, 3],
  [1, 4],
  [4, 3],
];

const FLOATING_CHIPS = [
  {
    id: "btc",
    className: "left-[6%] top-[18%] hero-float-a",
    body: "BTC/USDT",
    value: "96,842.50",
    delta: "+2.34%",
  },
  {
    id: "intent",
    className: "left-[14%] top-[62%] hero-float-b",
    body: "read.market.ticker",
    value: "847ms",
    delta: "P50",
  },
  {
    id: "confirm",
    className: "left-[38%] top-[78%] hero-float-c",
    body: "Type A",
    value: "Pending",
    delta: "await tap",
  },
  {
    id: "eth",
    className: "right-[42%] top-[14%] hero-float-b",
    body: "ETH/USDT",
    value: "3,842.12",
    delta: "-0.87%",
  },
  {
    id: "exec",
    className: "right-[38%] top-[58%] hero-float-a",
    body: "exec_7f3a2c",
    value: "RUNNING",
    delta: "audit",
  },
] as const;

const TICKER_ITEMS = [
  "read.account.balance",
  "write.order.limit",
  "read.market.depth",
  "confirm.type_a",
  "billing.token.consume",
  "scenario.trading.spot",
];

function HeroAgentBackgroundInner() {
  return (
    <div
      className="hero-agent-bg pointer-events-none absolute inset-0 overflow-hidden"
      aria-hidden
    >
      <div className="hero-mesh-blob absolute -left-24 top-1/4 h-[420px] w-[420px] rounded-full bg-accent/[0.06] blur-3xl" />
      <div className="hero-mesh-blob-delay absolute bottom-0 right-[10%] h-[360px] w-[360px] rounded-full bg-accent/[0.04] blur-3xl" />

      <svg
        className="absolute inset-0 h-full w-full opacity-[0.35] md:opacity-45"
        viewBox="0 0 100 64"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="hero-flow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0" />
            <stop offset="50%" stopColor="var(--accent)" stopOpacity="0.6" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {EDGES.map(([from, to], i) => {
          const a = NODES[from];
          const b = NODES[to];
          return (
            <line
              key={`${from}-${to}`}
              x1={a.cx}
              y1={a.cy}
              x2={b.cx}
              y2={b.cy}
              stroke="url(#hero-flow-grad)"
              strokeWidth="0.15"
              className="hero-flow-line"
              style={{ animationDelay: `${i * 0.7}s` }}
            />
          );
        })}

        {NODES.map((node, i) => (
          <g key={node.label}>
            <circle
              cx={node.cx}
              cy={node.cy}
              r="1.2"
              fill="var(--accent)"
              className="hero-node-pulse"
              style={{ animationDelay: `${i * 0.5}s` }}
            />
            <circle cx={node.cx} cy={node.cy} r="0.45" fill="var(--background)" />
          </g>
        ))}
      </svg>

      {FLOATING_CHIPS.map((chip) => (
        <div
          key={chip.id}
          className={`hero-data-chip absolute hidden sm:block ${chip.className}`}
        >
          <span className="font-mono text-[10px] uppercase tracking-wider text-muted">
            {chip.body}
          </span>
          <span className="mt-0.5 block font-mono text-xs font-medium text-foreground/80">
            {chip.value}
          </span>
          <span className="font-mono text-[10px] text-accent/70">{chip.delta}</span>
        </div>
      ))}

      <div className="absolute inset-x-0 bottom-[12%] hidden overflow-hidden md:block">
        <div className="hero-ticker-track flex gap-8 whitespace-nowrap px-4">
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
            <span
              key={`${item}-${i}`}
              className="font-mono text-[11px] tracking-wide text-muted/50"
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      <svg
        className="absolute left-[8%] top-[38%] hidden h-16 w-28 opacity-30 md:block"
        viewBox="0 0 112 48"
        fill="none"
        aria-hidden
      >
        <path
          d="M0 40 L16 32 L32 36 L48 20 L64 24 L80 12 L96 16 L112 8"
          stroke="var(--accent)"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="hero-sparkline-draw"
        />
      </svg>
    </div>
  );
}

export const HeroAgentBackground = memo(HeroAgentBackgroundInner);
