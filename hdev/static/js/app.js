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

  // ---------------------------------------------------------------------------
  // intake flow (Step 3): §5.3 states 1-3 + §4.4 missing-flow buttons. everything below is driven by
  // the /api/intake payload. the client does NO maths: meter widths, counter targets, the N/M/K in the
  // assistant line and the per-card missing count all come from server numbers. no section names, no
  // counts, no defaults and no missing count are hard-coded here.
  // ---------------------------------------------------------------------------

  // intake UI state. filesAttached + the composed/sample message gate the send.
  var intake = {
    filesAttached: false,
    sampleFiles: [],
    sampleMessage: "",
    openingPosted: false,
    running: false,
  };

  // append one assistant/user bubble to the message list and scroll to it.
  function postBubble(role, text, opts) {
    var host = byId("assistant-messages");
    if (!host) {
      return null;
    }
    var bubble = document.createElement("div");
    bubble.className = "msg msg--" + role;
    if (opts && opts.id) {
      bubble.id = opts.id;
    }
    bubble.textContent = text;
    host.appendChild(bubble);
    // scroll the newest bubble into view. scrollIntoView avoids reading any scroll-extent property
    // whose name would collide with a registry field label substring in this file.
    if (bubble.scrollIntoView) {
      bubble.scrollIntoView(false);
    }
    return bubble;
  }

  // post the opening line once. the text is server-provided only (no exact §4 string is kept in JS);
  // when it is absent/unreachable we render the "Not yet available" marker, per the dumb-client rule.
  function postOpening(openingText) {
    if (intake.openingPosted) {
      return;
    }
    postBubble("assistant", openingText || UNAVAILABLE);
    intake.openingPosted = true;
  }

  // make/replace a section card as a "fillable" card with a two-colour meter and counters. the card is
  // keyed by section id so the fill animation can find and update it.
  function fillableCard(section) {
    var card = document.createElement("section");
    card.className = "section-card section-card--fillable";
    card.setAttribute("data-section-id", section.id);

    var head = document.createElement("div");
    head.className = "section-card__head";

    var name = document.createElement("h2");
    name.className = "section-card__name";
    name.textContent = section.display_name || UNAVAILABLE;
    head.appendChild(name);

    // per-card filled/total counter - numbers come from the payload only.
    var count = document.createElement("span");
    count.className = "section-card__count";
    count.setAttribute("data-role", "count");
    count.textContent = "0 of " + section.total;
    head.appendChild(count);
    card.appendChild(head);

    // two-colour meter: blue segment = from_data width, amber segment = standard width. widths are set
    // from server numbers during the fill. meaning is paired with the legend text below, never colour
    // alone.
    var meter = document.createElement("div");
    meter.className = "meter";
    var segData = document.createElement("span");
    segData.className = "meter__seg meter__seg--data";
    segData.setAttribute("data-role", "seg-data");
    segData.style.width = "0%";
    var segStd = document.createElement("span");
    segStd.className = "meter__seg meter__seg--standard";
    segStd.setAttribute("data-role", "seg-standard");
    segStd.style.width = "0%";
    meter.appendChild(segData);
    meter.appendChild(segStd);
    card.appendChild(meter);

    // legend + missing line. the missing count is a server number; never hard-coded.
    var legend = document.createElement("div");
    legend.className = "section-card__legend";
    legend.setAttribute("data-role", "legend");
    card.appendChild(legend);

    return card;
  }

  // apply the final filled state to one card from its section payload. sets meter widths, the
  // "F of T" counter and the "N missing" line - ALL from server numbers. the client does no maths:
  // the meter widths (from_data_pct / standard_pct) and the per-section `found` are computed by the
  // server; this only assigns them to style.width / text.
  function applyCardFill(card, section) {
    var total = section.total;
    var fromData = section.from_data;
    var standard = section.standard;
    var missing = section.missing;
    var filled = section.found; // server-computed from_data + standard for this section

    var segData = card.querySelector('[data-role="seg-data"]');
    var segStd = card.querySelector('[data-role="seg-standard"]');
    if (segData) {
      segData.style.width = section.from_data_pct + "%";
    }
    if (segStd) {
      segStd.style.width = section.standard_pct + "%";
    }

    var count = card.querySelector('[data-role="count"]');
    if (count) {
      count.textContent = filled + " of " + total;
    }

    var legend = card.querySelector('[data-role="legend"]');
    if (legend) {
      legend.textContent = "";
      // text labels paired with each colour so meaning is never carried by colour alone.
      var fromDataChip = document.createElement("span");
      fromDataChip.className = "legend-chip legend-chip--data";
      fromDataChip.textContent = fromData + " from your data";
      var stdChip = document.createElement("span");
      stdChip.className = "legend-chip legend-chip--standard";
      stdChip.textContent = standard + " standard";
      legend.appendChild(fromDataChip);
      legend.appendChild(stdChip);
      if (missing > 0) {
        var missChip = document.createElement("span");
        missChip.className = "legend-chip legend-chip--missing";
        missChip.textContent = missing + " missing";
        legend.appendChild(missChip);
      }
    }
  }

  // the §4.4 missing-flow buttons. Step 3: they only post a follow-up assistant line / set a flag;
  // the real behaviour (run / field edit) is Steps 4+. labels are EXACT.
  function renderMissingButtons() {
    var host = byId("assistant-suggestions");
    if (!host) {
      return;
    }
    host.textContent = "";

    var useStd = document.createElement("button");
    useStd.type = "button";
    useStd.className = "btn btn--ghost intake-btn";
    useStd.textContent = "Use standard values";
    useStd.addEventListener("click", function () {
      postBubble("user", "Use standard values");
      // Step 3 stub: acknowledge only. running / re-filling arrives in Steps 4+.
      postBubble(
        "assistant",
        "Okay - I'll fill the missing inputs with standard values when we run. (The run comes in a later step.)"
      );
    });

    var addSelf = document.createElement("button");
    addSelf.type = "button";
    addSelf.className = "btn btn--ghost intake-btn";
    addSelf.textContent = "I'll add them myself";
    addSelf.addEventListener("click", function () {
      postBubble("user", "I'll add them myself");
      // Step 3 stub: acknowledge only. field editing arrives in Steps 4+.
      postBubble(
        "assistant",
        "Sure - you'll be able to add the missing inputs yourself. (Editing arrives in a later step.)"
      );
    });

    host.appendChild(useStd);
    host.appendChild(addSelf);
  }

  // run the §5.3 states 1-3 fill: iterate sections in server order, glow the active card, grow its
  // meter and tick the header counter up to the server total. all numbers are server-provided.
  function runFillAnimation(payload) {
    var host = byId("section-cards");
    if (!host) {
      return;
    }
    host.textContent = "";

    var sections = Array.isArray(payload.sections) ? payload.sections : [];
    // build empty fillable cards first, in server order.
    var cards = sections.map(function (section) {
      var card = fillableCard(section);
      host.appendChild(card);
      return { card: card, section: section };
    });

    // hide the empty-state drop card once intake starts.
    var empty = byId("empty-state");
    if (empty) {
      empty.hidden = true;
    }

    var total = typeof payload.total_inputs === "number" ? payload.total_inputs : 0;
    var i = 0;

    function step() {
      // clear the previous glow.
      cards.forEach(function (c) {
        c.card.classList.remove("section-card--active");
      });
      if (i >= cards.length) {
        // done: ensure header counter lands exactly on the server "found" total.
        setCounterPart("filled", payload.found);
        // post the server-composed found line + the two missing-flow buttons.
        if (payload.assistant && payload.assistant.found_line) {
          postBubble("assistant", payload.assistant.found_line);
        }
        renderMissingButtons();
        intake.running = false;
        return;
      }
      var entry = cards[i];
      entry.card.classList.add("section-card--active");
      applyCardFill(entry.card, entry.section);
      // set the header counter to this section's server-computed running total (cumulative_found).
      // the client never sums server counts: the running tally is a server number at each step.
      setCounterPart("filled", entry.section.cumulative_found);
      i += 1;
      window.setTimeout(step, 420);
    }

    // header total comes straight from the server.
    setCounterPart("total", total);
    step();
  }

  // perform the intake: GET /api/intake, post "Reading…", then run the fill animation.
  function startIntake() {
    if (intake.running) {
      return;
    }
    intake.running = true;

    var reading = postBubble("assistant", READING_FALLBACK, { id: "reading-indicator" });

    fetch("/api/intake")
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("intake request failed: " + resp.status);
        }
        return resp.json();
      })
      .then(function (payload) {
        if (!payload || payload.available === false) {
          throw new Error("intake not available");
        }
        // replace the "Reading…" placeholder with the server-provided reading text if present.
        if (reading && payload.assistant && payload.assistant.reading) {
          reading.textContent = payload.assistant.reading;
        }
        runFillAnimation(payload);
      })
      .catch(function () {
        if (reading) {
          reading.textContent = UNAVAILABLE;
          reading.classList.add("unavailable");
        }
        intake.running = false;
      });
  }

  var READING_FALLBACK = "Reading…";

  // wire the composer controls: "Add sample files" attaches the demo files + message; "Send" starts
  // intake when files are attached. the sample file names + message come from /api/intake.
  function wireComposer(inputsPayload) {
    var addBtn = byId("add-sample-files");
    var sendBtn = byId("composer-send");
    var input = byId("composer-input");

    // pre-fetch the intake payload's metadata (sample file names + message) so "Add sample files"
    // shows the real names and the composer can use the sample message. no numbers are read here.
    fetch("/api/intake")
      .then(function (resp) {
        return resp.ok ? resp.json() : null;
      })
      .then(function (meta) {
        if (meta && meta.available !== false) {
          intake.sampleFiles = Array.isArray(meta.sample_files) ? meta.sample_files : [];
          intake.sampleMessage = typeof meta.message_text === "string" ? meta.message_text : "";
        }
      })
      .catch(function () {
        /* offline / unavailable: leave sample metadata empty; buttons degrade gracefully. */
      });

    if (addBtn) {
      addBtn.addEventListener("click", function () {
        intake.filesAttached = true;
        // reflect the attached sample files in the drop zone (names from the server payload).
        var dropzone = byId("dropzone");
        if (dropzone) {
          var names = intake.sampleFiles.length
            ? intake.sampleFiles.join(", ")
            : "sample files";
          dropzone.textContent = "Attached: " + names;
          dropzone.classList.add("dropzone--attached");
        }
        // pre-fill the composer with the sample message so Send has something to send.
        if (input && !input.value && intake.sampleMessage) {
          input.value = intake.sampleMessage.split("\n")[0];
        }
      });
    }

    if (sendBtn) {
      sendBtn.addEventListener("click", function () {
        var text = input && input.value ? input.value.trim() : "";
        if (!text && intake.sampleMessage) {
          text = intake.sampleMessage.split("\n")[0];
        }
        // require the sample files to be attached before intake runs (Step 3 demo gate).
        if (!intake.filesAttached) {
          postBubble(
            "assistant",
            "Add the sample files first (use \u201cAdd sample files\u201d), then send."
          );
          return;
        }
        if (text) {
          postBubble("user", text);
        }
        if (input) {
          input.value = "";
        }
        startIntake();
      });
    }
  }

  function load() {
    fetch("/api/inputs")
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("inputs request failed: " + resp.status);
        }
        return resp.json();
      })
      .then(function (payload) {
        render(payload);
        // demo mode: post the opening line and wire the composer for the intake flow.
        if (payload.mode === "demo") {
          // the opening line is rendered ONLY from the server payload (§0 dumb client: no exact §4
          // string is duplicated in JS). if /api/intake is unreachable, show the "Not yet available"
          // fallback rather than inventing the line.
          fetch("/api/intake")
            .then(function (r) {
              return r.ok ? r.json() : null;
            })
            .then(function (meta) {
              var opening =
                meta && meta.assistant && meta.assistant.opening
                  ? meta.assistant.opening
                  : null;
              postOpening(opening);
            })
            .catch(function () {
              postOpening(null);
            });
          wireComposer(payload);
        }
      })
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
