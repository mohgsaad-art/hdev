# EV Scope landing page: Bob's likes and dislikes

Compiled 29 Oct 2026. Sources:
- this chat (landing v1 to v9);
- earlier chats: "UI demo mockups", "Website color and demo redesign", "Dynamic HTML landing page";
- project docs `landing-page-brief-2026-10-28.md` and `landing-copy-notes-2026-10-28.md`;
- project memory.

Quotes are Bob's own words. Where his feedback changed over time, the latest instruction wins, and the change is flagged under "Conflicts".

---

## 1. Reference and overall feel

**He likes**
- **patensify.com.** Dynamic, alive, "simple effective well made and aesthetic". What he means:
  - things move while you scroll;
  - elements keep subtly animating on screen even after you stop scrolling;
  - high-quality, smooth elements and transitions;
  - "not a goofy svg or sketch".
- **Minimal, clean, aesthetic.** "Not cluttered and confusing."
- **A product-style presentation.** Premium images (vehicles, charger) placed on a blank canvas, the way a product site shows a product. "No images used on the blank canvas as a product style" was a complaint about v9.
- **Subtle and smooth effects** everywhere. "Subtle" is his most repeated word.
- **Creativity.** "Useful creativity", "be creative". He liked the parts of v3–v4 that borrowed Patensify's ideas.
- **A credible engineering company page.** He should be able to send it to a municipality or an OEM without embarrassment.
- **For the tool itself** (useful context): a serious, trusted industry tool, like what a consultancy or bank puts out. Modern, simple yet technical. Not "websitey", not a gimmick, not dated Windows-XP style.

**He hates**
- **Long text pages.** "Scroll until eternity where we keep explaining all bullshit." He called v1 a "novel".
- **SVG illustrations, sketches or cartoon art** of any kind ("svg bull shit", "svg in your face trash").
- **The generic AI/SaaS look.** "Candy land", "AI made slop", "fake ads", "goofy".
- **Empty, still, blank pages** ("soulless, empty, blank, hollow, still").
- **Children's-book styling.** "Childrens rhyme book", cartoon moving trucks.
- **Dark "space" heroes**, gradient or rainbow text, glows and neon.

## 2. Brand

**Logo** (he expects it to be reused, never redrawn)
- A square in parking-sign blue **#1F4E9E** with a thin white inner border and "EV" in bold white, like a Danish parking sign.
- Wordmark "**EV** Scope", with EV in bold blue.
- Inventing a different logo is a hard fail ("not my logo, wtff??").

**Colour**
- Parking-sign blue #1F4E9E as the brand accent.
- Light, clean surfaces: white and light grey (#F5F6F8 sheet).
- Grey may be used as a **subtle accent**, but:
  - not full grey tiles;
  - not a whole page that is dull grey ("the full page is this dull grey its ugly").
- **No yellow** on the landing page, per his latest instruction (see Conflicts).
- Red and green only where they mean something.
- The colour scheme must look **cohesive**. Earlier he called a mix "trash, doesn't look cohesive at all".

**Type**
- IBM Plex Sans for text, IBM Plex Mono for numbers.
- Normal weights by default, with a clear hierarchy: headline, body, a few quiet notes.

**Neumorphism**
- It is part of his brand theme, but only when **subtle and tasteful**, with personality, where it means something.
- Fails:
  - heavy neumorphism ("overdoing the neomorphism soo much");
  - "used just for the sake of it";
  - "random buttons jammed where not needed";
  - "slapped abruptly";
  - "no personality".
- From the tool brief, where it does belong: recessed fields, raised buttons that press in.

## 3. Hero

**He likes**
- The **EV glyph / letter grid** with unit symbols (kW, kWh, °C, €, CO₂ …) and a label that moves between highlighted cells. "Soo cool."

**He hates**
- The grid made **bold or loud**. "So bold … makes you hate the brand."
- The grid made into a big readable mural. "Who asked you to draw a mural saying EV."
- **Removing** the grid. "I told you to make it subtle and you removed it."

**What that means**
- The grid stays, but as a faint, textural, living backdrop.
- The letters are not a statement, and the motion is barely noticeable.
- A bold or loud hero of any kind is a fail.

## 4. Motion

- Motion must be **smooth** and actually move as intended. "Dead animations" meant animations not moving as they were supposed to: janky, jumping or wrong, not frozen.
- The page should feel **dynamic**. "Nothing dynamic" was a v9 complaint, so static sections fail.
- Scroll-linked scenes and subtle ambient motion (as on Patensify) are wanted.
- Every effect is **subtle and smooth**, never "in your face".
- The earlier brief said motion should only respond to the visitor and nothing should loop forever. He later contradicted this (see Conflicts).
- Motion should explain something, never just decorate.

## 5. Layout

- **No card system.** "Cards feel sooo forced", "back to dogshit card system". This covers:
  - cards inside cards;
  - grids of white boxes;
  - audience sections shown as cards.
- **No pages that go on and on.** No scrolling until eternity.
- **Audiences must not be stacked** so that grid operators have to scroll past everyone else.
- **Audiences must not be hidden in tabs** where only one shows at a time (older brief).
- What he wants for the audiences: a **creative, visual way** of showing the four of them, "not each getting long texts".
- **Shadows** must look good. "Awful shadows" was a complaint about the blurry floor blobs under vehicles.
- **Vehicles all face the same direction.** "One truck is looking the other way" was a complaint.
- Nothing may overlap, cut off or scroll sideways at 1440 px, laptop or phone.

## 6. The four audiences

The audiences are:
- fleet owners;
- truck makers (OEMs);
- municipalities;
- charge operators and grid companies (DSOs).

For each one:
- **Sell, don't explain.** "The clients are not tech people so sell well not tell them the science behind it, sell features, sell what each client wants to hear."
- Each shows the decision they face, what EV Scope gives them, and which document they walk away with.
- Strong material from the project research:
  - grid lead times (Radius: 12–18 months with free capacity, 2–4 years without);
  - Radius's own pre-work list;
  - tenders scoring battery, delivery and 8–10-year service;
  - the Vejdirektoratet grant form fields;
  - FNA vs BNA;
  - year-8 battery guarantees.
- Weak slogans fail. "Sized for the hardest day" was rejected as a headline.

## 7. Documents

**He liked**
- The **fan / spread of document sheets** ("the document spread is great").
- The fan with a **small permanent description under each document**.

**He hated**
- A fan spread across the whole page ("spread to the fucking moon", "so overwhelming").
- The message that "you get dumped with 6 documents".
- A list picker that **can't be scrolled through decently** (v9).

**What it should say:** you get **whatever document you need** from one run.

**The six documents**
1. Feasibility report
2. Grid connection application
3. Tender annex
4. Financial model
5. Grant application data
6. Client presentation

## 8. Copy and claims

- Plain English, short sentences, confident. Lead with the answer.
- **Positioning:** EV Scope is a planning and sizing tool, **not a CPO**. It never "moves charging" or operates anything. "EV Scope moves charging to the night???" was flagged as wrong.
- Vague benefit lines fail ("a smaller connection lower peak charges???").
- **No invented** numbers, features, customers, testimonials, logos or prices. Illustrative data must be labelled as a sample case.
- Badges (Fleet Ready, etc.) only once their rules are decided.
- Overclaiming words ("bulletproof", "guaranteed", "legally require") must be checked before use.

## 9. Images

- **Wanted:** premium cutouts (trucks, vans, a charging post) with no background, used under the animations, product-style on a clean canvas.
- **Supplied** (in the artifact's asset store): van, refuse truck, charger, tractor-trailer, small, medium and large box trucks, and an OSM map of Nørrebro.
- The tractor-trailer and the medium box truck face left, so mirror them to match the others.
- The US reefer cutout failed and was dropped.
- Images are low-resolution and probably stock previews: check the licences before launch.
- A photo of a diesel truck on a page selling electric trucks needs replacing eventually (raised in an earlier chat).

## 10. Process

- **Render and check before sending.** "Critique it yourself", "think again what I would shit on and fix it before you dare show it to me".
- Read past chats and project docs **before** building. Don't ask for things he has already given (the logo).
- Don't drop a liked element while fixing a disliked one. Fix the problem with it, keep the element.
- One step at a time, flag every assumption, and invent no data.

## 10b. Feedback on the standalone file (29 Oct, evening): "much much better"

**Keep**
- The overall direction of `ev-scope-landing.html`.
- The faint glyph field. "Good, subtle."

**Change**
- **Hero truck:** use a different image, and **don't make it move**. The drive-in and parallax "look gimmicky".
- **Glyphs:** should **respond to the cursor**, turning more brand blue as the cursor gets closer.
- **Grid-connection chart:** "a very weak selling point". Replace it with something stronger and more creative.
- **Content inspiration from elento.dk** (content only, not its style). What it does:
  - questions framed from the client's side;
  - "three types of customers, one approach";
  - "advice before the decision";
  - a free first assessment.
- **Document fan:**
  - the overlap should go **the other way around**;
  - it should react to **cursor hover** and to **scrolling**.
- **One navigation pattern:** clients and documents had different next/prev controls ("that's bad"). It must be **uniform** across the page.
- **Cutouts and shadows:** redo them. The previous ones "suck".

## 10c. Gemini-image version (29 Oct, night): "this is sooo good its perfect wow"

**Keep**
- The overall build and the hero.
- The depot zoom story.
- The payload fill.
- The single switcher.
- Images used exactly as generated: white backgrounds, own shadows, no cutting.

**Fine-tune**
1. **Glyphs:**
   - must not sit behind the headline or subtitle;
   - the cursor effect stays;
   - remove the popup tags ("Grant ready" etc.).
2. **Battery:** start from a normal truck, not the depot. As you scroll fully into the chapter, it turns into the same truck showing its battery.
3. **Winter:** the refuse truck must be the same truck throughout, and only gets frosted once you have scrolled fully in.
4. **Charging:**
   - zoom into the screen only;
   - use generated screen images (three examples) instead of HTML overlays, which looked "wonky".
5. **Payload:**
   - the image's left shadow was cut, which looks blocky;
   - let the image show fully and overlay the text instead.
6. **Grid:**
   - no circular cutout of the substation image;
   - the lead-time panel must not cover the image.
7. **Audiences:** new copy to come from Bob.
8. **Documents:** the sheets must not cover the description text underneath.
9. **Closing:** show every vehicle type (car, van, trucks, refuse, mixer, trailer…) to say "we cover all of them".
10. **Switchers:** sit in the same position (all above or all below their content) in every section.
11. **Dark mode as "night":**
    - dark or graphite vehicles;
    - the depot at night with lights on;
    - an inverted charger screen.
    - It should feel like night, not just dark colours.

## 11. Conflicts between rounds (latest wins)

| Topic | Earlier | Latest |
|---|---|---|
| Yellow | Road-sign yellow plus grey as accents (and yellow made bold in the tool) | No yellow on the landing page; grey as a subtle accent only |
| Looping motion | Brief: nothing loops on its own | Wants Patensify-style elements that keep moving subtly after scrolling stops |
| Audiences | Brief: all visible at once, not in tabs | Not cards and not a long stack either; creative and visual |
| EV grid | Too bold (v6) | Removed (v8) was wrong; mural-like (v9) was wrong: keep it, very faint |

## 12. Version history in this chat

| Version | Verdict |
|---|---|
| v1 | Long, text-heavy "novel" |
| v2 | SVG scene art; documents looked bad |
| v3–v4 | Better; liked the Patensify-inspired parts; needed selling copy and all audiences shown creatively; neumorphism too heavy |
| v5 | Duplicate nav, faint text, broken layouts (found when he told me to critique it myself) |
| v6 | Animations not moving properly, bold EV hero, long audience text, incoherent colours, forced cards, neumorphism without personality |
| v7 | Invented logo; one truck facing the wrong way; grid audience behind the others; bad shadows; CPO-style copy; grid removed; dull grey page; random neumorphism; document fan too wide |
| v8 | Cards again, EV grid as a loud mural, documents not scrollable, audiences as cards, nothing dynamic, no product-style images |
