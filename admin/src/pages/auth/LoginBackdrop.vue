<!--
作者: 杨永的Agent
日期: 2026-05-11
修改功能: K 线涨跌微动、机器人瞳孔与口型条动效、天线闪烁；尊重 prefers-reduced-motion
-->
<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'

const BOT_PIVOT_X = 114
const BOT_PIVOT_Y = 115
const BASE_TX = 380
const BASE_TY = 118

/** 机器人相对枢轴缩放（仅 bot 几何，不包含 K 线） */
const BOT_SCALE = 1.3

/** 整体场景旋转枢轴 — 约在 K 线与机器人之间 */
const SCENE_ROT_X = 318
const SCENE_ROT_Y = 248

const sceneDriftRef = ref<SVGGElement | null>(null)
const botMotionRef = ref<SVGGElement | null>(null)

const MOUSE_IDLE_MS = 1000
const MOUSE_LERP = 0.072
/** 跟随谐振理想轨迹的强度（越高越贴近、延迟越小） */
const AMBIENT_FOLLOW_LERP = 0.09
/** 鼠标活跃时将场景拉回静态的衰减系数 */
const AMBIENT_MOUSE_DECAY = 0.11
/** 空闲时谐振幅（位移 / SVG 用户单位） */
const AMBIENT_XY_RANGE = 26
const AMBIENT_ROT_RANGE = 4.2
const MAX_SHIFT = 13
const MAX_ROT_DEG = 7.8

let rafId = 0

let targetNx = 0
let targetNy = 0
let curNx = 0
let curNy = 0

/** mount 后随机相位，轨迹对时间 C∞，视觉上仍「飘忽」且无锚点跳转 */
let phaseXA = 0
let phaseXB = 0
let phaseXC = 0
let phaseYA = 0
let phaseYB = 0
let phaseYC = 0
let phaseRA = 0
let phaseRB = 0

let ambientCurTx = 0
let ambientCurTy = 0
let ambientCurTr = 0

let lastMouseAt = -Infinity

let prefersReducedMotion = true
let canHoverFine = false

function seededPhase() {
  return Math.random() * Math.PI * 2
}

/**
 * 多频正弦漂移：无分段目标，位置和角速度在时间上是平滑的，
 * display 再通过 lerp 跟随 ideal，避免离散换锚时的转角感。
 */
function harmonicIdeal(nowMs: number) {
  const t = nowMs * 0.001
  const tx =
    AMBIENT_XY_RANGE *
    (0.5 * Math.sin(t * 0.52 + phaseXA) +
      0.32 * Math.sin(t * 0.87 + phaseXB) +
      0.18 * Math.sin(t * 1.21 + phaseXC))

  const ty =
    AMBIENT_XY_RANGE *
    0.68 *
    (0.48 * Math.cos(t * 0.44 + phaseYA) +
      0.33 * Math.cos(t * 0.76 + phaseYB) +
      0.19 * Math.cos(t * 1.05 + phaseYC))

  const tr =
    AMBIENT_ROT_RANGE * (0.58 * Math.sin(t * 0.39 + phaseRA) + 0.42 * Math.sin(t * 0.83 + phaseRB))

  return { tx, ty, tr }
}

function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n))
}

function applySceneTransform() {
  const el = sceneDriftRef.value
  if (!el) return
  el.setAttribute(
    'transform',
    `translate(${ambientCurTx.toFixed(2)}, ${ambientCurTy.toFixed(2)}) rotate(${ambientCurTr.toFixed(3)}, ${SCENE_ROT_X}, ${SCENE_ROT_Y})`,
  )
}

function applyBotTransform(deg: number) {
  const el = botMotionRef.value
  if (!el) return
  const dx = curNx * MAX_SHIFT
  const dy = curNy * MAX_SHIFT * 0.58
  const d = clamp(deg + curNx * 5.8 - curNy * 3.9, -MAX_ROT_DEG, MAX_ROT_DEG)

  el.setAttribute(
    'transform',
    `translate(${BASE_TX + dx}, ${BASE_TY + dy}) rotate(${d.toFixed(2)}, ${BOT_PIVOT_X}, ${BOT_PIVOT_Y}) translate(${BOT_PIVOT_X}, ${BOT_PIVOT_Y}) scale(${BOT_SCALE}) translate(${-BOT_PIVOT_X}, ${-BOT_PIVOT_Y})`,
  )
}

function syncMouse(e: MouseEvent) {
  if (!canHoverFine) return
  lastMouseAt = performance.now()
  const w = window.innerWidth || 1
  const h = window.innerHeight || 1
  targetNx = clamp((e.clientX / w) * 2 - 1, -1, 1)
  targetNy = clamp((e.clientY / h) * 2 - 1, -1, 1)
}

function loop() {
  const now = performance.now()
  const mouseFresh = canHoverFine && now - lastMouseAt < MOUSE_IDLE_MS

  if (!mouseFresh) {
    targetNx = 0
    targetNy = 0
    const ideal = harmonicIdeal(now)
    ambientCurTx += (ideal.tx - ambientCurTx) * AMBIENT_FOLLOW_LERP
    ambientCurTy += (ideal.ty - ambientCurTy) * AMBIENT_FOLLOW_LERP
    ambientCurTr += (ideal.tr - ambientCurTr) * AMBIENT_FOLLOW_LERP
  } else {
    ambientCurTx += (0 - ambientCurTx) * AMBIENT_MOUSE_DECAY
    ambientCurTy += (0 - ambientCurTy) * AMBIENT_MOUSE_DECAY
    ambientCurTr += (0 - ambientCurTr) * AMBIENT_MOUSE_DECAY
  }

  const lerpM = MOUSE_LERP
  curNx += (targetNx - curNx) * lerpM
  curNy += (targetNy - curNy) * lerpM

  const passiveWobbleDeg = mouseFresh ? 0 : ambientCurTr * 0.45

  applySceneTransform()
  applyBotTransform(passiveWobbleDeg)

  rafId = requestAnimationFrame(loop)
}

function initStaticTransforms() {
  ambientCurTx = 0
  ambientCurTy = 0
  ambientCurTr = 0
  applySceneTransform()
  applyBotTransform(0)
}

onMounted(async () => {
  prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  canHoverFine =
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(hover: hover)').matches &&
    window.matchMedia('(pointer: fine)').matches

  await nextTick()

  if (prefersReducedMotion) {
    initStaticTransforms()
    return
  }

  phaseXA = seededPhase()
  phaseXB = seededPhase()
  phaseXC = seededPhase()
  phaseYA = seededPhase()
  phaseYB = seededPhase()
  phaseYC = seededPhase()
  phaseRA = seededPhase()
  phaseRB = seededPhase()

  lastMouseAt = Number.NEGATIVE_INFINITY
  window.addEventListener('mousemove', syncMouse, { passive: true })
  initStaticTransforms()
  rafId = requestAnimationFrame(loop)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', syncMouse)
  cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="pointer-events-none absolute inset-0 overflow-hidden bg-zinc-950" aria-hidden="true">
    <div
      class="absolute inset-0 opacity-[0.35]"
      style="
        background-image:
          radial-gradient(circle at 18% 22%, rgb(16 185 129 / 0.12) 0%, transparent 42%),
          radial-gradient(circle at 82% 78%, rgb(16 185 129 / 0.08) 0%, transparent 40%),
          radial-gradient(circle at 52% 10%, rgb(39 39 42 / 0.9) 0%, transparent 38%);
      "
    />
    <div
      class="absolute inset-0 opacity-[0.04]"
      style="
        background-image:
          linear-gradient(rgb(248 250 252) 1px, transparent 1px),
          linear-gradient(90deg, rgb(248 250 252) 1px, transparent 1px);
        background-size: 56px 56px;
      "
    />

    <!-- 略增宽以容纳放大后的机器人；位移由 SVG 内 scene 组脚本驱动（无 CSS 周期浮动） -->
    <div
      class="absolute bottom-[4%] left-[-14%] w-[min(120vw,680px)] max-md:-translate-x-0 md:bottom-auto md:left-[max(1.75rem,calc((100vw-1120px)/2+1rem))] md:top-1/2 md:w-[min(50vw,580px)] md:-translate-x-0 md:-translate-y-1/2"
    >
      <svg
        class="w-full overflow-visible drop-shadow-[0_0_80px_rgb(16_185_129_/_0.12)]"
        viewBox="0 0 720 460"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient
            id="lb-bar-up"
            x1="0"
            y1="1"
            x2="0"
            y2="0"
            gradientUnits="objectBoundingBox"
          >
            <stop offset="0%" stop-color="rgb(16 185 129)" stop-opacity="0.95" />
            <stop offset="100%" stop-color="rgb(5 150 105)" stop-opacity="0.45" />
          </linearGradient>
          <linearGradient
            id="lb-bar-down"
            x1="0"
            y1="1"
            x2="0"
            y2="0"
            gradientUnits="objectBoundingBox"
          >
            <stop offset="0%" stop-color="rgb(244 63 94)" stop-opacity="0.85" />
            <stop offset="100%" stop-color="rgb(190 24 93)" stop-opacity="0.38" />
          </linearGradient>
          <linearGradient id="lb-beam" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="rgb(16 185 129)" stop-opacity="0" />
            <stop offset="45%" stop-color="rgb(16 185 129)" stop-opacity="0.5" />
            <stop offset="100%" stop-color="rgb(16 185 129)" stop-opacity="0.05" />
          </linearGradient>
        </defs>

        <!-- 执行链路 + K 线 + bot：空闲时整块随机漂移 -->
        <g ref="sceneDriftRef">
          <path
            d="M420 342 C 520 300, 600 268, 660 226"
            stroke="url(#lb-beam)"
            stroke-width="2"
            stroke-dasharray="6 14"
            class="opacity-90"
          />
          <circle
            cx="660"
            cy="226"
            r="8"
            stroke="rgb(212 212 216)"
            stroke-width="1.5"
            fill="rgb(24 24 27)"
          />

          <g opacity="0.92">
            <g transform="translate(96,248)">
              <g class="lb-candle lb-candle-dn lb-candle-s0">
                <rect x="0" y="24" width="12" height="56" rx="2" fill="url(#lb-bar-down)" />
                <line
                  x1="6"
                  y1="8"
                  x2="6"
                  y2="100"
                  stroke="rgb(228 228 231)"
                  stroke-width="1.2"
                  opacity="0.65"
                />
              </g>
            </g>
            <g transform="translate(138,218)">
              <g class="lb-candle lb-candle-up lb-candle-s1">
                <rect x="0" y="10" width="12" height="62" rx="2" fill="url(#lb-bar-up)" />
                <line
                  x1="6"
                  y1="4"
                  x2="6"
                  y2="86"
                  stroke="rgb(228 228 231)"
                  stroke-width="1.2"
                  opacity="0.65"
                />
              </g>
            </g>
            <g transform="translate(178,238)">
              <g class="lb-candle lb-candle-up lb-candle-s2">
                <rect x="0" y="18" width="12" height="48" rx="2" fill="url(#lb-bar-up)" />
                <line
                  x1="6"
                  y1="2"
                  x2="6"
                  y2="78"
                  stroke="rgb(228 228 231)"
                  stroke-width="1.2"
                  opacity="0.65"
                />
              </g>
            </g>
            <g transform="translate(218,255)">
              <g class="lb-candle lb-candle-dn lb-candle-s3">
                <rect x="0" y="28" width="12" height="44" rx="2" fill="url(#lb-bar-down)" />
                <line
                  x1="6"
                  y1="14"
                  x2="6"
                  y2="92"
                  stroke="rgb(228 228 231)"
                  stroke-width="1.2"
                  opacity="0.65"
                />
              </g>
            </g>
            <g transform="translate(258,200)">
              <g class="lb-candle lb-candle-up lb-candle-s4">
                <rect x="0" y="6" width="12" height="72" rx="2" fill="url(#lb-bar-up)" />
                <line
                  x1="6"
                  y1="0"
                  x2="6"
                  y2="90"
                  stroke="rgb(228 228 231)"
                  stroke-width="1.2"
                  opacity="0.65"
                />
              </g>
            </g>
          </g>

          <g ref="botMotionRef" class="opacity-[0.95]">
            <rect
              x="0"
              y="0"
              width="228"
              height="168"
              rx="36"
              stroke="rgb(63 63 70)"
              stroke-width="2"
              fill="rgb(24 24 27 / 0.65)"
            />
            <circle
              cx="86"
              cy="72"
              r="14"
              stroke="rgb(113 113 122)"
              stroke-width="1.5"
              fill="rgb(9 9 11)"
            />
            <!-- 瞳孔微动 -->
            <circle
              cx="86"
              cy="72"
              r="6"
              fill="rgb(16 185 129 / 0.85)"
              class="lb-bot-pupil lb-bot-pupil-l"
            />
            <circle
              cx="158"
              cy="72"
              r="14"
              stroke="rgb(113 113 122)"
              stroke-width="1.5"
              fill="rgb(9 9 11)"
            />
            <circle
              cx="158"
              cy="72"
              r="6"
              fill="rgb(16 185 129 / 0.45)"
              class="lb-bot-pupil lb-bot-pupil-r"
            />

            <!-- 口型条（极简） -->
            <rect
              class="lb-bot-mouth"
              x="94"
              y="98"
              width="40"
              height="6"
              rx="3"
              fill="rgb(63 63 70)"
              stroke="rgb(82 82 91)"
              stroke-width="0.75"
            />

            <rect
              x="36"
              y="122"
              width="156"
              height="12"
              rx="6"
              fill="rgb(39 39 42)"
              stroke="rgb(63 63 70)"
              stroke-width="1"
            />
            <circle cx="56" cy="128" r="4" fill="rgb(16 185 129)" class="login-motion-glow" />
            <circle cx="80" cy="128" r="4" fill="rgb(113 113 122)" opacity="0.85" />

            <line
              class="lb-bot-antenna-shaft"
              x1="114"
              y1="0"
              x2="114"
              y2="-32"
              stroke="rgb(161 161 170)"
              stroke-width="2.5"
              stroke-linecap="round"
            />
            <circle
              class="lb-bot-antenna-bulb"
              cx="114"
              cy="-36"
              r="7"
              stroke="rgb(82 82 91)"
              stroke-width="1.5"
              fill="rgb(16 185 129 / 0.35)"
            />

            <rect
              x="58"
              y="188"
              width="132"
              height="118"
              rx="26"
              stroke="rgb(63 63 70)"
              stroke-width="2"
              fill="rgb(24 24 27 / 0.45)"
            />
            <path
              d="M106 226h36M106 246h54M106 266h42"
              stroke="rgb(82 82 91)"
              stroke-width="2"
              stroke-linecap="round"
            />
            <rect
              x="90"
              y="208"
              width="148"
              height="68"
              rx="12"
              stroke="rgb(63 63 70)"
              stroke-width="1.5"
              fill="rgb(9 9 11 / 0.55)"
            />
            <text
              x="94"
              y="252"
              fill="rgb(113 113 122)"
              style="font-family: var(--font-mono)"
              font-size="11"
              letter-spacing="0.14em"
            >
              BOT · RUNTIME READY
            </text>
          </g>
        </g>
      </svg>
    </div>

    <div
      class="login-motion-float-b absolute top-[10%] right-[6%] text-right font-mono text-[10px] uppercase tracking-[0.22em] text-zinc-500 max-md:hidden"
    >
      <span class="block text-emerald-500/85">intent.route</span>
      <span class="mt-3 block opacity-85">risk.eval</span>
      <span class="mt-3 block opacity-70">billing.trace</span>
    </div>

    <div
      class="absolute inset-0 opacity-[0.07]"
      style="
        background-image: repeating-linear-gradient(
          -32deg,
          transparent,
          transparent 80px,
          rgb(248 250 252) 80px,
          rgb(248 250 252) 81px
        );
      "
    />
  </div>
</template>

<style scoped>
@keyframes login-motion-float-b {
  0% {
    transform: translate3d(0, 6px, 0);
    opacity: 0.92;
  }
  100% {
    transform: translate3d(0, -4px, 0);
    opacity: 1;
  }
}

@keyframes login-motion-led {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
}

.login-motion-float-b {
  animation: login-motion-float-b 12s cubic-bezier(0.45, 0, 0.55, 1) alternate infinite;
  will-change: transform;
}

.login-motion-glow {
  animation: login-motion-led 2.8s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}

/* ---------- K 线涨跌微移 ---------- */
.lb-candle {
  transform-box: fill-box;
  transform-origin: center bottom;
  will-change: transform;
}

.lb-candle-up {
  animation: lb-candle-rise 2.15s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}

.lb-candle-dn {
  animation: lb-candle-fall 2.15s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}

.lb-candle-s1 {
  animation-delay: 0.18s;
}
.lb-candle-s2 {
  animation-delay: 0.42s;
}
.lb-candle-s3 {
  animation-delay: 0.28s;
}
.lb-candle-s4 {
  animation-delay: 0.55s;
}

@keyframes lb-candle-rise {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

@keyframes lb-candle-fall {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(5px);
  }
}

/* ---------- 机器人瞳孔、口型、天线 ---------- */
.lb-bot-pupil {
  transform-box: fill-box;
  transform-origin: center center;
}

.lb-bot-pupil-l {
  animation: lb-bot-pupil-drift 4.1s ease-in-out infinite;
}

.lb-bot-pupil-r {
  animation: lb-bot-pupil-drift 4.5s ease-in-out infinite reverse;
  animation-delay: 0.35s;
}

@keyframes lb-bot-pupil-drift {
  0%,
  100% {
    transform: translate(0, 0);
  }
  32% {
    transform: translate(1.35px, -0.65px);
  }
  64% {
    transform: translate(-1.1px, 0.85px);
  }
}

.lb-bot-mouth {
  transform-box: fill-box;
  transform-origin: center center;
  animation: lb-bot-mouth-flex 2.35s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}

@keyframes lb-bot-mouth-flex {
  0%,
  100% {
    transform: scaleX(1) scaleY(1);
    opacity: 0.9;
  }
  42% {
    transform: scaleX(1.16) scaleY(1.06);
    opacity: 1;
  }
}

.lb-bot-antenna-shaft {
  animation: lb-bot-ant-shaft-pulse 1.7s ease-in-out infinite;
}

.lb-bot-antenna-bulb {
  animation: lb-bot-ant-bulb-flash 1.7s ease-in-out infinite;
}

@keyframes lb-bot-ant-shaft-pulse {
  0%,
  100% {
    opacity: 0.65;
    stroke: rgb(130 130 139);
  }
  52% {
    opacity: 1;
    stroke: rgb(207 207 217);
  }
}

@keyframes lb-bot-ant-bulb-flash {
  0%,
  50%,
  100% {
    opacity: 0.62;
    fill: rgb(16 185 129 / 0.22);
    stroke-opacity: 0.82;
  }
  26% {
    opacity: 1;
    fill: rgb(52 211 153 / 0.95);
    stroke-opacity: 1;
    filter: brightness(1.25);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-motion-float-b,
  .login-motion-glow,
  .lb-candle,
  .lb-bot-pupil,
  .lb-bot-mouth,
  .lb-bot-antenna-shaft,
  .lb-bot-antenna-bulb {
    animation: none;
  }

  .login-motion-float-b {
    transform: none;
  }

  .lb-candle,
  .lb-bot-pupil,
  .lb-bot-mouth {
    transform: none;
  }

  .lb-bot-antenna-shaft {
    opacity: 0.92;
    stroke: rgb(161 161 170);
  }

  .lb-bot-antenna-bulb {
    opacity: 1;
    fill: rgb(16 185 129 / 0.35);
    stroke-opacity: 1;
    filter: none;
  }
}
</style>
