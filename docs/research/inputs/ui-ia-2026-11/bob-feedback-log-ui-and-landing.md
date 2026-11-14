# Bob's feedback on the EV Scope tool UI and landing page (log, 26 Oct to 14 Nov 2026)

Compiled by Claude on 14 Nov 2026 from Bob's own messages in chat and from his saved preferences. Quotes are Bob's words. Where his view changed, the latest instruction wins. Older detail on the landing page is in `project-notes/claude_landing-likes-dislikes-2026-10-29.md` (26–29 Oct rounds) and `project-notes/claude_landing-page-brief-2026-10-28.md`.

## A. Tool UI: standing rules

1. **Look.** A serious, trusted industry tool, like what consultancies or banks put out. Professional, modern, simple yet technical. Not "websitey", not a gimmick, not dated Windows-XP style, not "AI-website" looking.
2. **Layout.** Classic SaaS layout: input pages by category, separate output pages, a Run button. Horizontal top menu with icons. Collapsible assistant. Subtle red/green only where it means something. Charts only where they help; not everything a chart, not all bar charts, no sparklines.
3. **Brand.** Parking-sign blue #1F4E9E, light surfaces (#F5F6F8 sheet), IBM Plex Sans. Subtle neumorphism on controls only (recessed fields, raised buttons). No yellow. Logo never redrawn.
4. **The UI is a dumb form.** All logic, defaults and calculations live in Python. The UI posts raw JSON.

## B. Tool UI: inputs (13–14 Nov feedback, in his words where possible)

1. Original problem (13 Nov): "there are too many input fields and some are just confusing how there is operations and then there is route separate it's confusing, and in each of those input fields it's not clear what the inputs are and they are presented all at once and it's very messy looks as if you are meant to enter them all at once even when there are multiple types of inputs, there is no clever use of pop up for advanced inputs to simplify the input phase tastefully, the inputs section also shows already some outputs which is very confusing and not intuitive."
2. "be careful of over correcting the problem and stuffing things into just one tab or everything in just one pop up, the goal is for it to be intuitive not go from overwhelming to empty overwhelming and confusing because everything is brushed under the rug, same with inputs and outputs."
3. **No source or assumption text beside each field.** "i dont like showing the sources or assumptions next to each field the user dsnt care much about it ... its things that go in the report, putting it on every field looks crowded and ugly." At most a subtle asterisk or a colour.
4. **No separate "Assumptions" page.** "its almost as if assumptions is a different category, no assumptions exist in all pages and thats fine we mention it in the report."
5. **Predictable pages.** "when i want to set in the weather or prices its very very very non intuitive that i have to go to the assumptions page ... The number of input pages and output pages dsnt matter as much as it being intuitive so i know what page to go to when i need to enter the weather details or the price details etc, but also having 20 pages is also not right and have 3 is also not right, the balance is what makes it intuitive, i should know what to expect from the pages before i go into them."
6. **All inputs must be there.** After a version that dropped many fields: "Half the inputs are missing???? ... This is not what we talked about." Every input in `hdev-ui-input-inventory-2026-11-13.md` and every input of the functions still to come must have a home in the UI.
7. **Popups for detailed inputs.** "Where the fuck are the pop ups?" Advanced and detailed inputs go in named popups (title = what the popup holds, e.g. "Tyres", not "Advanced settings"; the faded subtitle says where it belongs). Earlier (Oct): popup titles must name the content, not say "Advanced settings".
8. **The fleet table.** "Where is the table we discussed about????" The fleet is one table: one row per group of identical vehicles, a count, and a template dropdown per column (vehicle, route, payload, PTO, schedule), plus bulk apply to many rows. Designed 31 Oct to 13 Nov (see `project-notes/claude_status-engine.md` and the chat summary in section E).
9. **No separate Templates page.** "So now you a whole page for fucking templates????? wtf???" Templates are reached from the fleet table, not from their own page.
10. **Things belong where they physically belong.** "Cab heating and stuff are related to what the vehicle or the fucking weather? Can you not reason well?" Cab heating and cooling sits with Weather (it is driven by temperature), not inside the vehicle. Kiro should apply the same reasoning to every input: ask "what does this value depend on, and where would a user look for it?"
11. **Inputs must not show outputs.** Results belong on result pages.
12. **The year-8 battery check must never be dropped.** Bob, 14 Nov: "including the 8 year thing which you have just forgotten." Tenders state a guaranteed usable capacity at year 8, and the tool must size and check against it (inputs and results).
13. **Older UI rules still standing (Oct):** label, value and unit on one line; edited value turns blue with a reset; missing required field red and blocks Run; an engineering view can show physics names (Crr, CdxA) that the client view hides; OEM-only fields greyed for clients.

## C. Tool UI: results

1. Original problem (13 Nov): "The outputs also need work where some pages are just empty and some show things which are redundant."
2. "A lot of the outputs and results look merged because of poor visual hierarchy and bad alignment, it just looks like a sentence not results with million krona value."
3. Earlier (Oct): the Overview should also carry input context (distance, payload variation etc.) as visual summaries, because inputs are entered in fragments; one card or block per area (operations, consumption, charging, grid, cost, CO₂); feasibility checks are fine but must not eat the Overview; bars that only repeat the number beside them add nothing; long tables need hierarchy; charts were too high level (no component split, no monthly balance, no confidence band).
4. The documents page: the six document types are a core feature (feasibility report, grid connection application, tender annex, financial model, grant application data, client presentation). Users pick what they need.

## D. Landing page (13–14 Nov feedback)

1. **Likes:** the day/night effect and the images; the payload that changes; the chargers that change; the types of reports.
2. **Dislikes:** "the cursor following tiles are clunky and not professional" (removed since).
3. "it needs to be clear what its selling."
4. **Demo preview:** "smooth but not overwhelming where we show every tab but we show enough with smooth cursor to guide the eye."
5. **Personalisation:** "it should also make it very easy and clear for users of different types municipalities, housing associations, fleet owners, OEM/CPOs, etc. As one of them when i open the landing page i should not have to scroll ages to go to what i want, i want to go to the part that concerns me and that's what sells, not an ad about the tool but personalization."
6. **Framing:** "instead of talking about payload variation in the payload scroll part we can tell in one sentence the effect it has which is the hook and then the seller that the tool analyses payload ... it must be from their pov not how great the tool is but what it does for them."
7. **Hierarchy:** "it needs much better visual hierarchy, now its all to the point i dont even know how to read." "in the who it is for the main title still stays as top hierarchy while I am cycling thru municipalities etc and nothing besides the button tells me if its the municipalities or what."
8. "its silly in the end where it says you get this document instead of letting them pick."
9. "use some examples and clear the mess and make it intuitive, with good visual flow and hierarchy." "more customer facing without everything being a marketing jingle, it needs to be personal to them than a boast for us."
10. **14 Nov, after the next version:** "The landing page still has marketing jargon like measure you payload before you buy after selling your house? ... it's soo much sell sell sell." "The documents part is broken and not smooth." "The start of the page has a paragraph, the next thing is listing customers like a fucking grid block scroll a bit down and they are listed again. That shit is Wack." "You still have the documents you can take away thing sooo stupid."
11. **Positioning:** EV Scope is a planning and sizing tool, not a charge point operator. It never "moves charging" or operates anything.
12. **Claims:** no invented numbers, customers, testimonials, logos or prices. Sample figures are labelled as a sample case.

## E. The fleet table and templates as designed earlier (13 Nov chat, "Consumption engine and flowchart")

- Five small libraries: vehicle types, routes, payload profiles, PTO profiles, schedules (departure and return times, operating days).
- "Save as template" copies what the user just entered into the matching library under a name. VECTO templates are the same thing, pre-filled and locked.
- The fleet is one table. Each row picks one item from each library, plus optional overrides. "Same route, different payload" is two rows that differ in one cell.
- Count column ("× 20"); the parser expands it before the run. Bulk apply: select rows, set route/payload/schedule once.
- Rows that share route, vehicle class and PTO share one driver run (rerun table: route or class → driver + force; PTO → driver; payload, weather, date → consumption only; times → charging only).
- Open: link or copy when a template is edited (Claude suggested link plus an explicit "make a copy"; not decided). Templates live inside the project JSON for now; a user-level library across projects later.
- Weak spots Claude noted then: a new user must build templates before filling the table; the table is wide.

## F. Process rules for whoever builds or reviews this

- Read past material before building; don't ask Bob for things he already gave.
- Render and critique your own output before showing it. Don't drop a liked element while fixing a disliked one.
- Explain why each proposed change is made (does it remove an assumption, open more input types, estimate better?), so Bob can decide.
- Plain English, short sentences. Flag every assumption. No invented numbers.
