// STATUS: NEW (PR 2, Bob to review). the dumb-client renderer for the Step 2 UI shell.
//
// §0: this file does NO maths and holds NO section names, counts, defaults or calculation logic. it
// fetches /api/inputs once and renders exactly what the server sent: the header input counter (both
// numbers come from the payload), one card per section (display_name + count + subgroup names from
// the payload), the demo pill (only when mode == "demo") and the empty drop-card state. on any fetch
// failure or missing value it renders "Not yet available" rather than inventing data.

(function () {
  "use strict";

  var UNAVAILABLE = "Not yet available";

  function byId(id) {
    return document.getElementById(id);
  }

  // set a [data-counter] span's text, falling back to the unavailable marker when absent.
  function setCounterPart(name, value) {
    var el = document.querySelector('[data-counter="' + name + '"]');
    if (!el) {
      return;
    }
    if (value === null || value === undefined) {
      el.textContent = UNAVAILABLE;
      el.classList.add("unavailable");
    } else {
      el.textContent = String(value);
      el.classList.remove("unavailable");
    }
  }

  // header counter: both numbers come from the server payload only. nothing is hard-coded and the
  // client invents nothing. "filled" is whatever the server reports (filled_inputs, 0 in the shell
  // since nothing is filled yet); "total" is the registry-derived total_inputs. a missing value
  // renders the unavailable marker rather than a client-side default.
  function renderCounter(payload) {
    var total = typeof payload.total_inputs === "number" ? payload.total_inputs : null;
    var filled =
      typeof payload.filled_inputs === "number" ? payload.filled_inputs : null;
    setCounterPart("filled", filled);
    setCounterPart("total", total);
  }

  // demo pill: shown only when the server says mode == "demo".
  function renderDemoPill(payload) {
    var pill = byId("demo-pill");
    if (!pill) {
      return;
    }
    pill.setAttribute("data-visible", payload.mode === "demo" ? "true" : "false");
  }

  // one card per section, built entirely from the payload: display_name, per-section count and the
  // subgroup names the server provided. no names/counts are hard-coded here.
  function renderSections(payload) {
    var host = byId("section-cards");
    if (!host) {
      return;
    }
    host.textContent = "";

    var sections = Array.isArray(payload.sections) ? payload.sections : [];
    if (!sections.length) {
      var note = document.createElement("p");
      note.className = "unavailable";
      note.textContent = UNAVAILABLE;
      host.appendChild(note);
      return;
    }

    sections.forEach(function (section) {
      var card = document.createElement("section");
      card.className = "section-card";

      var head = document.createElement("div");
      head.className = "section-card__head";

      var name = document.createElement("h2");
      name.className = "section-card__name";
      name.textContent = section.display_name || UNAVAILABLE;
      head.appendChild(name);

      var count = document.createElement("span");
      count.className = "section-card__count";
      // display formatting only: the number itself comes straight from the server.
      if (typeof section.count === "number") {
        count.textContent =
          section.count === 1 ? "1 input" : section.count + " inputs";
      } else {
        count.textContent = UNAVAILABLE;
        count.classList.add("unavailable");
      }
      head.appendChild(count);
      card.appendChild(head);

      var subgroups = Array.isArray(section.subgroups) ? section.subgroups : [];
      if (subgroups.length) {
        var list = document.createElement("ul");
        list.className = "section-card__subgroups";
        subgroups.forEach(function (group) {
          var chip = document.createElement("li");
          chip.className = "subgroup-chip";
          chip.textContent = group && group.name ? group.name : UNAVAILABLE;
          list.appendChild(chip);
        });
        card.appendChild(list);
      }

      host.appendChild(card);
    });
  }

  // the empty workspace drop-card state is in the static HTML already; keep it visible in the shell.
  function renderEmptyState() {
    var empty = byId("empty-state");
    if (empty) {
      empty.hidden = false;
    }
  }

  // render the unavailable fallback across the shell when the fetch fails. no invented data.
  function renderUnavailable() {
    setCounterPart("filled", null);
    setCounterPart("total", null);
    var host = byId("section-cards");
    if (host) {
      host.textContent = "";
      var note = document.createElement("p");
      note.className = "unavailable";
      note.textContent = UNAVAILABLE;
      host.appendChild(note);
    }
    renderEmptyState();
  }

  function render(payload) {
    renderCounter(payload);
    renderDemoPill(payload);
    renderSections(payload);
    renderEmptyState();
  }

  function load() {
    fetch("/api/inputs")
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("inputs request failed: " + resp.status);
        }
        return resp.json();
      })
      .then(render)
      .catch(function () {
        renderUnavailable();
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
