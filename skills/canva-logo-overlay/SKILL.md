---
name: canva-logo-overlay
description: Use when overlaying a company logo onto property images using the Canva MCP integration to produce branded real estate photos at exact dimensions
---

# Canva Logo Overlay

## Overview
Brands property images with a company logo using Canva MCP. Creates one reusable canvas, locks the logo in position, then swaps each property image in/out — far faster than rebuilding a design per image.

## Intake Questions (Ask Every Run)

Before starting, always ask:

1. **Source folder**: What is the full path to the folder containing the property images?
2. **Property address**: What is the property address? (Used to name the output folder.)
3. **Company**: Which company's branding? (Used to look up logo in brand-themes.)
4. **Output location**: Where should finished images be saved?
   - Default: `C:\Users\joshu\Downloads\[property address] finished\`
   - Alternatives: custom path, or email to joshua@webberinvestmenthomes.com

## Brand Assets

**Root folder:** `C:\Users\joshu\brand-themes\`

| Company | Folder | Logo File |
|---------|--------|-----------|
| Rent to Own Cribs | `rent-to-own-cribs` | `logo-transparent.png` |

**Logo reference (Rent to Own Cribs):**
- Two-tone house icon (steel blue + olive/gold) with "Rent2OwnCribs.com" wordmark
- Tagline: "DON'T JUST RENT A CRIB – OWN IT"
- Source file: `C:\Users\joshu\brand-themes\rent-to-own-cribs\logo-transparent.png`
- Native size: 642 × 388 px (transparent background)

**Adding a new company:** If the brand folder doesn't exist yet, ask for the logo file path, create `C:\Users\joshu\brand-themes\[company-name]\`, and save it as `logo-transparent.png` before proceeding.

## Canvas & Logo Specifications

| Element | Dimensions | Notes |
|---------|-----------|-------|
| Canvas | **940 × 646 px** | Always resize canvas to this — source images may vary |
| Property image | 940 × 646 px | Fill canvas edge-to-edge; send to back |
| Logo overlay | **410 × 248 px** | Bottom-right, 15px from each edge |

**Logo pixel coordinates (bottom-right, 15px padding):**
- Left edge: `940 − 410 − 15 = 515 px from left`
- Top edge: `646 − 248 − 15 = 383 px from top`

## Canva Workflow

### One-Time Setup (do once per batch)

1. **Upload the logo** to Canva using `upload-asset-from-url` (or file upload).
2. **Create a new design** at exactly 940 × 646 px.
3. **Add logo** at 410 × 248 px, positioned at (515, 383) — bottom-right corner.
4. **Lock or group the logo** so it doesn't move when images are swapped.

### Per-Image Loop (repeat for every property image)

```
For each image in the source folder:
  1. Upload property image to Canva.
  2. Place image on the canvas — resize/fill to 940 × 646 px edge-to-edge.
  3. Send image to back (logo must remain on top).
  4. Export / download design as JPG or PNG.
  5. Save exported file to the output folder.
  6. Remove the property image from the canvas (logo stays in place).
  7. Proceed to next image.
```

**Key rule:** Never move or resize the logo between images. Only the background image changes.

### After All Images Are Processed

- Confirm count: "X images processed and saved to [output folder]."
- Offer to email the folder if the user selected email delivery.

## Output Folder

Name format: `[property address] finished`
Default path: `C:\Users\joshu\Downloads\[property address] finished\`

Create the folder before processing the first image.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Canvas is wrong size | Always set canvas to 940×646 before placing anything — source images vary |
| Logo drifts between images | Lock/group the logo after placing it; never touch it during the loop |
| Property image covers logo | Always send property image to back after placing |
| Logo wrong size | Explicitly resize to 410×248 — do not scale by eye |
| Output folder missing | Create folder first, not after the first export |
