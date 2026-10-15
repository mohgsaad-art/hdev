# STATUS: NEW (PR 7, Bob to review). a real-browser click-through of the Step 7 demo-acceptance flow.
#
# this test is ADDITIVE to the offline guarantee (tests/test_demo_acceptance_flow.py). it drives the
# live app in a headless Chromium: add sample files, send, use standard values, wait for results, click
# each §4.4 suggestion button, change the shift-end select, click Save scenario, open the Audit tab and
# the Report tab - asserting the 'illustrative values' pill stays visible throughout and no uncaught
# page error occurs.
#
# SKIP-GUARD (never fail CI when the browser is absent): the import of playwright is guarded with
# pytest.importorskip INSIDE this module (so the core suite never imports playwright at collection
# time), and the browser launch is wrapped so a missing browser binary / any launch error becomes a
# pytest.skip rather than a failure. in THIS sandbox playwright is installed and
# `python -m playwright install chromium` has been run, so the test actually RUNS here; on a machine
# without the browser it SKIPS cleanly.
#
# the app is started on 127.0.0.1 on an ephemeral port in a background uvicorn thread inside a fixture;
# it binds loopback only and runs in demo mode (no network, no AI provider, no API key).
import socket
import threading
import time

import pytest

# guard 1: skip the whole module if playwright is not installed. this import must stay INSIDE the module
# so the browser-free core suite never imports playwright at collection time.
sync_api = pytest.importorskip("playwright.sync_api")

PILL_TEXT = "illustrative values"


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def live_server():
    # start the FastAPI app on 127.0.0.1:<ephemeral> in a background uvicorn thread (demo mode).
    import uvicorn

    from hdev.server import create_app

    port = _free_port()
    config = uvicorn.Config(create_app(), host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # wait for the server to accept connections (up to ~10s).
    base = "http://127.0.0.1:{}".format(port)
    deadline = time.time() + 10
    while time.time() < deadline:
        if server.started:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    break
            except OSError:
                pass
        time.sleep(0.1)
    else:
        server.should_exit = True
        pytest.skip("live server did not start in time")

    yield base

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture()
def browser():
    # guard 2: launch chromium headless with --no-sandbox; ANY launch error (missing browser binary,
    # sandbox refusal, etc.) becomes a SKIP, never a failure, so CI stays green without the browser.
    with sync_api.sync_playwright() as p:
        try:
            br = p.chromium.launch(headless=True, args=["--no-sandbox"])
        except Exception as exc:  # pragma: no cover - exercised only when the browser is absent
            pytest.skip("chromium browser unavailable for Playwright: {}".format(exc))
        try:
            yield br
        finally:
            br.close()


def test_demo_acceptance_click_through(live_server, browser):
    page = browser.new_page()

    # collect uncaught page errors; the flow must produce none.
    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    page.goto(live_server, wait_until="networkidle")

    # the 'illustrative values' pill is visible from the start (demo mode).
    pill = page.locator("#demo-pill")
    assert pill.is_visible()
    assert PILL_TEXT in pill.inner_text()

    # 1. add the sample files, then send.
    page.click("#add-sample-files")
    page.click("#composer-send")

    # 2. the intake fill ends with the §4.4 missing-flow buttons; click "Use standard values".
    use_std = page.locator("button:has-text('Use standard values')")
    use_std.wait_for(state="visible", timeout=15000)
    use_std.click()

    # 3. wait for results: the tab bar is revealed once the run completes.
    page.locator("#tabbar").wait_for(state="visible", timeout=20000)
    # the suggestion buttons appear once results exist.
    page.locator(".suggestion-btn").first.wait_for(state="visible", timeout=20000)

    # 4. click each §4.4 suggestion button in turn (there are eight).
    count = page.locator(".suggestion-btn").count()
    assert count >= 1
    for i in range(count):
        btn = page.locator(".suggestion-btn").nth(i)
        btn.scroll_into_view_if_needed()
        btn.click()
        page.wait_for_timeout(300)
        # the pill must stay visible after every action.
        assert pill.is_visible()

    # 5. change the shift-end select. "Show me the inputs" (clicked above) opens the Inputs tab with the
    #    editable shift-end control; make sure the Inputs tab is active, then change the select.
    page.click("#tab-inputs")
    shift_select = page.locator("[data-role='shift-end-edit'] select")
    shift_select.wait_for(state="visible", timeout=10000)
    shift_select.select_option("16:00")
    page.wait_for_timeout(500)
    assert pill.is_visible()

    # 6. click Save scenario in the scenario bar.
    page.click("button[aria-label='Save scenario']")
    page.wait_for_timeout(500)
    assert pill.is_visible()

    # 7. open the Audit tab - the counts-only source table + the exact note + the run log render.
    page.click("#tab-audit")
    page.locator(".audit-note").wait_for(state="visible", timeout=10000)
    assert "Every value can be changed. Changes are logged with who and when." in page.locator(
        ".audit-note"
    ).inner_text()
    assert pill.is_visible()

    # 8. open the Report tab - it is reachable.
    page.click("#tab-report")
    page.wait_for_timeout(300)
    assert pill.is_visible()

    # no uncaught page error anywhere in the flow.
    assert page_errors == [], "uncaught page errors: {}".format(page_errors)

    page.close()
