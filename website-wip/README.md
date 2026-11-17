# EV Scope website and demo tool: work in progress

Temporary branch so the work can be picked up again if a session is interrupted.

- `out/ev-scope-site.html`: the combined site with the demo tool embedded (the deliverable).
- `out/ev-scope-tool.html`: the demo tool on its own.
- `src/`: the tool's source (shell, CSS, model, UI, results, app).
- `site_parts.py`, `build_site.py`, `build_tool.py`: build scripts. They expect the working folder layout of the session
  (`/home/claude/work`) and the IBM Plex packages from npm (`@ibm/plex-sans`, `@ibm/plex-mono`) unpacked under `/home/claude/fonts`.
- `assets/original-site.html`: the landing page as uploaded, the source of the images.
- `assets/site_stripped.html`: the same page with images and the old tool replaced by placeholders.
