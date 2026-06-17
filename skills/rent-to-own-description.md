# Rent to Own Cribs – Property Description Generator

Generate a listing description for a Rent2OwnCribs property in the established brand voice and format.

---

## When invoked

Ask the user the following questions **all at once** in a single message — numbered and clearly labeled so they can answer each one:

---

**Questions to ask:**

1. **Address** — Full property address (street, city, state, zip)?
2. **Property value** — What is the current appraised or market value of the property (this is NOT the sales price — we calculate that from it)?
3. **Interest rate** — What interest rate should the monthly payment be based on (e.g. 8%, 8.5%, 9%)?
4. **Estimated monthly insurance** — What do you estimate monthly homeowners insurance to be (e.g. $120/mo)?
5. **PMI** — Is Private Mortgage Insurance (PMI) included? If yes, what is the monthly amount?
6. **Garage / Carport / Parking** — Any garage, carport, or notable parking to highlight (e.g. 2-car garage, 1-car carport, extended driveway)? If none, say "none."
7. **Home inspection** — Is a home inspection report included for review?
8. **Move-in ready?** — Is the home move-in ready, or are there known issues to disclose?
9. **Special features** — Any standout items to highlight? (e.g. appliances included, security system, recent full renovation, mini splits, fireplace, bonus room, privacy fence, covered patio, etc.)
10. **Property photos folder** — What is the folder path or name containing the property photos? (e.g. "4513 48th St" inside Downloads, or a full path)

---

## After receiving answers

### Step 1 — Calculate the sales price

**Sales price** = Property value × 1.10, then round DOWN to the nearest $5,000
- Formula: floor((property value × 1.10) / 5000) × 5000
- Example: $120,000 × 1.10 = $132,000 → $130,000
- Example: $180,000 × 1.10 = $198,000 → $195,000

---

### Step 2 — Calculate the monthly payment

**Important:** The monthly payment is calculated on the FULL sales price (not reduced by the deposit). The deposit is an option fee, not a traditional down payment.

**Monthly P&I** using 30-year amortization on the full sales price:
- r = annual interest rate ÷ 12
- n = 360 (months)
- P&I = Sales price × [r × (1 + r)^360] ÷ [(1 + r)^360 − 1]

**Monthly taxes** = Look up the property's most recent annual tax amount from the Central Appraisal District (CAD) for that county using WebSearch (e.g. "lcad.org" for Lubbock County, or the relevant county CAD). Divide annual taxes by 12.

**Total monthly payment** = P&I + monthly taxes + monthly insurance + PMI (if applicable)

**Round up to the nearest $5 (always ceiling):**
- Example: $1,231 → $1,235 | $1,236 → $1,240 | $1,240 → $1,240

This rounded total is the number shown in the listing as `~$[amount]/mo`. Call this value **PITI**.

---

### Step 3 — Calculate the down payments

Using the PITI calculated in Step 2 and the sales price from Step 1:

**Rent to Own down payment:**
= (85% × PITI × 3) + $1,500 + (0.5% × sales price)
- Round to the nearest $100
- Example: PITI $2,500 / price $265,000 → (0.85 × 2500 × 3) + 1500 + (0.005 × 265000) = 6,375 + 1,500 + 1,325 = **$9,200**

**Seller Finance down payment:**
= (85% × PITI × 6) + $3,500 + $1,500 + (1% × sales price)
= (85% × PITI × 6) + $5,000 + (1% × sales price)
- Round to the nearest $100
- Example: same inputs → (0.85 × 2500 × 6) + 5000 + (0.01 × 265000) = 12,750 + 5,000 + 2,650 = **$20,400**

These numbers plus the sales price populate the header block.

---

### Step 4 — Read the photos
Use the Read tool on each image in the provided folder. Start with exterior/front-of-home shots and work inward. Note:
- Exterior: siding material and color, trim color, roof, driveway, yard, trees, fence, garage
- Entry and living areas: flooring type and color, wall color, ceiling details (beams, fans, recessed lighting), fireplace, accent walls, natural light
- Kitchen: cabinet color/style, countertops, backsplash, appliances, island/bar layout
- Bedrooms: size feel, flooring, ceiling fans, any built-ins
- Bathrooms: vanity style, tile, fixtures, shower vs tub
- Backyard/outdoor: patio, fence, storage, usable space

### Step 4 — Look up property details and research

**CAD lookup (do this first):**
Search the county Central Appraisal District for the property address. For Lubbock County use lubbockcad.org (note: the site blocks direct fetch — use WebSearch to find property data, or as a fallback ask the user to confirm details from lubbockcad.org directly). For other counties search "[county name] central appraisal district" to find the right site. Pull the following:
- Bedrooms
- Bathrooms
- Square footage (living area)
- Lot size
- Year built
- Annual property taxes (needed for monthly payment calculation in Step 2)

**After pulling CAD data, pause and confirm with the user before continuing:**
Present what you found in a short block, for example:
> "Here's what I found on the CAD for [address]:
> • 3 bed / 2 bath / 1,542 sqft / Lot: 0.18 acres / Built: 1978
> • Annual taxes: $2,840 (~$237/mo)
> Does this look correct, or do you want to update anything?"

Only proceed to the next steps once the user confirms.

**Additional research:**
- School district serving that address
- Notable cross streets or nearby landmarks (major roads, parks, shopping)
- Neighborhood character if helpful (quiet residential, close to downtown, etc.)

### Step 5 — Determine family size fit
Based on bedroom count AND square footage together:
- 2 bed / under 1,000 sqft → ideal for 1–3 people / couple or small family
- 3 bed / 1,000–1,300 sqft → ideal for a family of 3–5
- 3 bed / 1,300–1,600 sqft → ideal for a family of 3–5, comfortable for up to 6
- 3 bed / 1,600–2,000 sqft → ideal for a family of 4–6
- 4 bed / 2,000+ sqft → ideal for a large family of 4–6+, or 5–7+

---

## Output format

Generate the description exactly in this structure:

---

RENT TO OWN – $[RTO down] ([RTO %])
SELLER FINANCE – $[SF down] ([SF %])
Home is move-in ready! 🏡
[OR: Home inspection report included for review — if inspection is included instead]

🏠 Price: $[price]
📍 Address: [full address]
[beds] Bedrooms • [baths] Bathroom(s) • [garage/carport line if applicable] • [sqft] SqFt
[lot size line if notable]
Rent to Own payment: ~$[monthly]/mo (based on [rate]% interest — taxes & insurance included)
We do check credit, but your income matters most. 💳
Call our office: 8-zero-6-615-two-two-33 to schedule a tour 📞
To schedule a tour on your own go to Rent2OwnCribs Dot Com and click on "Schedule Walkthrough"

[BODY — 4 to 7 paragraphs structured as follows:]

**Paragraph 1 — Opening + exterior:**
Open with excitement ("We're excited to present / offer..."), give the address and a brief overview. Immediately move to curb appeal — exterior material and color, trim, roof style, driveway, yard, mature trees, and overall street presence. Mention the lot if notable (corner lot, large yard, etc.).

**Paragraph 2 — Entry / first impression inside:**
Describe what you see stepping inside. Flooring, wall color, ceiling height or details, natural light, open concept vs defined rooms. Set the overall interior tone.

**Paragraph 3 — Living area(s) and kitchen:**
Describe the main living room features (fireplace, beams, lighting, fans, accent walls). If there is a second living area or bonus room, call it out and suggest uses (home office, playroom, media room). Then flow into the kitchen — cabinets, countertops, backsplash, layout (island, bar, L-shape), appliances if included.

**Paragraph 4 — Bedrooms and bathrooms:**
Describe the primary/master bedroom and its bathroom. Then cover secondary bedrooms and shared bath(s). Be specific about finishes. Mention ceiling fans, flooring, built-ins if visible in photos.

**Paragraph 5 — Outdoor space / backyard:**
Describe the backyard, patio, fence, storage, and how it can be used. Connect to family lifestyle (gatherings, kids, pets, grilling).

**Paragraph 6 — Special features (if applicable):**
Only include if there are standout add-ons: security system, appliances included, mini splits, recent full renovation, bonus storage, extended garage potential, etc. Use 🔐 for security, ❄️🔥 for mini splits, 🚗 for standout parking/garage, ☀️ for outdoor entertaining.

**Paragraph 7 — Family fit + closing:**
Mention who this home is ideal for (family size based on beds + sqft). Close with a natural urgency statement that fits the tone — not desperate, just confident.

---

Call our office: 8-zero-6-615-two-two-33 to schedule a tour 📞
To schedule a tour on your own go to Rent2OwnCribs Dot Com and click on "Schedule Walkthrough"
Our homes move quickly, so reach out as soon as possible!

---

## Style rules

- **Always start outside, work inside** — curb appeal → entry → living → kitchen → bedrooms/baths → outdoor → close
- **Be specific about finishes** — never say "nice kitchen," say "gray cabinetry, granite countertops, stone-style backsplash"
- **Connect features to family use** — every room description should mention how a family would live in it
- **Family size fit is always included** — derive it from beds + sqft together
- **Phone number** — always written as `8-zero-6-615-two-two-33` (never as digits)
- **Website** — always written as `Rent2OwnCribs Dot Com` (never as a URL)
- **Emojis in the body** — maximum 2–3, only when genuinely warranted (🚗 standout parking, ☀️ outdoor entertaining, 🔐 security system, ❄️🔥 mini splits, 🌳 notable yard/trees). Never scatter emojis throughout body prose.
- **Emojis in the header block** — 🏠 Price, 📍 Address, 💳 credit line, 📞 phone, 🏡 or 📌 on status line
- **Tone** — confident, warm, direct. Reads like someone who knows the home well and is describing it honestly to a real family. No fluff, no overselling.
- **Sentence rhythm** — mix short punchy sentences with longer descriptive ones. Never a wall of text.
- **Numbers in the body** — always use digits (e.g. "2,344 square feet", "4 bedrooms", "5 to 7 people"). The only exception is the phone number, which is always written as `8-zero-6-615-two-two-33`
