# Universal Business Website Template System

A data-driven static site generator that builds complete, mobile-optimized, color-matched business websites from a single `site.json` file in under 1 second.

## Included Archetype Presets (`presets/`)
1. **[`presets/brick-and-mortar.json`](file:///Users/coleparker/.gemini/antigravity/scratch/business-site-templates/presets/brick-and-mortar.json)** — Retail, auto/tire shops, restaurants, and storefronts with roadside sign showcases (`isSignShowcase: true`), physical addresses, and hours.
2. **[`presets/service-with-location.json`](file:///Users/coleparker/.gemini/antigravity/scratch/business-site-templates/presets/service-with-location.json)** — Professional offices, escrow/title, legal, medical, and agencies with physical office suites, founder/team bios, simplified service pages, and a dedicated 2-minute online order intake page (`open-order.html`).
3. **[`presets/service-without-location.json`](file:///Users/coleparker/.gemini/antigravity/scratch/business-site-templates/presets/service-without-location.json)** — Mobile & service-area businesses (detailing, landscaping, contractors) without a physical storefront, featuring service-area city/ZIP pills, interactive Before & After comparison sliders, and online package purchasing.

## Modular Components (`assets/base.css` & `assets/site-widgets.js`)
- **Services Grid & Simplified Service Pages** (`services` + `hasDetailPage: true`)
- **Dedicated Service-Specific Order Form Page** (`orderForm.enabled: true` -> generates `open-order.html` with a dropdown switcher that adapts form fields per service and routes to `recipientEmail`)
- **Interactive Before & After Sliders** (`beforeAfter`)
- **Product / Package Storefront & Slide-Over Checkout Cart** (`products`)
- **Filterable Photo Gallery & Fullscreen Lightbox** (`gallery`)
- **Google Maps Reviews & Rating Badge** (`reviews`)
- **General Contact Form & Location / Coverage Cards** (`contact`)

## Usage
```bash
python3 build_site.py presets/service-without-location.json ./demo-mobile-service
```
