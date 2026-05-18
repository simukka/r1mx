---
layout: page
title: The Road Forward
subtitle: What we are building and how you can help keep RED ONE MX cameras alive
permalink: /roadmap/
---

<div class="roadmap-hero">
  <div class="roadmap-hero-label">Project Roadmap</div>
  <div class="roadmap-hero-title">The RED ONE MX<br>Is Not Done Yet</div>
  <p class="roadmap-hero-body">
    RED stopped. We did not. The r1mx project is actively developing new firmware,
    replacement hardware modules, and the documentation needed to keep these cameras
    running for another decade. This page is an honest account of where we are,
    what we are building, and what it takes to get there.
  </p>
</div>

---

## Where We Are Now

The r1mx project has spent several years reverse engineering the RED ONE MX camera body:
documenting PCB boards, identifying every key IC, decrypting and analyzing firmware builds,
and researching the SSD storage subsystem. The foundation is solid.

What remains is the hard part: turning research into reliable, reproducible hardware and
firmware that anyone can use to repair or extend the life of their camera.

---

## What We Are Building

<div class="milestones">

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--active"></div>
      <span class="status-label">Active Research</span>
    </div>
    <div class="milestone-title">Firmware Build 32.1<br>Any-SSD Support</div>
    <p class="milestone-desc">
      The RED ONE MX firmware validates replacement SSDs against a hardcoded approved-drive
      list. Build 32.1 removes this restriction, allowing any compatible SATA SSD to be
      used inside a REDMAG housing. This is the single most impactful thing we can do
      for camera owners today.
    </p>
    <div class="milestone-tags">
      <span class="tag">Firmware</span>
      <span class="tag">VxWorks</span>
      <span class="tag">SSD</span>
    </div>
  </div>

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--active"></div>
      <span class="status-label">Design In Progress</span>
    </div>
    <div class="milestone-title">Replacement REDMAG<br>SSD Module</div>
    <p class="milestone-desc">
      A drop-in replacement REDMAG housing designed in FreeCAD. Uses a standard
      off-the-shelf 2.5" SATA SSD. FreeCAD models already exist for the enclosure
      and SSD board. The goal is a design that anyone can print and assemble,
      or receive as a pre-built kit.
    </p>
    <div class="milestone-tags">
      <span class="tag">FreeCAD</span>
      <span class="tag">3D Print</span>
      <span class="tag">BOM Available</span>
    </div>
  </div>

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--active"></div>
      <span class="status-label">Design In Progress</span>
    </div>
    <div class="milestone-title">SSD Side Module<br>Replacement</div>
    <p class="milestone-desc">
      The SSD side module is the physical enclosure that attaches to the camera body and
      houses the REDMAG. Without it, REDMAG SSD storage cannot be used at all; cameras
      configured for CF or Hard Drive require this module to switch to SSD. FreeCAD models
      are in progress. Combined with the replacement REDMAG design and Build 32.1 firmware,
      this completes the full storage replacement path.
    </p>
    <div class="milestone-tags">
      <span class="tag">FreeCAD</span>
      <span class="tag">STL</span>
      <span class="tag">Hardware</span>
    </div>
  </div>

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--future"></div>
      <span class="status-label">Future Goal</span>
    </div>
    <div class="milestone-title">Marketplace<br>Buy, Sell, Trade</div>
    <p class="milestone-desc">
      A dedicated marketplace for RED ONE MX cameras, components, and accessories.
      Peer-to-peer, community-run. No fees, no middlemen. Just a trusted place for
      RED ONE MX owners to find what they need.
    </p>
    <div class="milestone-tags">
      <span class="tag">Community</span>
      <span class="tag">Future</span>
    </div>
  </div>

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--future"></div>
      <span class="status-label">Future Goal</span>
    </div>
    <div class="milestone-title">Certified by Kyle<br>Camera Inspection</div>
    <p class="milestone-desc">
      Send your camera in for a full inspection and functionality test against the
      r1mx diagnostic checklist. Cameras that pass receive a "Certified by Kyle"
      designation, giving buyers confidence in the used market.
    </p>
    <div class="milestone-tags">
      <span class="tag">Service</span>
      <span class="tag">Marketplace</span>
      <span class="tag">Future</span>
    </div>
  </div>

  <div class="milestone">
    <div class="milestone-status">
      <div class="status-dot status-dot--planned"></div>
      <span class="status-label">Planned</span>
    </div>
    <div class="milestone-title">Full Schematics<br>All Boards</div>
    <p class="milestone-desc">
      Complete KiCad schematics for every PCB board in the RED ONE MX: AUDIO_PCI,
      CPU_IO, UI, SENSOR, and POWER boards. The foundation for understanding every
      possible failure mode.
    </p>
    <div class="milestone-tags">
      <span class="tag">KiCad</span>
      <span class="tag">Schematics</span>
      <span class="tag">Research</span>
    </div>
  </div>

</div>

---

## How to Get the Hardware

Everything this project produces is open and free. The design files, BOMs, firmware patches,
and build instructions will all be published in the repository. There are two ways to
turn those files into a working part:

<div class="two-path">
  <div class="path-card">
    <div class="path-card-icon">🛠</div>
    <div class="path-card-title">Do It Yourself</div>
    <ul>
      <li>Download FreeCAD models and STL files from the repository</li>
      <li>Print the enclosure on any FDM printer (PLA or PETG)</li>
      <li>Source parts from the published BOM (all off-the-shelf components)</li>
      <li>Flash Build 32.1 firmware to your camera</li>
      <li>Follow the step-by-step assembly guide</li>
      <li>Community support via GitHub Issues</li>
    </ul>
  </div>
  <div class="path-card path-card--highlight">
    <div class="path-card-icon">📦</div>
    <div class="path-card-title">Kit (Pre-sourced Parts)</div>
    <ul>
      <li>Receive a kit with all parts pre-sourced and verified</li>
      <li>Printed enclosure included, ready for assembly</li>
      <li>Detailed assembly instructions included</li>
      <li>Pre-assembled option available: pay for assembly time</li>
      <li>Proceeds go directly toward continued r1mx research</li>
      <li>Contact Kyle via the repository to arrange</li>
    </ul>
  </div>
</div>

<div class="callout callout--info">
  <strong>No minimum orders, no company, no profit motive.</strong> The kit option exists
  because sourcing 25 individual components from 6 different suppliers is a real barrier
  for non-technical users. Pre-assembly is offered at cost-of-time only. If you want to
  do it yourself, every file and instruction you need will be free and public.
</div>

---

## The Real Cost

This is honest accounting. Research and hardware development has real costs:

<div class="cost-table" markdown="1">

| What costs money | Why it matters |
|---|---|
| **Prototype prints and iterations** | Every design revision requires printing and testing to verify fit and function. A single REDMAG revision costs ~$20-40 in materials and several hours of time. |
| **Component sourcing** | Verifying BOM accuracy means buying and testing multiple parts. A single BOM validation run for the REDMAG module costs ~$80-150 in parts. |
| **Firmware testing** | Testing firmware patches requires having multiple camera bodies. Camera bodies cost $800-$2,000 each on the used market. |
| **Time** | Every hour spent on r1mx is an hour not spent on paid work. The research phase alone has consumed hundreds of hours. |

</div>

None of this is asking for investment in a product. It is asking for support to continue
research that benefits every RED ONE MX owner who will never send a dollar.

---

## Support This Project

<div class="sponsor-cta">
  <h3>Keep RED ONE MX Cameras Running</h3>
  <p>
    If this project has helped you, or if you want to see Build 32.1 and the replacement
    REDMAG module become a reality, consider sponsoring the work. Every contribution
    goes directly toward hardware prototyping, component testing, and the time required
    to turn research into reliable, publishable designs.
  </p>
  <div class="btn-row">
    <a class="btn btn--red" href="https://github.com/sponsors/simukka" target="_blank" rel="noopener">
      Sponsor on GitHub
    </a>
    <a class="btn btn--outline" href="https://github.com/simukka/r1mx/issues" target="_blank" rel="noopener">
      Contribute on GitHub
    </a>
  </div>
</div>

### Other Ways to Help

Sponsorship is not the only way. These contributions are equally valuable:

- **Share your repair experience** - open an issue with anything you have found while debugging your camera
- **Contribute measurements** - probing components with a multimeter and submitting readings helps complete the schematics
- **Test firmware patches** - if you have a working RED ONE MX and are comfortable with firmware upgrades, become a tester
- **Send your broken camera** - cameras that no longer function are valuable for destructive analysis
- **Spread the word** - the more RED ONE MX owners who know this project exists, the larger the knowledge base becomes

---

## Future Vision: Marketplace and Certification

The long-term goal is more than repair documentation. It is a sustainable ecosystem for
people who choose to keep shooting on RED ONE MX cameras.

### Community Marketplace

A dedicated space for RED ONE MX owners to buy, sell, and trade cameras and components.
The used market for these cameras is scattered across eBay, Facebook Marketplace, and
forums, with no shared understanding of what a camera is worth or what condition it is in.
A focused marketplace changes that.

### Certified by Kyle

A voluntary inspection and certification service. Send your camera to Kyle, and it is
tested against the full r1mx diagnostic checklist:

- Firmware version and functionality
- All storage interfaces (CF, SSD, RED DRIVE)
- All video outputs (HD-SDI, HDMI)
- Audio input and output
- Power system and battery compatibility
- Sensor functionality and black shade calibration
- Physical condition assessment

Cameras that pass receive a dated "Certified by Kyle" designation with a public record
in the r1mx registry. This gives buyers in the marketplace a meaningful baseline for
what they are purchasing.

<div class="callout callout--info">
  These are future goals that depend on the project reaching a sustainable footing
  through sponsorship and community growth. Follow the
  <a href="https://github.com/simukka/r1mx">repository</a> for updates.
</div>
