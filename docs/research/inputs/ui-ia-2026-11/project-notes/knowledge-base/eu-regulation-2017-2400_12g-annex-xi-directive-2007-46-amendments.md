
# Annex XI — Amendments to Directive 2007/46/EC

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex XI, in full (lines ≈24696–24743, the end of the document).
**Amendment provenance:** **►M4** (Commission Regulation (EU) 2025/258) — this entire Annex was inserted by the same amending act that added the FCS/hydrogen fuel-cell methodology (Annex Xb point 7). It is a short, purely legal-mechanics annex that wires the new CO2/VECTO certification regime into the EU's general vehicle type-approval framework (Directive 2007/46/EC, now largely superseded in substance by Regulation (EU) 2018/858 but still amended here as the formal vehicle), and makes rolling-resistance determination an explicit homologation checkpoint.

---

## Content (verbatim structure, 5 numbered amendments)

**(1) Annex I** — new point inserted:
> "3.5.7 CO2 emissions and fuel consumption certification (for heavy-duty vehicles, as specified in Article 6 of Commission Regulation (EU) 2017/2400)
> 3.5.7.1 Simulation tool license number:"

**(2) Annex III, Part I, Section A** (vehicle categories M and N) — identical new points inserted:
> "3.5.7 CO2 emissions and fuel consumption certification (for heavy-duty vehicles, as specified in Article 6 of Commission Regulation (EU) 2017/2400)
> 3.5.7.1 Simulation tool licence number:"

*(Practical meaning: every HDV type-approval information document (Annex I general vehicle description, and Annex III per-category description) must now carry the vehicle's **VECTO simulation tool licence number** as a formal data field — this is the administrative link between a vehicle's type-approval paperwork and its VECTO simulation run.)*

**(3) Annex IV, Part I** — two row changes to the "requirements for EC type-approval" matrix:
- (a) Row **41A** replaced: *"Emissions (Euro VI) heavy duty vehicles/access to information — Regulation (EC) No 595/2009, Regulation (EU) No 582/2011 — X(9) X(9) X X(9) X(9) X"* (applicability flags across vehicle categories, footnote 9 referenced).
- (b) New row **41B** inserted: *"CO2 simulation tool licence (heavy-duty vehicles) — Regulation (EC) 595/2009, Regulation (EU) 2017/2400 — X(16) X"*.
- (c) New explanatory footnote **(16)** added: *"For vehicles with a technically permissible maximum laden mass from 7 500 kg"*.

*(This is the formal scope-threshold statement: the CO2-simulation-tool-licence type-approval requirement applies to vehicles with technically permissible maximum laden mass ≥ 7 500 kg — i.e. it demarcates which vehicles fall under the HDV CO2/VECTO regime for type-approval purposes via this cross-reference, consistent with the Regulation's general HDV scope.)*

**(4) Annex IX** — new point inserted in two places:
- (a) Part I, Model B, Side 2, **Vehicle category N2**: new point **"49. Cryptographic hash of the manufacturer's record file"**.
- (b) Part I, Model B, Side 2, **Vehicle category N3**: identical new point 49.

*(This formally embeds the VECTO "record file" cryptographic hash — i.e. the tamper-evidence hash of a vehicle's simulation run output — into the EU's standard Certificate of Conformity (CoC) template, for N2 and N3 trucks. This is a key auditability mechanism directly relevant to the project's "auditable" positioning: the EU CoC itself is designed to carry a hash binding the vehicle's paperwork to its specific VECTO simulation record.)*

**(5) Annex XV, point 2** — new row inserted:
> "46B Rolling resistance determination — Regulation (EU) 2017/2400, Annex X"

*(Adds rolling-resistance determination, per this Regulation's Annex X — the tyre/rolling-resistance component-certification annex, outside the assigned electric-powertrain range of this extraction — as a named, cross-referenced type-approval checkpoint within Directive 2007/46/EC's own Annex XV listing of special purpose/national requirements mapping.)*

---

## Significance for this project

Annex XI contains **no electric-powertrain or sizing methodology** of its own — it is purely the legal "wiring" that:
1. makes the **VECTO simulation tool licence number** a mandatory field on HDV type-approval paperwork (Annex I / Annex III);
2. formally scopes the CO2-simulation-tool-licence requirement to vehicles **≥ 7 500 kg** technically permissible maximum laden mass (Annex IV footnote 16);
3. embeds a **cryptographic hash of the manufacturer's VECTO record file** into the Certificate of Conformity for N2/N3 trucks (Annex IX) — the specific mechanism by which a real vehicle's paperwork is bound to its underlying simulation run, relevant to any "PVsyst for EVs" auditability design (e.g. a tool could expose/verify this hash as part of its own audit trail concept);
4. cross-links rolling-resistance determination (Annex X) into the general type-approval Annex XV mapping.

No further action needed for the battery/e-motor/FCS sizing methodology beyond noting point 3 above as a precedent for hash-based auditability that the project may wish to emulate.
