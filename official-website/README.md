# ChainUp AI Agent — Official Website

Product marketing site built with **Next.js 16 App Router**, optimized for SEO, performance, and international audiences.

## Features

- **SEO**: Metadata API, `sitemap.xml`, `robots.txt`, JSON-LD structured data, hreflang alternates
- **i18n**: 5 locales (en, zh-CN, zh-TW, ja, ko) via [next-intl](https://next-intl.dev)
- **Performance**: Static generation, font optimization (`next/font`), AVIF/WebP images, package import optimization
- **Product tour**: Interactive guided walkthrough powered by [driver.js](https://driverjs.com)
- **Interactive demo**: Telegram-style chat preview on the homepage

## Getting Started

```bash
cd official-website
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_SITE_URL` | Canonical site URL for SEO | `https://chainup-ai-agent.com` |

Copy `.env.example` to `.env.local` for local overrides.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server (Turbopack) |
| `npm run build` | Production build |
| `npm run start` | Production server |
| `npm run lint` | ESLint |

## Project Structure

```
src/
├── app/[locale]/     # Localized routes (/, /features, /guide)
├── components/       # UI, layout, home sections, guide
├── i18n/             # Routing, navigation, request config
├── messages/         # Translation JSON per locale
└── lib/              # SEO helpers, utilities
```

## Adding a Locale

1. Add locale code to `src/i18n/routing.ts`
2. Create `src/messages/{locale}.json`
3. Rebuild — static params regenerate automatically

## Deployment

Deploy to Vercel, Cloudflare Pages, or any Node.js host supporting Next.js 16.

Set `NEXT_PUBLIC_SITE_URL` to your production domain before building.
