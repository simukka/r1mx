---
layout: default
title: "RED ONE MX: Repair & Maintenance Reference"
---

<section class="hero">
  <p class="hero-eyebrow">Community Reference · Right to Repair</p>
  <h1 class="hero-title">RED ONE <span>MX</span></h1>
  <p class="hero-lead">
    An independent reference for owners, operators, and technicians who choose to
    keep RED ONE MX digital cinema cameras running. Specifications, hardware documentation,
    firmware history, and repair guides, preserved from the original era.
  </p>
  <div class="hero-image">
    <img src="{{ '/assets/images/redone-main.png' | relative_url }}"
         alt="RED ONE MX digital cinema camera"
         width="628" height="535" />
  </div>
  <div class="hero-badges">
    <span class="badge badge--red">14MP Mysterium-X™</span>
    <span class="badge badge--red">4.5K RAW</span>
    <span class="badge badge--gray">Super 35mm</span>
    <span class="badge badge--gray">REDCODE™ 42</span>
    <span class="badge badge--gold">Right to Repair</span>
  </div>
</section>

<div class="spec-grid">
  <div class="spec-cell">
    <div class="spec-cell-label">Sensor</div>
    <div class="spec-cell-value">14 <small>MP Mysterium-X™</small></div>
  </div>
  <div class="spec-cell">
    <div class="spec-cell-label">Max Resolution</div>
    <div class="spec-cell-value">4.5K <small>(4480×1920)</small></div>
  </div>
  <div class="spec-cell">
    <div class="spec-cell-label">Dynamic Range</div>
    <div class="spec-cell-value">13+ <small>stops</small></div>
  </div>
  <div class="spec-cell">
    <div class="spec-cell-label">Pixel Array</div>
    <div class="spec-cell-value">5120 <small>× 2700</small></div>
  </div>
  <div class="spec-cell">
    <div class="spec-cell-label">REDCODE™</div>
    <div class="spec-cell-value">28/36/42 <small>12-bit RAW</small></div>
  </div>
  <div class="spec-cell">
    <div class="spec-cell-label">Body</div>
    <div class="spec-cell-value">~10 <small>lbs aluminum</small></div>
  </div>
</div>

## About the RED ONE MX

The **RED ONE** was released in 2007 as the first digital cinema camera capable of capturing
true 4K RAW footage, effectively the resolution equivalent of 35mm film, in a form factor
accessible to independent filmmakers.

In late 2010, RED Digital Cinema introduced the **Mysterium-X™** (MX) sensor upgrade:
a 14-megapixel replacement for the original 12-megapixel Mysterium™ sensor. The upgrade
delivered improved dynamic range (13+ stops), better low-light performance, expanded ISO
range (up to ISO 6400), and opened the door to REDCODE 42 compression at 3K and 2K
resolutions.

> *"From the very early single digit firmware builds to its current state, the RED ONE has
> increased its resolution (4K to 4.5K), improved compression (REDCODE 42), boosted dynamic
> range and low light performance (Mysterium-X™) and added dozens and dozens of features."*
> - RED Digital Cinema product page, ~2010

## The Camera Today

<img src="{{ '/assets/images/obsolete.png' | relative_url }}"
     alt="RED Renders Obsolescence Obsolete"
     class="section-heading-img" />

Both the RED ONE and RED ONE MX have been **discontinued** and are no longer covered by
warranty or serviceable by the manufacturer. Yet these cameras remain capable tools:
capable of producing footage that holds up to modern distribution standards, and are in
active use around the world.

The challenge is that when something breaks, **there is almost no public documentation**
to help. The [r1mx project](https://github.com/simukka/r1mx) exists to change that:
reverse engineering the hardware, documenting failure modes, and building the repair knowledge
base that RED never published.

<div class="callout callout--warn">
  <strong>Disclaimer:</strong> This site is an independent community reference for
  educational purposes. It is not affiliated with or endorsed by RED Digital Cinema.
  RED ONE and RED ONE MX cameras are complex precision instruments; always exercise
  appropriate care when performing any maintenance or repair.
</div>

## What We Are Building

<div class="future-teaser">
  <div class="future-teaser-label">Road Forward</div>
  <div class="future-teaser-title">Build 32.1 + Replacement Hardware</div>
  <p>
    The r1mx project is developing new firmware that removes SSD restrictions, FreeCAD
    models for a printable replacement REDMAG module, and a replacement SSD side module.
    All files, BOMs, and instructions will be free and public. Kits and pre-assembled
    options will be available for those who want them.
  </p>
  <div class="btn-row" style="justify-content:flex-start; margin-bottom:0.5rem;">
    <a class="btn btn--red" href="{{ '/roadmap' | relative_url }}">See the Roadmap</a>
    <a class="btn btn--outline" href="https://github.com/sponsors/simukka" target="_blank" rel="noopener">Sponsor the Project</a>
  </div>
</div>

## Navigate

<div class="nav-cards">
  <a class="nav-card" href="{{ '/specs' | relative_url }}">
    <div class="nav-card-icon">📐</div>
    <div class="nav-card-title">Technical Specifications</div>
    <div class="nav-card-desc">Full sensor, codec, format, and I/O specs for the RED ONE and RED ONE MX.</div>
  </a>
  <a class="nav-card" href="{{ '/components' | relative_url }}">
    <div class="nav-card-icon">🔧</div>
    <div class="nav-card-title">Components & Accessories</div>
    <div class="nav-card-desc">All optional modules: storage, power, monitoring, RED-RAIL system, and lenses.</div>
  </a>
  <a class="nav-card" href="{{ '/hardware' | relative_url }}">
    <div class="nav-card-icon">🔩</div>
    <div class="nav-card-title">Hardware Reference</div>
    <div class="nav-card-desc">PCB boards, key ICs, and interconnects from the r1mx reverse engineering project.</div>
  </a>
  <a class="nav-card" href="{{ '/firmware' | relative_url }}">
    <div class="nav-card-icon">💾</div>
    <div class="nav-card-title">Firmware History</div>
    <div class="nav-card-desc">Complete build history from Build 3 (v1.0.4) through Build 32 (v32.0.3).</div>
  </a>
  <a class="nav-card" href="{{ '/guides' | relative_url }}">
    <div class="nav-card-icon">🛠</div>
    <div class="nav-card-title">Repair Guides</div>
    <div class="nav-card-desc">iFixit-style guides from tightening bolts to repairing broken traces. Contribute a guide.</div>
  </a>
  <a class="nav-card" href="{{ '/resources' | relative_url }}">
    <div class="nav-card-icon">📚</div>
    <div class="nav-card-title">Resources</div>
    <div class="nav-card-desc">External references, Wayback Machine archives, and community links.</div>
  </a>
  <a class="nav-card" href="{{ '/roadmap' | relative_url }}">
    <div class="nav-card-icon">🚀</div>
    <div class="nav-card-title">Roadmap</div>
    <div class="nav-card-desc">Build 32.1 firmware, replacement REDMAG module, and the path to a community marketplace.</div>
  </a>
</div>

## What People Said

<div class="quote-block">
  <p>"Shooting with RED is like hearing The Beatles for the first time. RED sees the way I see…
  Is it perfect? Not yet. But the flaws are fixable."</p>
  <div class="quote-attribution">- Steven Soderbergh, Director (Ocean's Eleven, Traffic)</div>
</div>

<div class="quote-block">
  <p>"I liked what they were doing, making a digital camera of the utmost quality, and making
  it affordable for indie filmmakers."</p>
  <div class="quote-attribution">- Peter Jackson, Director (Lord of the Rings)</div>
</div>

<div class="quote-block">
  <p>"We have 16mm and 35mm cameras here from the 80s that are still being used. People still use
  Konvas that are 30 years old. The technology will get better, no doubt. But I'm sure Red will
  last generations… resolution will maintain itself."</p>
  <div class="quote-attribution">- Jarred Land, RED Digital Cinema (2007)</div>
</div>
