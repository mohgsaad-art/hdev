# STATUS: NEW (PR 7, Bob to review). public API of the audit/ package (Step 7).
#
# audit/ owns the §8-SAFE shaping of the two audit-trail artefacts:
#   - sources.py   : the "Where every input came from" table - SOURCE TYPES + COUNTS ONLY (never a
#                    field id/label), derived from the demo intake tallies.
#   - run_log.py   : the §3.4 run-log entry builder (client-facing names, plain words, engine_version
#                    'demo') plus thin append/list helpers that delegate PERSISTENCE to
#                    hdev.project_store.
#
# §0: all logic lives in Python; the browser is a dumb client. nothing here touches the network or an
# AI provider.
from .sources import source_type_tallies, rows_contain_no_field_names
from .run_log import (
    build_run_entry,
    settings_summary,
    key_result_summary,
    changed_from_previous,
    append_entry,
    list_entries,
    latest_entry,
    ENGINE_VERSION_DEMO,
)

__all__ = [
    "source_type_tallies",
    "rows_contain_no_field_names",
    "build_run_entry",
    "settings_summary",
    "key_result_summary",
    "changed_from_previous",
    "append_entry",
    "list_entries",
    "latest_entry",
    "ENGINE_VERSION_DEMO",
]
