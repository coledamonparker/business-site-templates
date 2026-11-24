#!/usr/bin/env python3
"""
Universal Business Website Template Generator (build_site.py)
-------------------------------------------------------------
Builds a complete, mobile-optimized, color-matched business website from a single
`site.json` configuration file.

Supported Archetypes (`archetype`):
  1. "brick-and-mortar"   — Retail, auto shops, restaurants, showrooms with physical signs
  2. "service-location"   — Professional offices, clinics, agencies, escrow/law firms
  3. "service-mobile"     — Mobile/on-site contractors, detailing, landscaping (no storefront)

Supported Modular Sections (auto-enabled when present in `site.json`):
  - `services`: Grid of services + optional individual simplified detail pages (`hasDetailPage: true`)
  - `beforeAfter`: Interactive drag/touch Before & After image comparison sliders
  - `products`: Storefront cards for packages/products with slide-over cart & checkout
  - `about`: Founder / team / story section
  - `reviews`: Google Maps rating badge + verified customer review cards
  - `gallery`: Filterable photo gallery with fullscreen lightbox modal
  - `orderForm`: Dedicated `open-order.html` page with dropdown service switcher
  - `contact`: General contact form + location card (or service-area coverage card)

Usage:
  python3 build_site.py <path/to/site.json> <output_directory>
"""

import json
import os
import shutil
import sys
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")


def font_links_and_vars(font_preset: str):
    if font_preset == "industrial":
        link = "https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,700;0,800;1,700&family=Inter:wght@400;500;600;700&display=swap"
        css_vars = "--font-display: 'Barlow Condensed', Impact, sans-serif; --font-sans: 'Inter', sans-serif;"
    elif font_preset == "editorial":
        link = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
        css_vars = "--font-display: 'Plus Jakarta Sans', sans-serif; --font-sans: 'Plus Jakarta Sans', sans-serif; --font-serif: 'Cormorant Garamond', Georgia, serif;"
    else:
        link = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
        css_vars = "--font-display: 'Plus Jakarta Sans', sans-serif; --font-sans: 'Plus Jakarta Sans', sans-serif;"
    return link, css_vars


def build_theme_override(cfg: dict) -> str:
    theme = cfg.get("theme", {})
    _, font_vars = font_links_and_vars(theme.get("fontPreset", "modern"))
    rules = [
        f"--brand-primary: {theme.get('primaryColor', '#1B7A8C')};",
        f"--brand-primary-hover: {theme.get('primaryHover', '#146170')};",
        f"--brand-primary-soft: {theme.get('primarySoft', '#EDF8FA')};",
        f"--brand-accent: {theme.get('accentColor', '#B89B5E')};",
        f"--brand-dark: {theme.get('darkColor', '#1E2022')};",
        f"--brand-surface-dark: {theme.get('surfaceDark', '#151719')};",
        font_vars,
    ]
    return ":root { " + " ".join(rules) + " }"


def render_header(cfg: dict, has_order_page: bool, has_products: bool, is_subpage: bool = False) -> str:
    biz = cfg.get("business", {})
    archetype = cfg.get("archetype", "brick-and-mortar")
    name = escape(biz.get("name", "Business Name"))
    wordmark_html = biz.get("wordmarkHtml") or f"<strong>{name}</strong>"
    logo_path = biz.get("logo", "")
    phone = biz.get("phone", "")
    phone_digits = "".join(c for c in phone if c.isdigit())
    badge_text = escape(biz.get("topBadge", "LOCAL & TRUSTED"))

    if archetype == "service-mobile":
        loc_display = escape(biz.get("serviceAreaSummary", "Mobile Service • We Come to You"))
    else:
        loc_display = escape(biz.get("address", ""))

    hours = escape(biz.get("hoursSummary", "Mon–Fri: 9:00 AM – 5:00 PM"))
    prefix = "index.html" if is_subpage else ""

    nav_items = []
    if cfg.get("services"):
        nav_items.append((f"{prefix}#services", "Services"))
    if cfg.get("beforeAfter"):
        nav_items.append((f"{prefix}#before-after", "Before & After"))
    if has_products:
        nav_items.append((f"{prefix}#shop", escape(cfg.get("productsTitle", "Packages & Shop"))))
    if cfg.get("about"):
        nav_items.append((f"{prefix}#about", "About"))
    if cfg.get("reviews"):
        nav_items.append((f"{prefix}#reviews", "Reviews"))
    if cfg.get("gallery"):
        nav_items.append((f"{prefix}#gallery", "Photos"))
    nav_items.append((f"{prefix}#contact", "Contact"))

    primary_cta_href = "open-order.html" if has_order_page else f"{prefix}#contact"
    primary_cta_label = escape(cfg.get("orderForm", {}).get("ctaLabel", "Open Order / Book")) if has_order_page else escape(biz.get("primaryCtaLabel", "Request Quote"))

    logo_img_tag = f'<img src="{escape(logo_path)}" alt="{name} Logo" class="brand-logo-img" />' if logo_path else ""

    cart_btn_html = ""
    if has_products and not is_subpage:
        cart_btn_html = """
        <button type="button" class="cart-trigger-btn" id="cartTriggerBtn" aria-label="View Cart">
          <span>Cart</span>
          <span class="cart-count-badge" id="cartCountBadge">0</span>
        </button>"""

    nav_links_html = "\n        ".join([f'<a href="{href}">{label}</a>' for href, label in nav_items])
    mobile_links_html = "\n          ".join([f'<a href="{href}" class="mobile-link">{label}</a>' for href, label in nav_items])

    return f"""  <!-- Top Utility Bar -->
  <div class="utility-bar">
    <div class="container utility-inner">
      <div class="utility-left">
        <span class="pill-badge">{badge_text}</span>
        <span class="utility-address">{loc_display}</span>
      </div>
      <div class="utility-right">
        <span class="utility-hours">{hours}</span>
        {f'<a href="tel:{phone_digits}" class="utility-phone">{escape(phone)}</a>' if phone else ''}
      </div>
    </div>
  </div>

  <!-- Sticky Header -->
  <header class="site-header" id="top">
    <div class="container header-inner">
      <a href="index.html" class="brand-logo" aria-label="{name} Home">
        {logo_img_tag}
        <span class="brand-wordmark">{wordmark_html}</span>
      </a>

      <nav class="main-nav" aria-label="Primary Navigation">
        {nav_links_html}
      </nav>

      <div class="header-actions">
        {cart_btn_html}
        {f'<a href="tel:{phone_digits}" class="btn btn-ghost"><span>{escape(phone)}</span></a>' if phone else ''}
        <a href="{primary_cta_href}" class="btn btn-primary">{primary_cta_label}</a>
        <button type="button" class="menu-toggle" id="menuToggle" aria-label="Toggle Menu" aria-expanded="false" aria-controls="mobileDrawer">
          <span class="hamburger-bar"></span>
          <span class="hamburger-bar"></span>
          <span class="hamburger-bar"></span>
        </button>
      </div>
    </div>

    <div class="mobile-drawer" id="mobileDrawer" hidden>
      <div class="container mobile-drawer-inner">
        <nav class="mobile-nav" aria-label="Mobile Navigation">
          {mobile_links_html}
        </nav>
        <div class="mobile-drawer-cta">
          <a href="{primary_cta_href}" class="btn btn-primary btn-block mobile-link">{primary_cta_label}</a>
          {f'<a href="tel:{phone_digits}" class="btn btn-outline btn-block">Call {escape(phone)}</a>' if phone else ''}
        </div>
      </div>
    </div>
  </header>"""


def render_footer_and_scripts(cfg: dict, has_order_page: bool) -> str:
    biz = cfg.get("business", {})
    name = escape(biz.get("name", "Business Name"))
    wordmark_html = biz.get("wordmarkHtml") or f"<strong>{name}</strong>"
    logo_path = biz.get("logo", "")
    phone = biz.get("phone", "")
    phone_digits = "".join(c for c in phone if c.isdigit())
    tagline = escape(biz.get("tagline", ""))
    address_or_area = escape(biz.get("address") or biz.get("serviceAreaSummary") or "")
    legal = escape(biz.get("legalNote", f"© 2026 {biz.get('name', '')}. All rights reserved."))

    primary_cta_href = "open-order.html" if has_order_page else "#contact"
    primary_cta_label = escape(cfg.get("orderForm", {}).get("ctaLabel", "Open Order")) if has_order_page else escape(biz.get("primaryCtaLabel", "Get Quote"))

    order_schemas = {}
    for idx, svc in enumerate(cfg.get("services", []), start=1):
        slug = svc.get("slug", f"service-{idx}")
        order_schemas[slug] = {
            "code": svc.get("code", f"{idx:02d}"),
            "title": svc.get("title", "Service"),
            "helper": svc.get("summary", ""),
            "fields": svc.get("orderFields", [
                {"name": "Property_or_Service_Location", "label": "Address / Location", "required": True, "placeholder": "Street, City, ZIP"},
                {"name": "Preferred_Date", "label": "Target Date", "type": "date", "required": False},
                {"name": "Project_or_Order_Details", "label": "Details / Scope", "required": True, "placeholder": "Describe what you need..."}
            ])
        }

    js_config = {
        "businessName": biz.get("name", ""),
        "recipientEmail": biz.get("recipientEmail", "orders@example.com"),
        "phone": phone,
        "orderSchemas": order_schemas
    }

    logo_img_tag = f'<img src="{escape(logo_path)}" alt="{name} Logo" class="brand-logo-img" />' if logo_path else ""

    return f"""  <!-- Footer -->
  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <a href="index.html" class="brand-logo brand-logo-footer">
          {logo_img_tag}
          <span class="brand-wordmark">{wordmark_html}</span>
        </a>
        {f'<p style="margin-top:0.4rem;color:var(--brand-accent);font-weight:700;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;">{tagline}</p>' if tagline else ''}
        <p style="margin-top:0.25rem;">{address_or_area} {f'&bull; <a href="tel:{phone_digits}" style="color:#fff;font-weight:700;">{escape(phone)}</a>' if phone else ''}</p>
      </div>
      <div>
        <p>{legal}</p>
      </div>
    </div>
  </footer>

  <!-- Sticky Mobile Bottom Action Bar -->
  <div class="mobile-action-bar" aria-label="Quick Mobile Actions">
    {f'<a href="tel:{phone_digits}" class="mobile-action-btn mobile-action-call"><span>Call Now</span></a>' if phone else '<a href="#contact" class="mobile-action-btn mobile-action-call"><span>Message</span></a>'}
    <a href="{primary_cta_href}" class="mobile-action-btn mobile-action-primary"><span>{primary_cta_label}</span></a>
  </div>

  <script>
    window.SITE_CONFIG = {json.dumps(js_config)};
  </script>
  <script src="site-widgets.js"></script>"""


def build_site(config_path: str, out_dir: str):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "images"), exist_ok=True)

    # Copy base CSS and runtime JS
    with open(os.path.join(ASSETS_DIR, "base.css"), "r", encoding="utf-8") as f:
        base_css = f.read()
    theme_css = build_theme_override(cfg)
    with open(os.path.join(out_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(base_css + "\n\n/* Theme Token Overrides */\n" + theme_css + "\n")

    shutil.copyfile(os.path.join(ASSETS_DIR, "site-widgets.js"), os.path.join(out_dir, "site-widgets.js"))

    biz = cfg.get("business", {})
    archetype = cfg.get("archetype", "brick-and-mortar")
    services = cfg.get("services", [])
    has_order_page = bool(cfg.get("orderForm", {}).get("enabled", False))
    products = cfg.get("products", [])
    has_products = len(products) > 0
    font_link, _ = font_links_and_vars(cfg.get("theme", {}).get("fontPreset", "modern"))

    header_html = render_header(cfg, has_order_page, has_products, is_subpage=False)
    footer_html = render_footer_and_scripts(cfg, has_order_page)

    # Hero Section
    hero = cfg.get("hero", {})
    reviews_data = cfg.get("reviews", {})
    rating_score = escape(str(reviews_data.get("rating", "5.0")))
    rating_count = escape(str(reviews_data.get("countText", "Verified Google Reviews")))
    phone = biz.get("phone", "")
    phone_digits = "".join(c for c in phone if c.isdigit())
    primary_cta_href = "open-order.html" if has_order_page else "#contact"
    primary_cta_label = escape(cfg.get("orderForm", {}).get("ctaLabel", "Open Order")) if has_order_page else escape(biz.get("primaryCtaLabel", "Request Quote"))

    areas_html = ""
    if archetype == "service-mobile" and biz.get("serviceAreas"):
        pills = "".join([f'<span class="area-pill">{escape(a)}</span>' for a in biz["serviceAreas"]])
        areas_html = f'<div class="service-area-pills"><span class="service-area-label">Service Areas:</span>{pills}</div>'

    showcase_class = "hero-visual-card sign-showcase" if hero.get("isSignShowcase") else "hero-visual-card"
    hero_img = escape(hero.get("image", ""))
    hero_caption_left = escape(hero.get("captionLeft", biz.get("name", "")))
    hero_caption_right = escape(hero.get("captionRight", biz.get("topBadge", "")))

    hero_section = f"""  <!-- Hero Section -->
  <section class="hero">
    <div class="container hero-grid">
      <div>
        <div class="trust-badge">
          <span class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
          <strong>{rating_score} Google Rating</strong>
          <span>&bull; {rating_count}</span>
        </div>
        <h1>{escape(hero.get("headline", biz.get("name", "")))} <span class="hero-highlight">{escape(hero.get("highlight", ""))}</span></h1>
        <p class="hero-lead">{escape(hero.get("subtitle", ""))}</p>
        <div class="hero-cta-group">
          <a href="{primary_cta_href}" class="btn btn-primary btn-lg">{primary_cta_label} &rarr;</a>
          {f'<a href="tel:{phone_digits}" class="btn btn-outline btn-lg">Call {escape(phone)}</a>' if phone else ''}
        </div>
        {areas_html}
      </div>
      {f'''<div class="{showcase_class}">
        <img src="{hero_img}" alt="{escape(biz.get('name', ''))}" />
        <div class="hero-card-caption">
          <strong>{hero_caption_left}</strong>
          <span>{hero_caption_right}</span>
        </div>
      </div>''' if hero_img else ''}
    </div>
  </section>"""

    # Metrics Strip
    metrics = cfg.get("metrics", [])
    metrics_section = ""
    if metrics:
        items_html = "\n".join([
            f'      <div class="metric-item"><strong>{escape(m.get("value", ""))}</strong><span>{escape(m.get("label", ""))}</span></div>'
            for m in metrics
        ])
        metrics_section = f"""  <!-- Key Metrics Strip -->
  <section class="metrics-strip">
    <div class="container metrics-grid">
{items_html}
    </div>
  </section>"""

    # Services Section
    services_section = ""
    if services:
        cards = []
        for idx, s in enumerate(services, start=1):
            code = escape(s.get("code", f"{idx:02d}"))
            slug = escape(s.get("slug", f"service-{idx}"))
            title = escape(s.get("title", "Service"))
            summary = escape(s.get("summary", ""))
            price = escape(s.get("priceText", ""))
            has_detail = bool(s.get("hasDetailPage", False))
            target_url = f"{slug}.html" if has_detail else (f"open-order.html?type={slug}" if has_order_page else "#contact")
            link_text = "View Details & Open Order &rarr;" if has_detail else ("Open Order &rarr;" if has_order_page else "Request Quote &rarr;")

            cards.append(f"""        <article class="service-card">
          <div class="service-card-top">
            <span class="service-num-badge">{code}</span>
            {f'<span class="service-price-tag">{price}</span>' if price else ''}
          </div>
          <h3><a href="{target_url}">{title}</a></h3>
          <p>{summary}</p>
          <div class="service-card-actions">
            <a href="{target_url}" class="service-link">{link_text}</a>
          </div>
        </article>""")

        services_section = f"""  <!-- Services Section -->
  <section id="services" class="section">
    <div class="container">
      <div class="section-heading">
        <span class="eyebrow">{escape(cfg.get("servicesEyebrow", "What We Do"))}</span>
        <h2>{escape(cfg.get("servicesTitle", "Our Services"))}</h2>
        <p>{escape(cfg.get("servicesSubtitle", ""))}</p>
      </div>
      <div class="services-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>"""

    # Before & After Sliders Section
    ba_items = cfg.get("beforeAfter", [])
    ba_section = ""
    if ba_items:
        ba_cards = []
        for item in ba_items:
            ba_cards.append(f"""        <div class="ba-card">
          <div class="ba-viewport">
            <img src="{escape(item.get('afterImage', ''))}" alt="After: {escape(item.get('title', ''))}" class="ba-img" />
            <div class="ba-before-layer">
              <img src="{escape(item.get('beforeImage', ''))}" alt="Before: {escape(item.get('title', ''))}" class="ba-img" />
            </div>
            <span class="ba-tag ba-tag-before">{escape(item.get('beforeLabel', 'Before'))}</span>
            <span class="ba-tag ba-tag-after">{escape(item.get('afterLabel', 'After'))}</span>
            <div class="ba-divider"><div class="ba-handle">&harr;</div></div>
            <input type="range" min="0" max="100" value="50" class="ba-range-input" aria-label="Compare before and after for {escape(item.get('title', ''))}" />
          </div>
          <div class="ba-caption">
            <h3>{escape(item.get('title', ''))}</h3>
            <p>{escape(item.get('description', ''))}</p>
          </div>
        </div>""")
        ba_section = f"""  <!-- Interactive Before & After Sliders -->
  <section id="before-after" class="section section-alt">
    <div class="container">
      <div class="section-heading">
        <span class="eyebrow">Real Transformations</span>
        <h2>Before &amp; After Results</h2>
        <p>Drag the slider on any photo below to compare before and after our work.</p>
      </div>
      <div class="ba-grid">
{chr(10).join(ba_cards)}
      </div>
    </div>
  </section>"""

    # Products / Packages Storefront Section
    products_section = ""
    cart_drawer_html = ""
    if has_products:
        p_cards = []
        for idx, prod in enumerate(products, start=1):
            pid = escape(prod.get("id", f"prod-{idx}"))
            pname = escape(prod.get("name", "Package"))
            pprice = float(prod.get("price", 0))
            pdesc = escape(prod.get("description", ""))
            pimg = escape(prod.get("image", ""))
            pbadge = escape(prod.get("badge", ""))
            pcheckout = escape(prod.get("checkoutUrl", ""))
            feats = "\n".join([f"<li>{escape(ft)}</li>" for ft in prod.get("features", [])])

            badge_html = f'<span class="product-badge">{pbadge}</span>' if pbadge else ""
            img_block = f'<div class="product-img-wrap"><img src="{pimg}" alt="{pname}" loading="lazy" />{badge_html}</div>' if pimg else ""
            feats_block = f'<ul class="product-features">{feats}</ul>' if feats else ""

            p_cards.append(f"""        <article class="product-card">
          {img_block}
          <div class="product-body">
            <div class="product-top">
              <h3>{pname}</h3>
              <span class="product-price">${pprice:,.2f}</span>
            </div>
            <p class="product-desc">{pdesc}</p>
            {feats_block}
            <div class="product-actions">
              <button type="button" class="btn btn-primary btn-block add-to-cart-btn" data-id="{pid}" data-name="{pname}" data-price="{pprice}" data-checkout-url="{pcheckout}">
                {escape(prod.get("ctaLabel", "Add to Order"))}
              </button>
            </div>
          </div>
        </article>""")

        products_section = f"""  <!-- Products / Packages Storefront -->
  <section id="shop" class="section">
    <div class="container">
      <div class="section-heading">
        <span class="eyebrow">{escape(cfg.get("productsEyebrow", "Direct Online Ordering"))}</span>
        <h2>{escape(cfg.get("productsTitle", "Packages & Products"))}</h2>
        <p>{escape(cfg.get("productsSubtitle", "Select any package or item below to purchase or submit an order directly."))}</p>
      </div>
      <div class="products-grid">
{chr(10).join(p_cards)}
      </div>
    </div>
  </section>"""

        cart_drawer_html = """  <!-- Slide-Over Checkout Cart Drawer -->
  <div class="cart-backdrop" id="cartBackdrop" hidden></div>
  <aside class="cart-drawer" id="cartDrawer" aria-label="Shopping Cart" hidden>
    <div class="cart-header">
      <h3>Your Order Summary</h3>
      <button type="button" class="cart-close-btn" id="cartCloseBtn" aria-label="Close Cart">&times;</button>
    </div>
    <div class="cart-body">
      <div id="cartItemsList"></div>
      <div class="cart-total-bar">
        <span>Total</span>
        <span id="cartTotalValue">$0.00</span>
      </div>
      <form id="cartCheckoutForm" style="margin-top:1.25rem;">
        <div class="form-group">
          <label for="cart_name">Your Full Name *</label>
          <input type="text" id="cart_name" name="Customer_Name" required placeholder="Jane Doe" />
        </div>
        <div class="form-group">
          <label for="cart_email">Your Email *</label>
          <input type="email" id="cart_email" name="Customer_Email" required placeholder="jane@example.com" />
        </div>
        <div class="form-group">
          <label for="cart_phone">Your Phone *</label>
          <input type="tel" id="cart_phone" name="Customer_Phone" required placeholder="(555) 555-0199" />
        </div>
        <div class="form-group">
          <label for="cart_notes">Delivery / Service Address or Notes</label>
          <textarea id="cart_notes" name="Order_Notes" rows="2" placeholder="Address, preferred date, or questions..."></textarea>
        </div>
        <button type="submit" class="btn btn-primary btn-block btn-lg">Place Order Now</button>
        <div id="cartCheckoutStatus" class="form-status" hidden></div>
      </form>
    </div>
  </aside>"""

    # About Section
    about = cfg.get("about", {})
    about_section = ""
    if about and about.get("headline"):
        paras = "\n".join([f"        <p style='margin-bottom:1rem;color:var(--brand-muted);'>{escape(p)}</p>" for p in about.get("paragraphs", [])])
        img_col = f"""      <div>
        <div class="hero-visual-card" style="max-width:380px;margin:0 auto;">
          <img src="{escape(about.get('image', ''))}" alt="{escape(about.get('personName', ''))}" />
          {f'<div class="hero-card-caption"><strong>{escape(about.get("personName", ""))}</strong><span>{escape(about.get("personTitle", ""))}</span></div>' if about.get("personName") else ''}
        </div>
      </div>""" if about.get("image") else ""

        about_section = f"""  <!-- About Section -->
  <section id="about" class="section section-alt">
    <div class="container hero-grid">
{img_col}
      <div>
        <span class="eyebrow">{escape(about.get("eyebrow", "About Us"))}</span>
        <h2 style="font-size:clamp(1.75rem,3vw,2.35rem);font-weight:800;margin-bottom:1rem;">{escape(about.get("headline", ""))}</h2>
{paras}
      </div>
    </div>
  </section>"""

    # Reviews Section
    reviews_items = reviews_data.get("items", [])
    reviews_section = ""
    if reviews_items:
        r_cards = []
        for r in reviews_items:
            name_str = r.get("name", "Customer")
            initials = "".join([w[0].upper() for w in name_str.split()[:2]]) or "★"
            r_cards.append(f"""        <article class="review-card">
          <div class="review-meta">
            <div class="reviewer-avatar">{escape(initials)}</div>
            <div>
              <h3>{escape(name_str)}</h3>
              <span>{escape(r.get("meta", "Verified Google Review"))}</span>
            </div>
            <div class="review-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          </div>
          <p class="review-text">“{escape(r.get("text", ""))}”</p>
        </article>""")

        maps_url = escape(biz.get("googleMapsUrl", "#"))
        reviews_section = f"""  <!-- Google Reviews Section -->
  <section id="reviews" class="section reviews-section">
    <div class="container">
      <div class="reviews-top">
        <div>
          <span class="eyebrow">Customer Feedback</span>
          <h2>{escape(reviews_data.get("headline", "Verified Google Reviews"))}</h2>
        </div>
        <div class="google-badge-card">
          <div class="google-score">{rating_score}</div>
          <div>
            <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
            <span style="font-size:0.82rem;color:#CBD5E1;">{rating_count}</span>
          </div>
          {f'<a href="{maps_url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-light">Google Maps &rarr;</a>' if maps_url != "#" else ''}
        </div>
      </div>
      <div class="reviews-grid">
{chr(10).join(r_cards)}
      </div>
    </div>
  </section>"""

    # Gallery Section
    gallery_items = cfg.get("gallery", [])
    gallery_section = ""
    if gallery_items:
        categories = sorted(list({g.get("category", "") for g in gallery_items if g.get("category")}))
        filter_bar = ""
        if len(categories) > 1:
            btns = ['<button type="button" class="filter-pill-btn active" data-filter="all">All Photos</button>']
            for c in categories:
                btns.append(f'<button type="button" class="filter-pill-btn" data-filter="{escape(c)}">{escape(c.title())}</button>')
            filter_bar = f'<div class="gallery-filters">{"".join(btns)}</div>'

        g_cards = []
        for g in gallery_items:
            g_cards.append(f"""        <figure class="gallery-card" data-category="{escape(g.get('category', 'all'))}">
          <img src="{escape(g.get('image', ''))}" alt="{escape(g.get('caption', ''))}" loading="lazy" />
          <figcaption>{escape(g.get('caption', ''))}</figcaption>
        </figure>""")

        gallery_section = f"""  <!-- Photo Gallery & Lightbox -->
  <section id="gallery" class="section">
    <div class="container">
      <div class="section-heading">
        <span class="eyebrow">Photos</span>
        <h2>{escape(cfg.get("galleryTitle", "Our Work & Facility"))}</h2>
      </div>
      {filter_bar}
      <div class="gallery-grid">
{chr(10).join(g_cards)}
      </div>
    </div>
  </section>
  <div class="lightbox-modal" id="lightboxModal" hidden>
    <button type="button" class="lightbox-close" id="lightboxClose" aria-label="Close">&times;</button>
    <img id="lightboxImg" src="" alt="" />
    <div class="lightbox-caption" id="lightboxCaption"></div>
  </div>"""

    # Contact Section (Adapts to Physical Address vs. Service Area Coverage)
    loc_card_title = "Service Area Coverage" if archetype == "service-mobile" else "Location & Address"
    loc_card_body = escape(biz.get("serviceAreaSummary", "")) if archetype == "service-mobile" else escape(biz.get("address", ""))

    contact_section = f"""  <!-- Contact Section -->
  <section id="contact" class="section section-alt">
    <div class="container contact-grid">
      <div>
        <span class="eyebrow">Get in Touch</span>
        <h2 style="font-size:clamp(1.75rem,3vw,2.35rem);font-weight:800;margin-bottom:0.75rem;">{escape(cfg.get("contactTitle", "Contact Us or Request Service"))}</h2>
        <p style="color:var(--brand-muted);margin-bottom:1.5rem;">{escape(cfg.get("contactSubtitle", "Reach out by phone or send us a message below."))}</p>
        {f'<div style="margin-bottom:1.5rem;"><a href="open-order.html" class="btn btn-primary btn-lg">{primary_cta_label} &rarr;</a></div>' if has_order_page else ''}
        <div class="contact-cards">
          <div class="contact-card">
            <h3>{loc_card_title}</h3>
            <p>{loc_card_body}</p>
          </div>
          <div class="contact-card">
            <h3>Phone &amp; Hours</h3>
            <p><strong>Phone:</strong> <a href="tel:{phone_digits}" style="color:var(--brand-primary);font-weight:700;">{escape(phone)}</a></p>
            <p>{escape(biz.get("hoursSummary", ""))}</p>
          </div>
        </div>
      </div>

      <div class="form-panel">
        <form id="contactForm">
          <h3 style="font-size:1.45rem;font-weight:800;margin-bottom:0.35rem;">Send Us a Message</h3>
          <p style="font-size:0.9rem;color:var(--brand-muted);margin-bottom:1.25rem;">We respond promptly to all inquiries.</p>
          <div class="form-row">
            <div class="form-group">
              <label for="c_name">Your Name *</label>
              <input type="text" id="c_name" name="Name" required placeholder="Jane Doe" />
            </div>
            <div class="form-group">
              <label for="c_phone">Phone Number *</label>
              <input type="tel" id="c_phone" name="Phone" required placeholder="(555) 555-0199" />
            </div>
          </div>
          <div class="form-group">
            <label for="c_email">Email Address</label>
            <input type="email" id="c_email" name="Email" placeholder="jane@example.com" />
          </div>
          <div class="form-group">
            <label for="c_message">How Can We Help? *</label>
            <textarea id="c_message" name="Message" rows="3" required placeholder="Tell us about your project, vehicle, or question..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary btn-block btn-lg">Send Message</button>
          <div id="formStatus" class="form-status" hidden></div>
        </form>
      </div>
    </div>
  </section>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(biz.get("name", ""))} | {escape(biz.get("seoSubtitle", ""))}</title>
  <meta name="description" content="{escape(biz.get("metaDescription", ""))}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{font_link}" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{header_html}
{hero_section}
{metrics_section}
{services_section}
{ba_section}
{products_section}
{about_section}
{reviews_section}
{gallery_section}
{contact_section}
{cart_drawer_html}
{footer_html}
</body>
</html>
"""
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # Generate Simplified Individual Service Pages if enabled
    detail_services = [s for s in services if s.get("hasDetailPage")]
    for idx, s in enumerate(detail_services, start=1):
        slug = s.get("slug", f"service-{idx}")
        code = escape(s.get("code", f"{idx:02d}"))
        title = escape(s.get("title", "Service"))
        summary = escape(s.get("summary", ""))
        desc = escape(s.get("description", summary))
        essentials = s.get("essentials", ["Contact Name & Phone", "Service Address", "Target Date", "Project Details"])
        ess_html = "\n".join([f"          <li>{escape(item)}</li>" for item in essentials])
        opts_html = "\n".join([
            f'            <option value="{escape(ds.get("slug", ""))}.html" {"selected" if ds.get("slug") == slug else ""}>{escape(ds.get("code", ""))} — {escape(ds.get("title", ""))}</option>'
            for ds in detail_services
        ])
        cta_target = f"open-order.html?type={escape(slug)}" if has_order_page else "index.html#contact"

        sub_header = render_header(cfg, has_order_page, has_products, is_subpage=True)
        svc_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{code}. {title} | {escape(biz.get("name", ""))}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{font_link}" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{sub_header}
  <main class="simple-service-page">
    <div class="container narrow-container">
      <div class="simple-service-topbar">
        <a href="index.html#services" class="service-link">&larr; All Services</a>
        <select aria-label="Switch Service" onchange="if(this.value) window.location.href=this.value;" style="padding:0.5rem 0.85rem;border-radius:8px;border:1px solid var(--brand-border);font-weight:600;">
{opts_html}
        </select>
      </div>
      <article class="simple-service-card">
        <span class="service-num-badge">SERVICE {code}</span>
        <h1 style="font-size:clamp(1.85rem,3.5vw,2.45rem);font-weight:800;margin:0.85rem 0 0.65rem;">{title}</h1>
        <p style="font-size:1.15rem;font-weight:600;color:var(--brand-primary);margin-bottom:0.85rem;">{summary}</p>
        <p style="color:var(--brand-muted);">{desc}</p>
        <div class="simple-essentials-box">
          <h2 style="font-size:0.9rem;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;">What You Need to Get Started</h2>
          <ul class="simple-essentials-list">
{ess_html}
          </ul>
        </div>
        <a href="{cta_target}" class="btn btn-primary btn-lg">Open a {title} Order &rarr;</a>
      </article>
    </div>
  </main>
{footer_html}
</body>
</html>
"""
        with open(os.path.join(out_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(svc_page_html)

    # Generate Dedicated Open Order Page (`open-order.html`) if enabled
    if has_order_page:
        sub_header = render_header(cfg, has_order_page, has_products, is_subpage=True)
        order_cfg = cfg.get("orderForm", {})
        dropdown_options = "\n".join([
            f'              <option value="{escape(s.get("slug", f"service-{i}"))}">{escape(s.get("code", f"{i:02d}"))} — {escape(s.get("title", "Service"))}</option>'
            for i, s in enumerate(services, start=1)
        ])
        open_order_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(order_cfg.get("pageTitle", "Open an Order"))} | {escape(biz.get("name", ""))}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{font_link}" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
{sub_header}
  <main class="open-escrow-page">
    <div class="container narrow-container">
      <div style="text-align:center;margin-bottom:1.75rem;">
        <span class="eyebrow">2-Minute Online Intake</span>
        <h1 style="font-size:clamp(2rem,4vw,2.65rem);font-weight:800;margin-bottom:0.4rem;">{escape(order_cfg.get("pageTitle", "Open a Service Order"))}</h1>
        <p style="color:var(--brand-muted);">{escape(order_cfg.get("pageSubtitle", f"Routed directly to {biz.get('recipientEmail', '')}"))}</p>
      </div>
      <div class="clean-order-card">
        <form id="serviceOrderForm">
          <div class="type-dropdown-banner">
            <label for="txTypeSelect">{escape(order_cfg.get("dropdownLabel", "Select Service / Order Type"))}</label>
            <select id="txTypeSelect" name="Service_Type">
{dropdown_options}
            </select>
            <p id="txTypeHelper" style="font-size:0.85rem;color:var(--brand-muted);margin-top:0.5rem;"></p>
          </div>

          <div class="clean-form-section">
            <div class="clean-section-title">
              <span class="clean-step-num">1</span>
              <h3>Service Details</h3>
            </div>
            <div id="dynamicServiceFieldsMount"></div>
          </div>

          <div class="clean-form-section" style="border-bottom:none;">
            <div class="clean-section-title">
              <span class="clean-step-num">2</span>
              <h3>Your Contact Information</h3>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="sub_name">Your Name *</label>
                <input type="text" id="sub_name" name="Submitted_By_Name" required placeholder="Jane Doe" />
              </div>
              <div class="form-group">
                <label for="sub_phone">Your Phone *</label>
                <input type="tel" id="sub_phone" name="Submitted_By_Phone" required placeholder="(555) 555-0199" />
              </div>
            </div>
            <div class="form-group">
              <label for="sub_email">Your Email *</label>
              <input type="email" id="sub_email" name="Submitted_By_Email" required placeholder="you@example.com" />
            </div>
            <div class="form-group">
              <label for="sub_notes">Additional Notes (Optional)</label>
              <textarea id="sub_notes" name="Additional_Notes" rows="2" placeholder="Any special instructions..."></textarea>
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-block btn-lg" id="orderSubmitBtn">Submit Order</button>
          <div id="orderFormStatus" class="form-status" hidden></div>
        </form>
      </div>
    </div>
  </main>
{footer_html}
</body>
</html>
"""
        with open(os.path.join(out_dir, "open-order.html"), "w", encoding="utf-8") as f:
            f.write(open_order_html)

    print(f"Built site for '{biz.get('name', '')}' -> {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 build_site.py <path/to/site.json> <output_directory>")
        sys.exit(1)
    build_site(sys.argv[1], sys.argv[2])
