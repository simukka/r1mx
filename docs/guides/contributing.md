---
layout: guide
title: "Contributing a Guide"
subtitle: "How to write a repair guide for the RED ONE MX - template and instructions"
difficulty: Easy
time: "30-60 minutes"
tools: []
parts: []
category: meta
status: available
permalink: /guides/contributing/
---

## Overview

Anyone can write a guide for this project: experienced repair technicians, camera owners
who have worked through a problem, or AI agents working from documentation. The format is
designed so that guides can be published as **text-only drafts** and photos added later
by anyone who has the camera in hand.

Every guide in this project follows the same structure so readers know what to expect.

---

## Guide Format

### Front Matter (required)

Copy this block to the top of your guide file:

```yaml
---
layout: guide
title: "Your Guide Title"
subtitle: "One sentence describing what this guide covers and why it matters"
difficulty: Easy          # Easy | Medium | Hard
time: "20 minutes"        # realistic estimate including setup and cleanup
tools:
  - Tool name (e.g. Torx T6 screwdriver)
  - Another tool
parts:
  - Part name and part number if known
  - Leave this list empty ([]) if no parts are needed
category: maintenance     # maintenance | media | firmware | diagnosis | repair
status: available         # available | draft
permalink: /guides/your-guide-slug/
---
```

**Difficulty guide:**
- **Easy** - No disassembly, no soldering, low risk of damage if instructions are followed
- **Medium** - Partial disassembly or requires care; mistake could damage something
- **Hard** - Full disassembly, soldering, microscope work, or high risk of further damage

---

### Overview Section (required)

Start with a short paragraph explaining:

1. What the guide covers
2. When to use it (what symptoms or situations call for this procedure)
3. What the outcome will be

---

### Safety / Before You Start (include if relevant)

Use a callout block for any safety warnings:

```markdown
<div class="callout callout--warn">
  Warning text here.
</div>
```

Use `callout--info` for informational notes, `callout--warn` for cautions.

---

### Steps (required)

Each step uses this HTML block:

```html
<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Short action title.</strong>
    <p>Detailed explanation of what to do, what to watch for, and any warnings
    specific to this step.</p>
  </div>
</div>
```

Increment the number for each step. Keep each step focused on a single action.

---

### Photo Placeholders (use when you cannot take a photo)

Where a photo would help, add this block:

```html
<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: describe exactly what the photo should show
</div>
```

Be specific. "Photo of board" is not useful. "Close-up of J7 connector on CPU_IO board,
showing the 180-position mezzanine socket from above" is useful.

---

### Attribution (required if based on external sources)

If your guide is based on a REDuser.net thread, forum post, or another person's work,
add an attribution block immediately after the section it relates to:

```html
<div class="guide-attribution">
  <strong>Source:</strong> Based on findings by <strong>username</strong> at
  <a href="https://reduser.net/threads/..." target="_blank" rel="noopener">thread title</a>
  (REDuser.net, YYYY). Used with thanks.
</div>
```

Always credit the original author. If you found information across multiple threads,
add an attribution block per source or list them all in a "Sources" section at the end.

---

### Troubleshooting Table (optional but encouraged)

A table of things that can go wrong:

```markdown
| Problem | Likely cause | Fix |
|---|---|---|
| Camera does X | Reason | Action to take |
```

---

### See Also (optional)

Link to related guides or pages on this site:

```markdown
## See Also

- [Related guide title]({{ '/guides/related-slug' | relative_url }})
- [Hardware Reference]({{ '/hardware' | relative_url }})
```

---

## File Naming and Location

- Place your file in `docs/guides/` directory
- Use lowercase kebab-case for the filename: `replacing-the-cooling-fan.md`
- Set `permalink: /guides/your-slug/` in front matter to match

---

## Submitting

1. Fork [github.com/simook/r1mx](https://github.com/simook/r1mx)
2. Add your guide file to `docs/guides/`
3. Add a link to your guide in `docs/guides.md` (copy an existing `guide-list-item` block and change `planned` to `available`)
4. Open a pull request with a brief description of what you documented

---

## Complete Example

See [Black Shading Calibration]({{ '/guides/black-shading-calibration' | relative_url }})
for a complete example of a finished guide using this format.

---

## Notes for AI Agents

If you are an AI agent writing a guide:

- Do not invent procedures. Only document what is confirmed by the r1mx project, the
  RED ONE Operation Guide, or cited REDuser.net threads.
- Add photo placeholder blocks for every step that involves a physical action.
- Write attribution blocks for every source used.
- Set `status: draft` in front matter. A human should review before setting `status: available`.
- Do not use em dashes in any content. Use `:`, `;`, `,`, or `-` instead.
