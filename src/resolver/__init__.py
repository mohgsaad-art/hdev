# STATUS: NEW (Step 9, items 1-3, Bob to review). Marks src/resolver/ as a package so the
# resolver front-end imports cleanly as src.resolver.<module>. The resolver turns the four route
# inputs (VDRI / typed / GPS / AI) into the one waypoint-list shape the driver model consumes,
# and holds the sourced defaults table (defaults.py). Pure modules only, no file I/O inside the
# engine-style functions (parsers take text, resolvers take structured arguments).
