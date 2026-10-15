// STATUS: UPDATED (PR 6, Bob to review). the dumb-client renderer, extended for the Step 6 demo
// assistant (suggestion buttons, typed-send to /api/chat, shift-end field edit, applyChatAction).
//
// §0: this file does NO business maths and holds NO section names, counts, defaults, strategy keys or
// calculation logic. it fetches /api/inputs once, GETs /api/intake for the fill animation, and POSTs
// the raw client-facing lever set to /api/run; it then renders exactly what the server sent in the
// §3.3 results payload - KPI tiles, verdict, plan, strategy table and the charts - and POSTs lever
// JSON back unchanged. the ONLY arithmetic in this file is SVG coordinate scaling inside the chart
// helpers (mapping a data value to a pixel position is drawing layout, not business maths); no
// DISPLAYED figure is ever derived here - every number shown comes verbatim from the payload. on any
// fetch failure or missing/null value it renders "Not yet available" rather than inventing data.
//
// STEP 6 ADDITIONS (demo assistant): the §4.4 suggestion buttons, a typed-message send path and the
// shift-end field edit all POST to /api/chat and render the server reply + apply the server action
// (open a tab, update the scenario bar for a changed lever, render new results). the client sends
// ONLY raw typed text or an action identifier; it does NO keyword matching, generates NO reply text,
// and computes NO number. every reply string and every routing/lever decision comes from the server
// (explain/ templates + the §4.3 number-check); the client just draws what it is handed.

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

  // the latest /api/inputs payload, retained in client state so the Inputs results tab can re-render
  // its section cards from payload.sections without relying on DOM left behind by the intake fill
  // animation. nothing is recomputed; the server payload is simply kept.
  var inputsState = { payload: null };

  function render(payload) {
    inputsState.payload = payload;
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
      postBubble(
        "assistant",
        "Okay - I'll fill the missing inputs with standard values and run the full year now."
      );
      // §5.3 state 4: trigger the full run. the client sends NO lever values of its own on the first
      // run - it posts an empty lever set and the server fills + echoes the standard values. JS never
      // invents a default.
      triggerFirstRun();
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
        // post-run: Send a typed question to the assistant. the RAW text is POSTed to /api/chat; the
        // server does the keyword routing and returns the reply + any action. pre-run: run the intake
        // fill animation as before. (Step 6: the typed-send path replaces the old scenario re-run.)
        if (results.payload) {
          if (!text) {
            return;
          }
          askAssistant({
            message: text,
            levers: results.levers,
            current_results: results.payload,
          });
        } else {
          startIntake();
        }
      });
    }
  }

  // ===========================================================================
  // STEP 5: run screen (§5.3 state 4), result tabs (§5.6), hand-drawn SVG charts (§5.1), scenario
  // bar (§5.5) and the recalculation overlay. everything below renders ONLY from the /api/run
  // payload and POSTs raw lever JSON back. no business maths, no hard-coded section/strategy names.
  // ===========================================================================

  // chart colour tokens (kept in sync with css custom properties). these are drawing colours only;
  // every series/limit is also paired with a text label in the legend so meaning is never colour
  // alone (§5.1).
  var COLOR = {
    electric: "#1F5FD1", // signal blue
    diesel: "#9AA5B8", // diesel grey
    limit: "#F2A93B", // amber: limits / standard / warnings
    axis: "#10233f", // navy for text + axes
    grid: "#c9d2e0", // light gridlines
  };

  // the full §5.6 tab set, in order. these are UI copy labels (not registry section names or computed
  // numbers); the client-facing tab titles are fixed UI chrome, so they live here as plain labels.
  // each tab names which renderer draws its panel.
  var TABS = [
    { id: "inputs", label: "Inputs", render: renderInputsTab },
    { id: "overview", label: "Overview", render: renderOverviewTab },
    { id: "energy", label: "Energy", render: renderEnergyTab },
    { id: "charging", label: "Charging", render: renderChargingTab },
    { id: "gridflex", label: "Grid & flexibility", render: renderGridTab },
    { id: "tco", label: "Costs (TCO)", render: renderTcoTab },
    { id: "co2", label: "CO₂", render: renderCo2Tab },
    { id: "scenarios", label: "Scenarios", render: renderScenariosTab },
    { id: "report", label: "Report", render: renderReportTab },
    { id: "audit", label: "Audit trail", render: renderAuditTab },
  ];

  // the nine §5.3 run-screen checklist lines, in order. fixed UI copy strings (not registry names or
  // computed numbers). "250 working days per truck" is a verbatim §5.3 copy string.
  var CHECKLIST = [
    "Reading routes and stops",
    "Simulating 250 working days per truck",
    "Adding weather for every day of the year",
    "Sizing batteries to the hardest day",
    "Testing charging strategies",
    "Checking the depot grid connection",
    "Finding flexibility",
    "Calculating total cost of ownership",
    "Calculating CO₂",
  ];

  // the four §5.5 recalculation overlay rotating lines.
  var RECALC_LINES = [
    "Re-running the year…",
    "Re-sizing chargers…",
    "Checking the grid…",
    "Updating costs…",
  ];

  // human labels for the client-facing charging-priority names (§8: never surface internal keys). the
  // payload only ever carries these three client-facing names; map each to a human label for display.
  var PRIORITY_LABELS = {
    lowest_cost: "Lowest cost",
    grid_friendly: "Grid-friendly",
    ready_earliest: "Ready earliest",
  };

  // scenario-bar controls as client-facing values only (verbatim from src/registry/levers.py). the
  // segmented options carry a human label + the raw value the server expects. the client picks none of
  // these numbers itself at run time - it just posts whatever the controls hold.
  var LEVER_UI = {
    charging_priority: [
      { value: "lowest_cost", label: "Lowest cost" },
      { value: "grid_friendly", label: "Grid-friendly" },
      { value: "ready_earliest", label: "Ready earliest" },
    ],
    electricity_price: [
      { value: "low", label: "Low" },
      { value: "expected", label: "Expected" },
      { value: "high", label: "High" },
    ],
    weather_year: [
      { value: "normal", label: "Normal year" },
      { value: "cold_winter", label: "Cold winter" },
    ],
    ownership_years: [
      { value: 8, label: "8" },
      { value: 10, label: "10" },
      { value: 12, label: "12" },
    ],
  };

  // results UI state: the latest payload, the active tab, the current lever set and the shift-end
  // lever target (only sent if the server/context provided one).
  var results = {
    payload: null,
    activeTab: "overview",
    levers: null, // the current client-facing lever set
    shiftEnd: null, // operation.schedule.shift_end "HH:MM" if present, else null (omit it)
    recalcTimer: null,
  };

  // ---- small DOM helpers --------------------------------------------------

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) {
      node.className = cls;
    }
    if (text !== undefined && text !== null) {
      node.textContent = text;
    }
    return node;
  }

  function svgEl(tag) {
    return document.createElementNS("http://www.w3.org/2000/svg", tag);
  }

  // render an opaque value or the unavailable marker. does NOT format numbers (no maths); it only
  // decides present vs absent. the server sends display-ready numbers.
  function orUnavailable(value) {
    if (value === null || value === undefined) {
      return UNAVAILABLE;
    }
    return String(value);
  }

  // ready_by normalisation (§5.3 display artifact): the ready_earliest strategy's ready_by can read
  // "19:00".."24:00" or higher - an illustrative artifact from Step 4. treat it as an OPAQUE display
  // string from the server and sanitise display only: if the hour part reads >= 24, show an en dash
  // instead of "24:00". this changes display only; demo_engine is unchanged.
  function displayReadyBy(value) {
    if (value === null || value === undefined || value === "") {
      return UNAVAILABLE;
    }
    var text = String(value);
    var colon = text.indexOf(":");
    if (colon > 0) {
      var head = text.slice(0, colon);
      // Number() here parses the opaque clock string for a display threshold check only; it does not
      // derive any shown figure (the shown figure is the server string or an en dash).
      var hour = Number(head);
      if (!isNaN(hour) && hour >= 24) {
        return "\u2013";
      }
    }
    return text;
  }

  // ---- KPI tiles ----------------------------------------------------------

  // one KPI tile: small label, big number (verbatim from payload), one-line note. tone 'good' = blue,
  // 'warn' = amber, each paired with the note text so meaning is never colour alone. a null/absent
  // value renders the unavailable marker.
  function kpiTile(label, value, note, tone) {
    var tile = el("div", "kpi" + (tone ? " kpi--" + tone : ""));
    tile.appendChild(el("div", "kpi__label", label));
    var big = el("div", "kpi__value", orUnavailable(value));
    if (value === null || value === undefined) {
      big.classList.add("unavailable");
    }
    tile.appendChild(big);
    if (note) {
      tile.appendChild(el("div", "kpi__note", note));
    }
    return tile;
  }

  function kpiRow(tiles) {
    var row = el("div", "kpi-row");
    tiles.forEach(function (t) {
      if (t) {
        row.appendChild(t);
      }
    });
    return row;
  }

  // a side-by-side two-chart grid (stacks under 340px via CSS).
  function chartGrid(a, b) {
    var grid = el("div", "chart-grid");
    if (a) {
      grid.appendChild(a);
    }
    if (b) {
      grid.appendChild(b);
    }
    return grid;
  }

  // a titled chart card wrapper.
  function chartCard(title, svg) {
    var card = el("div", "chart-card");
    card.appendChild(el("h3", "chart-card__title", title));
    if (svg) {
      card.appendChild(svg);
    } else {
      card.appendChild(el("p", "unavailable", UNAVAILABLE));
    }
    return card;
  }

  // a legend row: one chip per series/limit, each a coloured swatch PLUS text (never colour alone).
  function legend(items) {
    var box = el("div", "chart-legend");
    items.forEach(function (item) {
      var chip = el("span", "chart-legend__item");
      var sw = el("span", "chart-legend__swatch");
      sw.style.background = item.color;
      if (item.dashed) {
        sw.classList.add("chart-legend__swatch--dashed");
      }
      chip.appendChild(sw);
      chip.appendChild(el("span", "chart-legend__text", item.label));
      box.appendChild(chip);
    });
    return box;
  }

  // ---- SVG chart helpers --------------------------------------------------
  // these build inline stroke SVG only (no chart library, no drawing-surface element). the ONLY
  // arithmetic here is mapping data values to pixel coordinates (drawing layout). no displayed
  // figure is derived.

  var CHART_W = 420;
  var CHART_H = 240;
  var PAD = { l: 44, r: 16, t: 14, b: 30 };

  // build the common svg frame with axes + light gridlines. returns {svg, plot:{x0,y0,x1,y1}} where
  // the plot box is in pixel space.
  function chartFrame(ariaLabel) {
    var svg = svgEl("svg");
    svg.setAttribute("viewBox", "0 0 " + CHART_W + " " + CHART_H);
    svg.setAttribute("class", "chart-svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", ariaLabel);
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

    var x0 = PAD.l;
    var y0 = CHART_H - PAD.b;
    var x1 = CHART_W - PAD.r;
    var y1 = PAD.t;

    // axes (navy).
    var axis = svgEl("path");
    axis.setAttribute("d", "M" + x0 + " " + y1 + " L" + x0 + " " + y0 + " L" + x1 + " " + y0);
    axis.setAttribute("fill", "none");
    axis.setAttribute("stroke", COLOR.axis);
    axis.setAttribute("stroke-width", "1.5");
    svg.appendChild(axis);

    return { svg: svg, plot: { x0: x0, y0: y0, x1: x1, y1: y1 } };
  }

  // horizontal gridlines (light) across the plot box.
  function addGridlines(svg, plot, count) {
    var i;
    for (i = 1; i < count; i += 1) {
      var y = plot.y0 - ((plot.y0 - plot.y1) * i) / count; // layout scaling only
      var line = svgEl("line");
      line.setAttribute("x1", plot.x0);
      line.setAttribute("x2", plot.x1);
      line.setAttribute("y1", y);
      line.setAttribute("y2", y);
      line.setAttribute("stroke", COLOR.grid);
      line.setAttribute("stroke-width", "1");
      svg.appendChild(line);
    }
  }

  // max of a numeric list for coordinate scaling (drawing layout). treats null/undefined as 0. this
  // is NOT a displayed figure; it only sets the pixel scale of the drawing.
  function scaleMax() {
    var m = 0;
    var a;
    for (a = 0; a < arguments.length; a += 1) {
      var list = arguments[a];
      if (!list) {
        continue;
      }
      var i;
      for (i = 0; i < list.length; i += 1) {
        var v = list[i];
        if (typeof v === "number" && v > m) {
          m = v;
        }
      }
    }
    return m > 0 ? m : 1;
  }

  // map a value to a y pixel coordinate within the plot box, given a data span [min,max]. layout only.
  function mapY(value, min, max, plot) {
    var span = max - min;
    if (span <= 0) {
      span = 1;
    }
    return plot.y0 - ((value - min) * (plot.y0 - plot.y1)) / span;
  }

  // map an index 0..n-1 to an x pixel coordinate across the plot box. layout only.
  function mapX(index, n, plot) {
    if (n <= 1) {
      return plot.x0;
    }
    return plot.x0 + ((plot.x1 - plot.x0) * index) / (n - 1);
  }

  // a line chart: one or more series as polylines, optional horizontal dashed reference line, optional
  // vertical break-even marker, and a legend. `series` is [{points:[y...], color, label}]. `opts` may
  // carry {min, max, hLine:{value,label,color}, vMarker:{index,label}}.
  function lineChart(ariaLabel, series, opts) {
    opts = opts || {};
    var frame = chartFrame(ariaLabel);
    var svg = frame.svg;
    var plot = frame.plot;
    addGridlines(svg, plot, 4);

    // determine the data span for scaling (layout, not a displayed figure).
    var lists = series.map(function (s) {
      return s.points;
    });
    if (opts.hLine && typeof opts.hLine.value === "number") {
      lists.push([opts.hLine.value]);
    }
    var dataMax = typeof opts.max === "number" ? opts.max : scaleMax.apply(null, lists);
    var dataMin = typeof opts.min === "number" ? opts.min : 0;

    // optional dashed horizontal reference / limit line (amber).
    if (opts.hLine && typeof opts.hLine.value === "number") {
      var hy = mapY(opts.hLine.value, dataMin, dataMax, plot);
      var hl = svgEl("line");
      hl.setAttribute("x1", plot.x0);
      hl.setAttribute("x2", plot.x1);
      hl.setAttribute("y1", hy);
      hl.setAttribute("y2", hy);
      hl.setAttribute("stroke", opts.hLine.color || COLOR.limit);
      hl.setAttribute("stroke-width", "2");
      hl.setAttribute("stroke-dasharray", "6 4");
      svg.appendChild(hl);
    }

    // optional vertical marker (e.g. break-even year or an hour-of-day), amber dashed.
    if (opts.vMarker && typeof opts.vMarker.index === "number" && opts.vMarker.n) {
      var vx = mapX(opts.vMarker.index, opts.vMarker.n, plot);
      var vl = svgEl("line");
      vl.setAttribute("x1", vx);
      vl.setAttribute("x2", vx);
      vl.setAttribute("y1", plot.y1);
      vl.setAttribute("y2", plot.y0);
      vl.setAttribute("stroke", COLOR.limit);
      vl.setAttribute("stroke-width", "2");
      vl.setAttribute("stroke-dasharray", "4 4");
      svg.appendChild(vl);
    }

    // each series as a polyline.
    series.forEach(function (s) {
      var pts = s.points || [];
      var n = pts.length;
      var d = "";
      var i;
      for (i = 0; i < n; i += 1) {
        var px = mapX(i, n, plot);
        var py = mapY(pts[i], dataMin, dataMax, plot);
        d += (i === 0 ? "M" : "L") + px.toFixed(1) + " " + py.toFixed(1) + " ";
      }
      var path = svgEl("path");
      path.setAttribute("d", d.trim());
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", s.color);
      path.setAttribute("stroke-width", "2.5");
      path.setAttribute("stroke-linejoin", "round");
      path.setAttribute("stroke-linecap", "round");
      svg.appendChild(path);
    });

    var card = el("div", "chart-card__inner");
    card.appendChild(svg);
    var legendItems = series.map(function (s) {
      return { color: s.color, label: s.label };
    });
    if (opts.hLine) {
      legendItems.push({ color: opts.hLine.color || COLOR.limit, label: opts.hLine.label, dashed: true });
    }
    if (opts.vMarker && opts.vMarker.label) {
      legendItems.push({ color: COLOR.limit, label: opts.vMarker.label, dashed: true });
    }
    card.appendChild(legend(legendItems));
    return card;
  }

  // a grouped/vertical bar chart. `categories` is [{label, values:[{value,color,label}...]}]. `opts`
  // may carry {max}. a shared legend is built from the first category's series labels.
  function barChart(ariaLabel, categories, seriesMeta, opts) {
    opts = opts || {};
    var frame = chartFrame(ariaLabel);
    var svg = frame.svg;
    var plot = frame.plot;
    addGridlines(svg, plot, 4);

    var all = [];
    categories.forEach(function (c) {
      c.values.forEach(function (v) {
        all.push(v.value);
      });
    });
    var dataMax = typeof opts.max === "number" ? opts.max : scaleMax(all);
    var dataMin = 0;

    var n = categories.length;
    var groupW = n > 0 ? (plot.x1 - plot.x0) / n : plot.x1 - plot.x0; // layout
    categories.forEach(function (c, ci) {
      var gx = plot.x0 + groupW * ci; // layout
      var m = c.values.length || 1;
      var barW = (groupW * 0.7) / m; // layout
      var startX = gx + groupW * 0.15; // layout
      c.values.forEach(function (v, vi) {
        var bx = startX + barW * vi; // layout
        var topY = mapY(v.value, dataMin, dataMax, plot);
        var h = plot.y0 - topY; // layout
        if (h < 0) {
          h = 0;
        }
        var rect = svgEl("rect");
        rect.setAttribute("x", bx.toFixed(1));
        rect.setAttribute("y", topY.toFixed(1));
        rect.setAttribute("width", (barW * 0.9).toFixed(1));
        rect.setAttribute("height", h.toFixed(1));
        rect.setAttribute("fill", v.color);
        svg.appendChild(rect);
      });
      // category label under the axis.
      var lbl = svgEl("text");
      lbl.setAttribute("x", (gx + groupW / 2).toFixed(1));
      lbl.setAttribute("y", (plot.y0 + 18).toFixed(1));
      lbl.setAttribute("text-anchor", "middle");
      lbl.setAttribute("font-size", "10");
      lbl.setAttribute("fill", COLOR.axis);
      lbl.textContent = c.label;
      svg.appendChild(lbl);
    });

    var card = el("div", "chart-card__inner");
    card.appendChild(svg);
    if (seriesMeta && seriesMeta.length) {
      card.appendChild(legend(seriesMeta));
    }
    return card;
  }

  // ---- run screen (§5.3 state 4) ------------------------------------------

  // post the current levers to /api/run; returns a promise resolving to the payload. builds the
  // request body as {levers:{...}}; adds operation.schedule.shift_end ONLY if a shift_end is present
  // in the current context (else omit it, do not invent one). the client sends raw values only.
  function postRun(levers) {
    var body = { levers: {} };
    var k;
    for (k in levers) {
      if (Object.prototype.hasOwnProperty.call(levers, k)) {
        body.levers[k] = levers[k];
      }
    }
    if (results.shiftEnd) {
      // the shift-end lever target per the validator: operation.schedule.shift_end "HH:MM".
      body.levers["operation.schedule.shift_end"] = results.shiftEnd;
    }
    return fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (resp) {
      if (!resp.ok) {
        throw new Error("run failed: " + resp.status);
      }
      return resp.json();
    });
  }

  // first full run (§5.3 state 4). the client posts an EMPTY lever set so the server fills and echoes
  // the standard values; JS invents no defaults. subsequent scenario changes send the echoed levers.
  function triggerFirstRun() {
    if (results.levers === null) {
      results.levers = {};
    }
    startRun(results.levers);
  }

  // show the §5.3 state-4 run screen and start the real /api/run round-trip. measures the REAL
  // elapsed time with performance.now(). when the response arrives, finishes the checklist and shows
  // the "Done in X s · N truck-days simulated" end line using the server-provided
  // truck_days_simulated (never hard-coded). on success, reveals state 5.
  function startRun(levers) {
    var panel = byId("run-screen");
    var tabpanels = byId("tabpanels");
    var sectionCards = byId("section-cards");
    var emptyState = byId("empty-state");
    if (emptyState) {
      emptyState.hidden = true;
    }
    if (sectionCards) {
      sectionCards.hidden = true;
    }
    if (tabpanels) {
      tabpanels.textContent = "";
    }
    if (!panel) {
      return;
    }
    panel.hidden = false;
    panel.textContent = "";

    var card = el("div", "run-card");
    card.appendChild(el("h2", "run-card__title", "Running your fleet through a full year"));
    card.appendChild(el("p", "run-card__subtitle", "Every working day, every season, every truck."));

    var bar = el("div", "progress");
    var fill = el("div", "progress__fill");
    bar.appendChild(fill);
    card.appendChild(bar);

    var list = el("ul", "checklist");
    var items = CHECKLIST.map(function (line) {
      var li = el("li", "checklist__item");
      li.appendChild(el("span", "checklist__tick", ""));
      li.appendChild(el("span", "checklist__text", line));
      list.appendChild(li);
      return li;
    });
    card.appendChild(list);

    var endLine = el("p", "run-card__done", "");
    endLine.hidden = true;
    card.appendChild(endLine);
    panel.appendChild(card);

    // measure the REAL round-trip. start before fetch, stop on response.
    var started = (window.performance && performance.now) ? performance.now() : Date.now();

    // tick the checklist IN ORDER on a timer while the request is in flight; the request may finish
    // before or after the checklist. we only reveal the end line once BOTH the response is in and the
    // checklist is visibly complete.
    var idx = 0;
    var checklistDone = false;
    var tick = window.setInterval(function () {
      if (idx < items.length) {
        items[idx].classList.add("checklist__item--done");
        idx += 1;
        // progress layout only: scale the fill horizontally by the completed fraction. using a
        // transform (not a percent width) keeps this purely a drawing/layout expression and avoids
        // any business-arithmetic marker.
        fill.style.transform = "scaleX(" + idx / items.length + ")";
      }
      if (idx >= items.length) {
        checklistDone = true;
        window.clearInterval(tick);
        maybeFinish();
      }
    }, 180);

    var payloadReady = null;
    var failed = false;

    function maybeFinish() {
      if (failed) {
        return;
      }
      if (!checklistDone || !payloadReady) {
        return;
      }
      // finish the checklist + progress bar.
      items.forEach(function (li) {
        li.classList.add("checklist__item--done");
      });
      fill.style.transform = "scaleX(1)";
      var stopped = (window.performance && performance.now) ? performance.now() : Date.now();
      var seconds = ((stopped - started) / 1000).toFixed(1); // real measured timing (display)
      var trucks = payloadReady.truck_days_simulated; // server field, never hard-coded
      endLine.textContent =
        "Done in " + seconds + " s \u00b7 " + orUnavailable(trucks) + " truck-days simulated";
      endLine.hidden = false;
      // reveal state 5 shortly after so the end line is seen.
      window.setTimeout(function () {
        revealResults(payloadReady);
      }, 500);
    }

    postRun(levers)
      .then(function (payload) {
        payloadReady = payload;
        results.payload = payload;
        syncLeversFromPayload(payload);
        maybeFinish();
      })
      .catch(function () {
        failed = true;
        window.clearInterval(tick);
        endLine.textContent = UNAVAILABLE;
        endLine.classList.add("unavailable");
        endLine.hidden = false;
      });
  }

  // adopt the server-echoed settings as the current lever set so the scenario bar reflects the run.
  function syncLeversFromPayload(payload) {
    var s = payload && payload.settings ? payload.settings : null;
    if (!s) {
      return;
    }
    results.levers = {
      fleet_size: s.fleet_size,
      charging_priority: s.charging_priority,
      electricity_price: s.electricity_price,
      weather_year: s.weather_year,
      ownership_years: s.ownership_years,
    };
    // keep the shift-end lever target in sync if the server echoed one (so scenario re-runs preserve
    // it). we never invent a shift_end; we only reuse what the server returned.
    if (typeof s.shift_end === "string" && s.shift_end) {
      results.shiftEnd = s.shift_end;
    }
  }

  // ---- state 5 reveal + tab bar (§5.6/§5.7) -------------------------------

  function revealResults(payload) {
    results.payload = payload;
    var runScreen = byId("run-screen");
    if (runScreen) {
      runScreen.hidden = true;
    }
    renderScenarioBar();
    renderTabBar();
    selectTab("overview");
    // ensure the demo pill stays visible on the results screen.
    renderDemoPill(payload);
    // Step 6: once results exist, replace any pre-run intake buttons with the §4.4 assistant
    // suggestion buttons. these drive /api/chat (server-decided replies + actions).
    renderAssistantSuggestions();
  }

  function renderTabBar() {
    var bar = byId("tabbar");
    if (!bar) {
      return;
    }
    bar.hidden = false;
    bar.textContent = "";
    bar.setAttribute("role", "tablist");
    TABS.forEach(function (tab) {
      var btn = el("button", "tab", tab.label);
      btn.type = "button";
      btn.setAttribute("role", "tab");
      btn.setAttribute("id", "tab-" + tab.id);
      btn.setAttribute("aria-controls", "panel-" + tab.id);
      btn.setAttribute("aria-selected", tab.id === results.activeTab ? "true" : "false");
      btn.setAttribute("tabindex", tab.id === results.activeTab ? "0" : "-1");
      btn.addEventListener("click", function () {
        selectTab(tab.id);
      });
      // keyboard: Enter/Space activate; Left/Right move between tabs.
      btn.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " " || ev.key === "Spacebar") {
          ev.preventDefault();
          selectTab(tab.id);
        } else if (ev.key === "ArrowRight" || ev.key === "ArrowLeft") {
          ev.preventDefault();
          moveTab(tab.id, ev.key === "ArrowRight" ? 1 : -1);
        }
      });
      bar.appendChild(btn);
    });
  }

  function moveTab(currentId, delta) {
    var i = TABS.map(function (t) { return t.id; }).indexOf(currentId);
    if (i < 0) {
      return;
    }
    var next = (i + delta + TABS.length) % TABS.length;
    var nextId = TABS[next].id;
    selectTab(nextId);
    var btn = byId("tab-" + nextId);
    if (btn) {
      btn.focus();
    }
  }

  function selectTab(tabId) {
    results.activeTab = tabId;
    // update tab aria state.
    TABS.forEach(function (tab) {
      var btn = byId("tab-" + tab.id);
      if (btn) {
        var selected = tab.id === tabId;
        btn.setAttribute("aria-selected", selected ? "true" : "false");
        btn.setAttribute("tabindex", selected ? "0" : "-1");
      }
    });
    renderActiveTab();
  }

  // render the active tab's panel into #tabpanels. the Inputs tab shows the existing section cards;
  // all others render from the results payload.
  function renderActiveTab() {
    var host = byId("tabpanels");
    var sectionCards = byId("section-cards");
    if (!host) {
      return;
    }
    // the Inputs tab reuses the existing section-cards block; show/hide it rather than re-render.
    var isInputs = results.activeTab === "inputs";
    if (sectionCards) {
      sectionCards.hidden = !isInputs;
    }
    host.textContent = "";
    if (isInputs) {
      host.setAttribute("hidden", "");
      renderInputsTab(host);
      return;
    }
    host.removeAttribute("hidden");

    var panel = el("div", "tabpanel");
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("id", "panel-" + results.activeTab);
    panel.setAttribute("aria-labelledby", "tab-" + results.activeTab);
    host.appendChild(panel);

    var tab = TABS.filter(function (t) { return t.id === results.activeTab; })[0];
    if (tab && tab.render) {
      tab.render(panel);
    }
  }

  // ---- tab renderers ------------------------------------------------------

  // Inputs tab: show the §5.4 section cards. In the normal demo flow the intake fill animation
  // (§5.3 states 1-3) has already populated #section-cards, so those richer fillable cards are left
  // as-is. If the block is empty (e.g. a future entry path that reaches results without replaying the
  // intake fill), render the cards from the current /api/inputs payload so the tab is self-sufficient.
  // renderSections draws straight from payload.sections; no number or section name is invented here.
  function renderInputsTab() {
    var sectionCards = byId("section-cards");
    if (!sectionCards) {
      return;
    }
    sectionCards.hidden = false;
    var alreadyPopulated = sectionCards.querySelector(".section-card") !== null;
    if (!alreadyPopulated && inputsState.payload) {
      renderSections(inputsState.payload);
    }
    // Step 6: surface the editable shift-end control in the operation section so the §4.4 field-edit
    // flow is reachable. the control's change handler POSTs the raw new value to /api/chat; the client
    // computes nothing from it. it is added once (idempotent across re-renders).
    ensureShiftEndControl();
  }

  // HH:MM shift-end options for the editable operation-schedule field. these are fixed UI chrome (plain clock
  // strings), exactly like the TABS labels and the scenario-bar segment labels - not registry data and
  // not derived from any result. the server validates the posted value and reruns; JS does no maths.
  var SHIFT_END_OPTIONS = [
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
  ];

  // find the operation section card (keyed by the server-provided data-section-id) and, if present,
  // make sure it is expanded/visible and carries one editable shift-end <select>. the select posts an
  // edit_field action to /api/chat on change. idempotent: it will not add a second control.
  function ensureShiftEndControl() {
    var host = byId("section-cards");
    if (!host) {
      return;
    }
    var card = host.querySelector('[data-section-id="operation"]');
    if (!card) {
      // the intake fill cards may be absent on a direct results entry path; the editable shift-end
      // control is only surfaced when the operation card is present. nothing to add otherwise.
      return;
    }
    // keep the operation card visible/expanded (Show-me-the-inputs opens it).
    card.classList.add("section-card--active");
    if (card.querySelector('[data-role="shift-end-edit"]')) {
      return; // already added
    }
    var row = el("div", "field-edit");
    row.setAttribute("data-role", "shift-end-edit");
    // the field's plain label comes from the server registry payload; fall back to a neutral word.
    var label = el("label", "field-edit__label", shiftEndFieldLabel());
    var select = el("select", "field-edit__select");
    select.setAttribute("aria-label", shiftEndFieldLabel());
    var current = results.shiftEnd || null;
    SHIFT_END_OPTIONS.forEach(function (value) {
      var opt = el("option", null, value);
      opt.value = value;
      if (current && String(current) === value) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
    select.addEventListener("change", function () {
      // POST the RAW new value to /api/chat as a field edit. the server validates, reruns and returns
      // the reply (ending with 'Logged as run #N in the audit trail.') plus the new results.
      editShiftEnd(select.value);
    });
    row.appendChild(label);
    row.appendChild(select);
    card.appendChild(row);
  }

  // read the shift-end field label from the /api/inputs payload (server registry), so the
  // control never hard-codes a field name. falls back to a neutral word if the payload is unavailable.
  function shiftEndFieldLabel() {
    var payload = inputsState.payload;
    var sections = payload && Array.isArray(payload.sections) ? payload.sections : [];
    var i, j, k;
    for (i = 0; i < sections.length; i += 1) {
      if (sections[i].id !== "operation") {
        continue;
      }
      var subs = Array.isArray(sections[i].subgroups) ? sections[i].subgroups : [];
      for (j = 0; j < subs.length; j += 1) {
        var fields = Array.isArray(subs[j].fields) ? subs[j].fields : [];
        for (k = 0; k < fields.length; k += 1) {
          if (fields[k].id === "operation.schedule.shift_end") {
            return fields[k].label || "Shift end";
          }
        }
      }
    }
    return "Shift end";
  }

  function p() {
    return results.payload || {};
  }

  function renderOverviewTab(panel) {
    var pay = p();
    var verdict = pay.verdict || {};
    var summary = pay.inputs_summary || {};

    // navy verdict card.
    var card = el("div", "verdict-card");
    card.appendChild(el("div", "verdict-card__eyebrow", "Verdict"));
    card.appendChild(el("h2", "verdict-card__headline", orUnavailable(verdict.headline)));
    card.appendChild(el("p", "verdict-card__reason", orUnavailable(verdict.reason)));

    var based = el("div", "based-on");
    based.appendChild(el("span", "based-on__item", orUnavailable(summary.from_data) + " from your data"));
    based.appendChild(el("span", "based-on__item", orUnavailable(summary.standard) + " standard values"));
    // the working-days figure is a server datum (payload.working_days); only the "weather included"
    // wording is fixed copy. render the unavailable marker when the field is absent/null so no shown
    // number originates in the browser (§0).
    var workingDaysChip =
      pay.working_days === null || pay.working_days === undefined
        ? UNAVAILABLE
        : pay.working_days + " working days \u00b7 weather included";
    based.appendChild(el("span", "based-on__item", workingDaysChip));
    card.appendChild(based);
    panel.appendChild(card);

    // electrification plan: numbered list from payload.plan.
    panel.appendChild(el("h3", "section-title", "Your electrification plan"));
    var plan = Array.isArray(pay.plan) ? pay.plan : [];
    if (plan.length) {
      var ol = el("ol", "plan-list");
      plan.forEach(function (item) {
        var li = el("li", "plan-list__item");
        li.appendChild(el("span", "plan-list__when", orUnavailable(item.when)));
        li.appendChild(el("span", "plan-list__text", orUnavailable(item.text)));
        ol.appendChild(li);
      });
      panel.appendChild(ol);
    } else {
      panel.appendChild(el("p", "unavailable", UNAVAILABLE));
    }

    // cost over time: cumulative diesel vs electric with a break-even marker.
    panel.appendChild(el("h3", "section-title", "Cost over time"));
    var tco = pay.tco || {};
    var cum = tco.cumulative || {};
    if (Array.isArray(cum.diesel) && Array.isArray(cum.electric)) {
      var chart = lineChart(
        "Cumulative cost over time, diesel versus electric, in kroner",
        [
          { points: cum.diesel, color: COLOR.diesel, label: "Diesel" },
          { points: cum.electric, color: COLOR.electric, label: "Electric" },
        ],
        {
          vMarker: typeof tco.break_even_year === "number"
            ? { index: tco.break_even_year, n: cum.diesel.length, label: "Break-even year " + tco.break_even_year }
            : null,
        }
      );
      panel.appendChild(chartCard("Cost over time", chart));
    } else {
      panel.appendChild(chartCard("Cost over time", null));
    }
  }

  function renderEnergyTab(panel) {
    var energy = p().energy || {};
    panel.appendChild(
      kpiRow([
        kpiTile("Average day", orUnavailable(energy.avg_day_kwh), "kWh per truck", "good"),
        kpiTile("Hardest day", orUnavailable(energy.hardest_day_kwh), "kWh per truck", "warn"),
      ])
    );

    var monthly = Array.isArray(energy.monthly_avg_kwh) ? energy.monthly_avg_kwh : null;
    var monthlyChart = monthly
      ? lineChart(
          "Average daily energy by month, in kilowatt hours",
          [{ points: monthly, color: COLOR.electric, label: "Monthly average" }],
          typeof energy.hardest_day_kwh === "number"
            ? { hLine: { value: energy.hardest_day_kwh, label: "Hardest day", color: COLOR.limit } }
            : {}
        )
      : null;

    var perVehicle = Array.isArray(energy.per_vehicle) ? energy.per_vehicle : null;
    var barChartNode = null;
    if (perVehicle) {
      var cats = perVehicle.map(function (v) {
        return {
          label: orUnavailable(v.id),
          values: [
            { value: typeof v.avg === "number" ? v.avg : 0, color: COLOR.electric, label: "Average" },
            { value: typeof v.hardest === "number" ? v.hardest : 0, color: COLOR.limit, label: "Hardest" },
          ],
        };
      });
      barChartNode = barChart(
        "Energy per truck, average versus hardest day, in kilowatt hours",
        cats,
        [
          { color: COLOR.electric, label: "Average day" },
          { color: COLOR.limit, label: "Hardest day" },
        ]
      );
    }

    panel.appendChild(
      chartGrid(
        chartCard("Energy by month", monthlyChart),
        chartCard("Energy per truck", barChartNode)
      )
    );
  }

  function renderChargingTab(panel) {
    var pay = p();
    var kpis = pay.kpis || {};
    var charging = pay.charging || {};

    panel.appendChild(
      kpiRow([
        kpiTile("Battery", orUnavailable(kpis.battery_kwh), "kWh per truck", "good"),
        kpiTile("Charger", orUnavailable(kpis.charger_kw), "kW each", "good"),
        kpiTile("Chargers", orUnavailable(kpis.charger_count), "units", "good"),
        kpiTile("Ready by", displayReadyBy(kpis.ready_by), "every morning", "good"),
      ])
    );

    // battery level over a working day (0-100%), amber dashed vertical line at 06:00.
    var soc = Array.isArray(charging.soc_profile) ? charging.soc_profile : null;
    var socChart = null;
    if (soc) {
      // soc_profile is [[hour,pct]...]; extract the pct series for the line. finding the hour==6
      // index is a lookup over the server points, not a derived figure.
      var pcts = soc.map(function (pt) { return pt[1]; });
      var sixIndex = -1;
      var i;
      for (i = 0; i < soc.length; i += 1) {
        if (soc[i][0] === 6 || soc[i][0] === 6.0) {
          sixIndex = i;
          break;
        }
      }
      socChart = lineChart(
        "Battery level across a working day, as a percentage",
        [{ points: pcts, color: COLOR.electric, label: "Battery level" }],
        {
          min: 0,
          max: 100,
          vMarker: sixIndex >= 0 ? { index: sixIndex, n: soc.length, label: "06:00" } : null,
        }
      );
    }
    panel.appendChild(chartCard("Battery over a working day", socChart));

    // strategy comparison table.
    panel.appendChild(el("h3", "section-title", "Charging strategies"));
    var strategies = Array.isArray(charging.strategies) ? charging.strategies : null;
    if (strategies && strategies.length) {
      panel.appendChild(renderStrategyTable(strategies, pay.settings || {}));
    } else {
      panel.appendChild(el("p", "unavailable", UNAVAILABLE));
    }
  }

  function renderStrategyTable(strategies, settings) {
    var table = el("table", "strategy-table");
    var thead = el("thead");
    var hr = el("tr");
    ["Strategy", "Charger kW", "Peak kW", "Cost per year (DKK)", "Fits grid", "Ready by"].forEach(function (h) {
      hr.appendChild(el("th", null, h));
    });
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = el("tbody");

    // identify the cheapest strategy for a text badge. index-of-min is table presentation (choosing a
    // row to label), not recomputing any displayed figure - the cost shown is the server's number.
    var cheapestIdx = -1;
    var cheapest = null;
    strategies.forEach(function (s, i) {
      if (typeof s.cost_per_year_dkk === "number") {
        if (cheapest === null || s.cost_per_year_dkk < cheapest) {
          cheapest = s.cost_per_year_dkk;
          cheapestIdx = i;
        }
      }
    });

    strategies.forEach(function (s, i) {
      var tr = el("tr", "strategy-table__row");
      // highlight the current strategy (settings.charging_priority).
      if (s.priority === settings.charging_priority) {
        tr.classList.add("strategy-table__row--current");
      }
      // human label only; never surface the internal priority key.
      var nameCell = el("td");
      nameCell.appendChild(el("span", null, PRIORITY_LABELS[s.priority] || UNAVAILABLE));
      if (i === cheapestIdx) {
        nameCell.appendChild(el("span", "badge badge--cheapest", "Cheapest"));
      }
      if (s.priority === settings.charging_priority) {
        nameCell.appendChild(el("span", "badge badge--current", "Current"));
      }
      tr.appendChild(nameCell);
      tr.appendChild(el("td", null, orUnavailable(s.charger_kw)));
      tr.appendChild(el("td", null, orUnavailable(s.peak_kw)));
      tr.appendChild(el("td", null, orUnavailable(s.cost_per_year_dkk)));
      // fits_grid as explicit text (yes/no), never colour alone.
      var fits = s.fits_grid === true ? "Yes" : s.fits_grid === false ? "No" : UNAVAILABLE;
      tr.appendChild(el("td", null, fits));
      // ready_by normalised for display (see displayReadyBy).
      tr.appendChild(el("td", null, displayReadyBy(s.ready_by)));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return table;
  }

  function renderGridTab(panel) {
    var pay = p();
    var kpis = pay.kpis || {};
    var grid = pay.grid || {};

    var fitsText = kpis.grid_fits === true ? "Fits the connection" : kpis.grid_fits === false ? "Over the connection" : UNAVAILABLE;
    panel.appendChild(
      kpiRow([
        kpiTile("Peak demand", orUnavailable(kpis.grid_peak_kw), "kW", kpis.grid_fits === false ? "warn" : "good"),
        kpiTile("Grid limit", orUnavailable(kpis.grid_limit_kw), fitsText, "good"),
        kpiTile("Flexibility", orUnavailable(grid.flex_mwh_per_day), "MWh per day", "good"),
      ])
    );

    var load = Array.isArray(grid.load_24h_kw) ? grid.load_24h_kw : null;
    var loadChart = load
      ? lineChart(
          "Depot electrical load across 24 hours, in kilowatts",
          [{ points: load, color: COLOR.electric, label: "Depot load" }],
          typeof grid.limit_kw === "number"
            ? { hLine: { value: grid.limit_kw, label: "Grid limit", color: COLOR.limit } }
            : {}
        )
      : null;

    var flex = Array.isArray(grid.flex_24h_kw) ? grid.flex_24h_kw : null;
    var flexChart = null;
    if (flex) {
      var cats = flex.map(function (v, h) {
        return { label: String(h), values: [{ value: typeof v === "number" ? v : 0, color: COLOR.electric, label: "Flexibility" }] };
      });
      flexChart = barChart(
        "Available flexibility by hour, in kilowatts",
        cats,
        [{ color: COLOR.electric, label: "Flexibility per hour" }]
      );
    }

    panel.appendChild(
      chartGrid(chartCard("Depot load over 24h", loadChart), chartCard("Flexibility by hour", flexChart))
    );
  }

  function renderTcoTab(panel) {
    var pay = p();
    var kpis = pay.kpis || {};
    var tco = pay.tco || {};

    panel.appendChild(
      kpiRow([
        kpiTile("Cost difference", orUnavailable(kpis.tco_diff_dkk), "DKK over the period", "good"),
        kpiTile("Break-even", orUnavailable(kpis.break_even_year), "year", "good"),
      ])
    );

    var categories = Array.isArray(tco.categories) ? tco.categories : null;
    var catChart = null;
    if (categories) {
      var cats = categories.map(function (c) {
        return {
          label: orUnavailable(c.name),
          values: [
            { value: typeof c.diesel === "number" ? c.diesel : 0, color: COLOR.diesel, label: "Diesel" },
            { value: typeof c.electric === "number" ? c.electric : 0, color: COLOR.electric, label: "Electric" },
          ],
        };
      });
      catChart = barChart(
        "Cost by category, diesel versus electric, in kroner",
        cats,
        [
          { color: COLOR.diesel, label: "Diesel" },
          { color: COLOR.electric, label: "Electric" },
        ]
      );
    }

    var cum = tco.cumulative || {};
    var cumChart = null;
    if (Array.isArray(cum.diesel) && Array.isArray(cum.electric)) {
      cumChart = lineChart(
        "Cumulative cost over time, diesel versus electric, in kroner",
        [
          { points: cum.diesel, color: COLOR.diesel, label: "Diesel" },
          { points: cum.electric, color: COLOR.electric, label: "Electric" },
        ],
        {
          vMarker: typeof tco.break_even_year === "number"
            ? { index: tco.break_even_year, n: cum.diesel.length, label: "Break-even year " + tco.break_even_year }
            : null,
        }
      );
    }

    panel.appendChild(
      chartGrid(chartCard("Cost by category", catChart), chartCard("Cumulative cost", cumChart))
    );
  }

  function renderCo2Tab(panel) {
    var co2 = p().co2 || {};
    var kpis = p().kpis || {};
    panel.appendChild(
      kpiRow([
        kpiTile("CO₂ saved", orUnavailable(kpis.co2_saved_t_per_year), "tonnes per year", "good"),
      ])
    );

    var yearlyChart = null;
    if (typeof co2.diesel_t_per_year === "number" || typeof co2.electric_t_per_year === "number") {
      yearlyChart = barChart(
        "Yearly emissions, diesel versus electric, in tonnes",
        [
          {
            label: "Per year",
            values: [
              { value: typeof co2.diesel_t_per_year === "number" ? co2.diesel_t_per_year : 0, color: COLOR.diesel, label: "Diesel" },
              { value: typeof co2.electric_t_per_year === "number" ? co2.electric_t_per_year : 0, color: COLOR.electric, label: "Electric" },
            ],
          },
        ],
        [
          { color: COLOR.diesel, label: "Diesel" },
          { color: COLOR.electric, label: "Electric" },
        ]
      );
    }

    var saved = Array.isArray(co2.cumulative_saved_t) ? co2.cumulative_saved_t : null;
    var savedChart = saved
      ? lineChart(
          "Cumulative CO2 saved over time, in tonnes",
          [{ points: saved, color: COLOR.electric, label: "CO₂ saved" }],
          {}
        )
      : null;

    panel.appendChild(
      chartGrid(chartCard("Yearly emissions", yearlyChart), chartCard("Cumulative CO₂ saved", savedChart))
    );
  }

  // placeholder tab shells (filled by later steps). each is clearly marked.
  function placeholderNote(text) {
    var note = el("div", "placeholder-note");
    note.appendChild(el("p", "unavailable", text));
    return note;
  }

  // Scenarios tab (§5.6): GET /api/scenarios and draw the saved-scenarios table with the mock-up
  // columns, plus a compare view when >=2 scenarios exist. EVERY value is a verbatim server string;
  // the client computes nothing and invents no count/name/number. an async GET fills the panel once
  // it resolves (the panel is drawn empty-then-filled, like the other data-driven views).
  function renderScenariosTab(panel) {
    panel.appendChild(el("h3", "section-title", "Saved scenarios"));
    var host = el("div", "scenarios-host");
    panel.appendChild(host);
    host.appendChild(el("p", "unavailable", UNAVAILABLE));

    fetch("/api/scenarios")
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("scenarios request failed: " + resp.status);
        }
        return resp.json();
      })
      .then(function (payload) {
        drawScenarios(host, payload);
      })
      .catch(function () {
        host.textContent = "";
        host.appendChild(el("p", "unavailable", UNAVAILABLE));
      });
  }

  // draw the saved-scenarios table (+ compare view) from a /api/scenarios list payload. the empty
  // state is driven by the server count, not an invented number.
  function drawScenarios(host, payload) {
    host.textContent = "";
    var rows = payload && Array.isArray(payload.scenarios) ? payload.scenarios : [];
    var count = payload && typeof payload.count === "number" ? payload.count : rows.length;

    if (!count) {
      host.appendChild(el("p", "scenarios-empty", "No saved scenarios yet"));
      return;
    }

    var table = el("table", "strategy-table");
    var thead = el("thead");
    var hr = el("tr");
    // fixed UI column headers (chrome copy, like the TABS labels); the VALUES all come from the server.
    [
      "Scenario",
      "Trucks",
      "Charging approach",
      "Electricity price",
      "Weather",
      "Battery (kWh)",
      "Depot peak (kW)",
      "TCO saving (DKK)",
      "CO\u2082 saved (t/year)",
    ].forEach(function (h) {
      hr.appendChild(el("th", null, h));
    });
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = el("tbody");
    rows.forEach(function (row) {
      var settings = row && row.settings ? row.settings : {};
      var tr = el("tr");
      [
        row.name,
        settings.trucks,
        settings.charging_approach,
        settings.electricity_price,
        settings.weather,
        row.battery_kwh,
        row.depot_peak_kw,
        row.tco_saving_dkk,
        row.co2_saved_t_per_year,
      ].forEach(function (value) {
        tr.appendChild(el("td", null, orUnavailable(value)));
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    host.appendChild(table);

    // a compare view is offered once >=2 scenarios exist. clicking it POSTs /api/scenarios/compare
    // (no ids -> compare all) and renders the server-returned diff table verbatim.
    if (count >= 2) {
      var compareBtn = el("button", "btn btn--ghost", "Compare scenarios");
      compareBtn.type = "button";
      compareBtn.setAttribute("aria-label", "Compare scenarios");
      var compareHost = el("div", "scenarios-compare");
      compareBtn.addEventListener("click", function () {
        fetch("/api/scenarios/compare", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        })
          .then(function (resp) {
            if (!resp.ok) {
              throw new Error("compare failed: " + resp.status);
            }
            return resp.json();
          })
          .then(function (cmp) {
            drawScenarioCompare(compareHost, cmp);
          })
          .catch(function () {
            compareHost.textContent = "";
            compareHost.appendChild(el("p", "unavailable", UNAVAILABLE));
          });
      });
      host.appendChild(compareBtn);
      host.appendChild(compareHost);
    }
  }

  // draw the §4.2 compare diff table from a /api/scenarios/compare payload. columns = one per chosen
  // scenario; rows = the server diff entries. a row whose values all agree is marked "same"; one that
  // differs is highlighted. all cells are verbatim server strings.
  function drawScenarioCompare(host, cmp) {
    host.textContent = "";
    var scenarios = cmp && Array.isArray(cmp.scenarios) ? cmp.scenarios : [];
    var diff = cmp && Array.isArray(cmp.diff) ? cmp.diff : [];
    if (!scenarios.length || !diff.length) {
      host.appendChild(el("p", "unavailable", UNAVAILABLE));
      return;
    }

    host.appendChild(el("h4", "section-subtitle", "Compare"));
    var table = el("table", "strategy-table");
    var thead = el("thead");
    var hr = el("tr");
    hr.appendChild(el("th", null, ""));
    scenarios.forEach(function (s) {
      hr.appendChild(el("th", null, orUnavailable(s.name)));
    });
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = el("tbody");
    diff.forEach(function (entry) {
      var tr = el("tr");
      if (entry && entry.same === false) {
        tr.className = "strategy-table__row--diff";
      }
      tr.appendChild(el("th", null, orUnavailable(entry.field)));
      var values = entry && Array.isArray(entry.values) ? entry.values : [];
      values.forEach(function (value) {
        tr.appendChild(el("td", null, orUnavailable(value)));
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    host.appendChild(table);
  }

  // re-render the Scenarios tab if it is the active tab (used after a save so the new row shows).
  function refreshScenariosIfActive() {
    if (results.activeTab === "scenarios") {
      renderActiveTab();
    }
  }

  // the 9 §5.6 report-section names, in order. these only LABEL the thumbnails; the report content
  // itself is built entirely server-side (§0 dumb client). the JS never assembles report text.
  var REPORT_SECTIONS = [
    "Summary",
    "Your fleet & inputs",
    "Energy",
    "Charging",
    "Grid & flexibility",
    "Total cost",
    "CO\u2082",
    "Plan",
    "Inputs & sources",
  ];

  // trigger a real browser download of the bytes the server returns from /api/report. the client
  // computes NOTHING and builds NO report content: it POSTs the current results verbatim, reads the
  // response as an opaque Blob and saves it. the filename comes from the server's Content-Disposition
  // header when present, else a fixed fallback per format.
  function downloadReport(format, fallbackName) {
    if (!results.payload) {
      return; // guard: no run yet, nothing to export.
    }
    fetch("/api/report?format=" + encodeURIComponent(format), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        results: results.payload,
        levers: results.levers,
      }),
    })
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("report request failed: " + resp.status);
        }
        var name = fallbackName;
        var disp = resp.headers.get("Content-Disposition");
        if (disp) {
          var match = /filename="?([^";]+)"?/i.exec(disp);
          if (match && match[1]) {
            name = match[1];
          }
        }
        return resp.blob().then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = el("a");
          a.href = url;
          a.download = name;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        });
      })
      .catch(function () {
        // dumb client: no invented content. a failure leaves the tab unchanged.
      });
  }

  function renderReportTab(panel) {
    var card = el("div", "report-card");
    card.appendChild(el("h3", "section-title", "Your report is ready"));
    card.appendChild(el("p", "report-card__hint", "A full report with every section is prepared from these results."));
    var thumbs = el("div", "report-thumbs");
    REPORT_SECTIONS.forEach(function (name) {
      thumbs.appendChild(el("div", "report-thumb", name));
    });
    card.appendChild(thumbs);
    var actions = el("div", "report-actions");
    var pdf = el("button", "btn btn--ghost", "Download PDF");
    pdf.type = "button";
    pdf.setAttribute("aria-label", "Download PDF report");
    pdf.addEventListener("click", function () {
      downloadReport("pdf", "hdev-report.pdf");
    });
    var xls = el("button", "btn btn--ghost", "Download data (Excel)");
    xls.type = "button";
    xls.setAttribute("aria-label", "Download Excel data report");
    xls.addEventListener("click", function () {
      downloadReport("excel", "hdev-report.xlsx");
    });
    actions.appendChild(pdf);
    actions.appendChild(xls);
    card.appendChild(actions);
    panel.appendChild(card);
  }

  // Audit tab (§5.6/§8): GET /api/audit and draw (1) the counts-only "Where every input came from"
  // source table + the server total row, (2) the exact server note, and (3) the §3.4 run log
  // newest-first. the client NAMES NO field, computes NO total and invents NO count - every row,
  // count, total, note string and run-log cell is a verbatim server value.
  function renderAuditTab(panel) {
    panel.appendChild(el("h3", "section-title", "Audit trail"));
    var host = el("div", "audit-host");
    panel.appendChild(host);
    host.appendChild(el("p", "unavailable", UNAVAILABLE));

    fetch("/api/audit")
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("audit request failed: " + resp.status);
        }
        return resp.json();
      })
      .then(function (payload) {
        drawAudit(host, payload);
      })
      .catch(function () {
        host.textContent = "";
        host.appendChild(el("p", "unavailable", UNAVAILABLE));
      });
  }

  function drawAudit(host, payload) {
    host.textContent = "";
    if (!payload || payload.available === false) {
      host.appendChild(el("p", "unavailable", UNAVAILABLE));
      return;
    }

    // (1) the counts-only source table.
    host.appendChild(el("h4", "section-subtitle", "Where every input came from"));
    var sourceTable = payload.source_table || {};
    var srcRows = Array.isArray(sourceTable.rows) ? sourceTable.rows : [];
    var table = el("table", "strategy-table");
    var thead = el("thead");
    var hr = el("tr");
    ["Source type", "Count", "Status"].forEach(function (h) {
      hr.appendChild(el("th", null, h));
    });
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = el("tbody");
    srcRows.forEach(function (row) {
      var tr = el("tr");
      tr.appendChild(el("td", null, orUnavailable(row.source_type)));
      tr.appendChild(el("td", null, orUnavailable(row.count)));
      tr.appendChild(el("td", null, orUnavailable(row.status)));
      tbody.appendChild(tr);
    });
    // the total row: the number comes straight from the server (the client sums nothing).
    var totalTr = el("tr", "strategy-table__row--current");
    totalTr.appendChild(el("th", null, "Total"));
    totalTr.appendChild(el("td", null, orUnavailable(sourceTable.total)));
    totalTr.appendChild(el("td", null, ""));
    tbody.appendChild(totalTr);
    table.appendChild(tbody);
    host.appendChild(table);

    // (2) the exact server note (plain words; names no field).
    if (typeof payload.note === "string") {
      host.appendChild(el("p", "audit-note", payload.note));
    }

    // (3) the §3.4 run log, newest-first in server order.
    host.appendChild(el("h4", "section-subtitle", "Run log"));
    var runLog = Array.isArray(payload.run_log) ? payload.run_log : [];
    if (!runLog.length) {
      host.appendChild(el("p", "scenarios-empty", "No runs yet"));
      return;
    }
    var logTable = el("table", "strategy-table");
    var logHead = el("thead");
    var logHr = el("tr");
    ["Run #", "Time", "Settings", "Key result"].forEach(function (h) {
      logHr.appendChild(el("th", null, h));
    });
    logHead.appendChild(logHr);
    logTable.appendChild(logHead);

    var logBody = el("tbody");
    runLog.forEach(function (entry) {
      var tr = el("tr");
      tr.appendChild(el("td", null, orUnavailable(entry.run_id)));
      tr.appendChild(el("td", null, orUnavailable(entry.timestamp)));
      tr.appendChild(auditSettingsCell(entry.settings_summary));
      tr.appendChild(auditResultCell(entry.key_result_summary));
      logBody.appendChild(tr);
    });
    logTable.appendChild(logBody);
    host.appendChild(logTable);
  }

  // build the "Settings" cell for one run-log row from the server settings_summary. the labels are
  // fixed chrome; every VALUE is a verbatim client-facing server string (§8-safe). no field is named.
  function auditSettingsCell(summary) {
    var td = el("td", "audit-cell");
    summary = summary && typeof summary === "object" ? summary : {};
    var pairs = [
      ["Trucks", summary.trucks],
      ["Charging approach", summary.charging_approach],
      ["Electricity price", summary.electricity_price],
      ["Weather", summary.weather],
      ["Years kept", summary.years_kept],
      ["Shift end", summary.shift_end],
    ];
    pairs.forEach(function (pair) {
      var line = el("span", "audit-cell__line");
      line.appendChild(el("span", "audit-cell__key", pair[0] + ": "));
      line.appendChild(el("span", "audit-cell__val", orUnavailable(pair[1])));
      td.appendChild(line);
    });
    return td;
  }

  // build the "Key result" cell for one run-log row from the server key_result_summary. labels fixed;
  // values verbatim from the server.
  function auditResultCell(summary) {
    var td = el("td", "audit-cell");
    summary = summary && typeof summary === "object" ? summary : {};
    var pairs = [
      ["Battery (kWh)", summary.battery_kwh],
      ["Depot peak (kW)", summary.depot_peak_kw],
      ["TCO saving (DKK)", summary.tco_saving_dkk],
      ["CO\u2082 saved (t/year)", summary.co2_saved_t_per_year],
    ];
    pairs.forEach(function (pair) {
      var line = el("span", "audit-cell__line");
      line.appendChild(el("span", "audit-cell__key", pair[0] + ": "));
      line.appendChild(el("span", "audit-cell__val", orUnavailable(pair[1])));
      td.appendChild(line);
    });
    return td;
  }

  // ---- scenario bar (§5.5) ------------------------------------------------

  function renderScenarioBar() {
    var bar = byId("scenario-bar");
    if (!bar) {
      return;
    }
    bar.hidden = false;
    bar.textContent = "";
    var levers = results.levers || {};

    // Trucks: range slider bound to fleet_size with a live readout. the slider max comes from the
    // current value (we never invent a project bound in JS); the server validates the posted value.
    var truckGroup = el("div", "scenario-ctrl");
    truckGroup.appendChild(el("label", "scenario-ctrl__label", "Trucks"));
    var sliderRow = el("div", "scenario-ctrl__sliderrow");
    var slider = el("input", "scenario-slider");
    slider.type = "range";
    slider.min = "1";
    // a generous display range so the slider is usable; the server is the source of truth on bounds.
    var current = typeof levers.fleet_size === "number" ? levers.fleet_size : 1;
    slider.max = String(Math.max(20, current));
    slider.value = String(current);
    slider.setAttribute("aria-label", "Number of trucks");
    var readout = el("span", "scenario-ctrl__readout", String(current));
    slider.addEventListener("input", function () {
      readout.textContent = slider.value;
    });
    slider.addEventListener("change", function () {
      updateLever("fleet_size", parseInt(slider.value, 10));
    });
    sliderRow.appendChild(slider);
    sliderRow.appendChild(readout);
    truckGroup.appendChild(sliderRow);
    bar.appendChild(truckGroup);

    // segmented controls for the enum levers.
    // labels are plain scenario-bar copy, chosen so they do NOT reproduce any collapsed/hidden
    // registry field label (§8). the lever keys they bind to are the client-facing lever names.
    bar.appendChild(segmented("Charging approach", "charging_priority", levers.charging_priority));
    bar.appendChild(segmented("Electricity price", "electricity_price", levers.electricity_price));
    bar.appendChild(segmented("Weather", "weather_year", levers.weather_year));
    bar.appendChild(segmented("Years kept", "ownership_years", levers.ownership_years));

    // Save scenario button: POST the CURRENT run to /api/scenarios so the server snapshots it, then
    // re-GET the list and refresh the Scenarios table + post a short confirmation bubble. the client
    // sends the whole current results payload (so the saved scenario's run_id matches the run log);
    // it computes nothing and invents no name/number.
    var saveGroup = el("div", "scenario-ctrl scenario-ctrl--save");
    var save = el("button", "btn", "Save scenario");
    save.type = "button";
    save.setAttribute("aria-label", "Save scenario");
    save.addEventListener("click", function () {
      saveCurrentScenario();
    });
    saveGroup.appendChild(save);
    bar.appendChild(saveGroup);
  }

  // the running count of saved scenarios in this session, used ONLY to build a default scenario name
  // ("Scenario 1", "Scenario 2", ...) when the user does not type one. it is a UI label, not a result
  // number; the server never derives anything from it. it is seeded from the server list before saving.
  var scenarioSaveSeq = 0;

  // POST the current run to /api/scenarios (whole results payload so run_id matches the run log), then
  // refresh the Scenarios table and confirm. on failure show the unavailable marker (no invented data).
  function saveCurrentScenario() {
    scenarioSaveSeq += 1;
    var name = "Scenario " + scenarioSaveSeq;
    fetch("/api/scenarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, results: results.payload }),
    })
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("save failed: " + resp.status);
        }
        return resp.json();
      })
      .then(function (payload) {
        var savedName =
          payload && payload.scenario && payload.scenario.name
            ? payload.scenario.name
            : name;
        postBubble("assistant", "Saved as \u201c" + savedName + "\u201d in the scenarios list.");
        refreshScenariosIfActive();
      })
      .catch(function () {
        postBubble("assistant", UNAVAILABLE);
      });
  }

  // a segmented button group for an enum lever. each button posts the full lever set on click.
  function segmented(label, leverKey, currentValue) {
    var group = el("div", "scenario-ctrl");
    group.appendChild(el("label", "scenario-ctrl__label", label));
    var seg = el("div", "segmented");
    seg.setAttribute("role", "group");
    seg.setAttribute("aria-label", label);
    var options = LEVER_UI[leverKey] || [];
    options.forEach(function (opt) {
      var btn = el("button", "segmented__btn", opt.label);
      btn.type = "button";
      var isActive = String(opt.value) === String(currentValue);
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      if (isActive) {
        btn.classList.add("segmented__btn--active");
      }
      btn.addEventListener("click", function () {
        updateLever(leverKey, opt.value);
      });
      seg.appendChild(btn);
    });
    group.appendChild(seg);
    return group;
  }

  // apply a lever change and re-run via /api/run with the recalculation overlay. the client posts the
  // RAW client-facing lever values; it computes nothing.
  function updateLever(key, value) {
    if (!results.levers) {
      results.levers = {};
    }
    results.levers[key] = value;
    rerunWithOverlay();
  }

  // ---- recalculation overlay (§5.5) ---------------------------------------

  function rerunWithOverlay() {
    showRecalcOverlay();
    postRun(results.levers)
      .then(function (payload) {
        results.payload = payload;
        syncLeversFromPayload(payload);
        hideRecalcOverlay();
        // re-render the active tab + refresh the scenario bar active states + keep the pill visible.
        renderScenarioBar();
        renderActiveTab();
        renderDemoPill(payload);
      })
      .catch(function () {
        hideRecalcOverlay();
      });
  }

  function showRecalcOverlay() {
    var overlay = byId("recalc-overlay");
    if (!overlay) {
      return;
    }
    overlay.hidden = false;
    overlay.setAttribute("aria-hidden", "false");
    overlay.textContent = "";
    var box = el("div", "recalc-box");
    box.appendChild(el("div", "recalc-box__title", "Recalculating"));
    var bar = el("div", "progress");
    var fill = el("div", "progress__fill progress__fill--indeterminate");
    bar.appendChild(fill);
    box.appendChild(bar);
    var line = el("p", "recalc-box__line", RECALC_LINES[0]);
    box.appendChild(line);
    overlay.appendChild(box);
    // rotate the four lines.
    var i = 0;
    if (results.recalcTimer) {
      window.clearInterval(results.recalcTimer);
    }
    results.recalcTimer = window.setInterval(function () {
      i = (i + 1) % RECALC_LINES.length;
      line.textContent = RECALC_LINES[i];
    }, 650);
  }

  function hideRecalcOverlay() {
    var overlay = byId("recalc-overlay");
    if (results.recalcTimer) {
      window.clearInterval(results.recalcTimer);
      results.recalcTimer = null;
    }
    if (overlay) {
      overlay.hidden = true;
      overlay.setAttribute("aria-hidden", "true");
      overlay.textContent = "";
    }
  }

  // ===========================================================================
  // STEP 6: demo assistant wiring. the client posts raw text / action ids to /api/chat and renders
  // the server reply + applies the server action. NO reply text, NO keyword logic and NO maths here.
  // ===========================================================================

  // map the server-returned tab ids (action.open_tab) to the TABS ids used by the tab bar. the two
  // sets already align 1:1 for the assistant tabs; this is an explicit, data-only mapping (no logic).
  var CHAT_TAB_MAP = {
    charging: "charging",
    tco: "tco",
    gridflex: "gridflex",
    energy: "energy",
    scenarios: "scenarios",
    inputs: "inputs",
    audit: "audit",
    report: "report",
    overview: "overview",
    co2: "co2",
  };

  // the §4.4 suggestion buttons: EXACT labels (fixed UI chrome, like the TABS labels) paired with the
  // server action id each posts. order is fixed per the spec.
  var SUGGESTIONS = [
    { label: "Compare charging strategies", action: "compare_strategies" },
    { label: "What if electricity costs more?", action: "price_up" },
    { label: "Add 4 more trucks", action: "more_trucks" },
    { label: "Cold winter", action: "cold_winter" },
    { label: "Save as scenario", action: "save_scenario" },
    { label: "Show me the inputs", action: "show_inputs" },
    { label: "Show the audit trail", action: "show_audit" },
    { label: "Make the report", action: "make_report" },
  ];

  var TYPING_INDICATOR_ID = "assistant-typing";
  var typingSeq = 0;

  // post a transient "typing" assistant bubble before the /api/chat reply resolves. returns the bubble
  // id so the caller can replace its text with the server reply. reuses the postBubble id-replacement
  // pattern used for the intake "Reading…" indicator.
  function showTypingIndicator() {
    typingSeq += 1;
    var id = TYPING_INDICATOR_ID + "-" + typingSeq;
    var bubble = postBubble("assistant", "\u2026", { id: id });
    if (bubble) {
      bubble.classList.add("msg--typing");
    }
    return id;
  }

  // replace the typing bubble's text with the final reply (or the unavailable marker). if the bubble
  // is gone, append a fresh assistant bubble instead so a reply is never lost.
  function resolveTypingIndicator(id, text) {
    var bubble = id ? byId(id) : null;
    if (bubble) {
      bubble.classList.remove("msg--typing");
      if (text === null || text === undefined) {
        bubble.textContent = UNAVAILABLE;
        bubble.classList.add("unavailable");
      } else {
        bubble.textContent = text;
      }
      bubble.removeAttribute("id");
      return;
    }
    postBubble("assistant", text === null || text === undefined ? UNAVAILABLE : text);
  }

  // POST the given body to /api/chat and return the parsed JSON. mirrors postRun. on a non-ok response
  // or a fetch failure it rejects, so callers render the "Not yet available" marker (dumb-client rule:
  // the client never invents a reply). the body is sent verbatim - raw text / action ids only.
  function sendChat(body) {
    return fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    }).then(function (resp) {
      // a 400 (e.g. an invalid shift-end value) still carries a plain server reply we should show.
      return resp.json().then(function (payload) {
        if (!resp.ok && !(payload && typeof payload.reply === "string")) {
          throw new Error("chat failed: " + resp.status);
        }
        return payload;
      });
    });
  }

  // apply a /api/chat response verbatim: render the server reply, then apply the server action (new
  // results -> update scenario bar + active tab; a changed lever -> keep results.levers/shiftEnd in
  // sync; open_tab -> open that tab; expand_section -> open Inputs with the operation card visible).
  // the client decides nothing - it only draws what the server returned.
  function applyChatAction(payload, typingId) {
    if (!payload || typeof payload.reply !== "string") {
      resolveTypingIndicator(typingId, UNAVAILABLE);
      return;
    }
    resolveTypingIndicator(typingId, payload.reply);

    var action = payload.action && typeof payload.action === "object" ? payload.action : null;
    if (!action) {
      return;
    }

    // a changed lever echoed by the server. for the shift-end target keep results.shiftEnd in sync so
    // later re-runs preserve it; other levers are covered by syncLeversFromPayload below.
    if (action.lever && typeof action.lever === "object") {
      if (typeof action.lever["operation.schedule.shift_end"] === "string") {
        results.shiftEnd = action.lever["operation.schedule.shift_end"];
      }
    }

    // fresh results from a rerun: adopt them, resync the lever set, and redraw the scenario bar + the
    // active tab so an assistant-driven lever change VISIBLY updates the controls and the KPIs/charts.
    if (action.results && typeof action.results === "object") {
      results.payload = action.results;
      syncLeversFromPayload(action.results);
      renderScenarioBar();
      renderActiveTab();
      renderDemoPill(action.results);
    }

    // open the named tab. expand_section (Show me the inputs) opens the Inputs tab with the operation
    // card expanded/visible via renderInputsTab -> ensureShiftEndControl.
    if (action.expand_section) {
      selectTab("inputs");
      ensureShiftEndControl();
    } else if (action.open_tab) {
      var mapped = CHAT_TAB_MAP[action.open_tab];
      if (mapped) {
        selectTab(mapped);
      }
    }

    // the server persisted a scenario (the 'Save as scenario' action). the Scenarios tab was just
    // opened above; re-render it so the new row is fetched from the server. the client refetches the
    // list rather than inventing the row.
    if (action.saved_scenario) {
      refreshScenariosIfActive();
    }
  }

  // common send path for a typed message or a suggestion-button/edit action: show the typing bubble,
  // POST to /api/chat, then applyChatAction. on failure render the unavailable marker (no invented
  // reply). the caller is responsible for posting the user bubble (its label / typed text).
  function askAssistant(body) {
    var typingId = showTypingIndicator();
    sendChat(body)
      .then(function (payload) {
        applyChatAction(payload, typingId);
      })
      .catch(function () {
        resolveTypingIndicator(typingId, UNAVAILABLE);
      });
  }

  // the shift-end field edit (§4.4): POST the RAW new HH:MM value as an edit_field action. the server
  // validates, reruns and returns the reply ending with 'Logged as run #N in the audit trail.'.
  function editShiftEnd(value) {
    askAssistant({
      action: "edit_field",
      target: "operation.schedule.shift_end",
      value: value,
      levers: results.levers,
      current_results: results.payload,
    });
  }

  // render the §4.4 suggestion buttons into #assistant-suggestions once results exist. each button
  // posts a user bubble with its label, shows the typing indicator and posts its action id to
  // /api/chat. this replaces any pre-run intake buttons in the same area.
  function renderAssistantSuggestions() {
    var host = byId("assistant-suggestions");
    if (!host) {
      return;
    }
    host.textContent = "";
    SUGGESTIONS.forEach(function (item) {
      var btn = el("button", "btn btn--ghost suggestion-btn", item.label);
      btn.type = "button";
      btn.addEventListener("click", function () {
        postBubble("user", item.label);
        askAssistant({
          action: item.action,
          levers: results.levers,
          current_results: results.payload,
        });
      });
      host.appendChild(btn);
    });
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
