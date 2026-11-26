#!/usr/bin/env python3
"""Click through the Skill Tree demo flow in a headless browser.

    python3 tools/build_standalone.py
    python3 tools/test_flows.py            # add --shots to save screenshots to tools/shots/

Needs: pip install playwright && playwright install chromium (or a local Chrome).
"""
import functools
import http.server
import pathlib
import sys
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SHOTS = ROOT / "tools" / "shots"
SAVE = "--shots" in sys.argv


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(DOCS))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def main():
    httpd, base = serve()
    errors, passed = [], []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(f"{page.url}: {e}"))
        page.on("console", lambda m: m.type == "error" and "fonts.g" not in (m.location or {}).get("url", "") + m.text and errors.append(f"{page.url}: {m.text}"))
        # Google Fonts may be unreachable in CI/sandboxes; skip them (system font fallback).
        page.route(lambda u: "fonts.googleapis" in u or "fonts.gstatic" in u, lambda r: r.abort())
        expect.set_options(timeout=4000)

        def at(name):
            page.wait_for_url(f"**/{name}", wait_until="domcontentloaded")
            page.wait_for_selector("#dc-stage > *")
            if SAVE:
                SHOTS.mkdir(exist_ok=True)
                page.screenshot(path=str(SHOTS / f"{len(passed):02d}-{name.replace('/', '_').replace('.html', '')}.png"))

        def step(label):
            passed.append(label)
            print("  ok ", label)

        def btn(name, exact=True):
            return page.get_by_role("button", name=name, exact=exact).first

        def link(name, exact=False):
            return page.get_by_role("link", name=name, exact=exact).first

        def see(text):
            expect(page.get_by_text(text, exact=False).first).to_be_visible()

        def gone(text):
            expect(page.get_by_text(text, exact=False)).to_have_count(0)

        print("Skill Tree demo flow")
        page.goto(base + "/index.html"); at("index.html"); step("launcher loads")
        expect(link("Start demo")).to_have_attribute("class", "btn btn-primary nudge"); step("launcher hint on Start demo")
        link("Start demo").click(); at("A0-Home.html"); step("launcher -> tractor screen")

        expect(page.locator("#dc-stage img").first).to_be_visible()
        assert page.evaluate("document.querySelector('#dc-stage img').naturalWidth") > 0, "tractor image did not load"
        step("tractor image loads")

        # Normal mode: controls behave normally (prototype notice); Help is hinted
        expect(btn("Help")).to_have_attribute("class", "helpbtn nudge"); step("hint on Help")
        btn("Display").click(); see("isn't part of this prototype"); btn("OK").click(); gone("isn't part of this prototype"); step("normal mode: control shows prototype notice")

        # Help mode
        btn("Help").click(); see("Tap any control to see what it does"); see("Controls are paused"); expect(btn("Exit help")).to_be_visible(); step("Help mode opens; screen stays; controls paused")
        expect(page.locator("#dc-stage .side .ring.nudge")).to_have_count(1); step("hint moves to Headland control")
        btn("Front PTO").click(); expect(page.get_by_role("dialog")).to_be_visible(); see("Control not activated"); gone("isn't part of this prototype"); step("tap image control in Help: card, no activation")
        btn("QR code").click(); expect(page.locator("svg[aria-label='Placeholder QR code']")).to_be_visible(); expect(btn("QR code")).to_have_attribute("aria-pressed", "true"); step("QR code shows")
        btn("More info").click(); expect(btn("More info")).to_have_attribute("aria-pressed", "true"); step("More info toggles")
        see("No learning path for this control"); link("Learn", exact=True).click(); at("A1-Explore.html"); step("Learn without a path -> Skill Tree overview")
        page.go_back(); at("A0-Home.html")
        btn("Help").click(); btn("AUTO [name to verify]").click(); btn("Close help card").click(); expect(page.get_by_role("dialog")).to_have_count(0); step("close help card")
        btn("Exit help").click(); expect(btn("Help")).to_be_visible(); gone("Controls are paused"); step("Exit help restores normal screen")
        btn("Help").click(); link("Browse all skills").click(); at("A1-Explore.html"); page.go_back(); at("A0-Home.html"); step("Help mode: Browse all skills -> overview")
        btn("Help").click(); btn("Headland").click(); see("Headland management")
        learn = link("Learn", exact=True); expect(learn).to_have_attribute("class", "pbtn pbtn-learn nudge"); step("Headland card with hinted Learn")
        learn.click(); at("Path-Headland.html"); see("Opened from Help · Headland"); step("Learn -> learning path for that control")

        # Learning path screen
        link("Back to tractor").click(); at("A0-Home.html"); page.go_back(); at("Path-Headland.html"); step("path: Back to tractor")
        link("See all skills").click(); at("A1-Explore.html"); page.go_back(); at("Path-Headland.html"); step("path: See all skills")
        link("Go to practice").click(); at("A3-Practice.html"); page.go_back(); at("Path-Headland.html"); step("path: Go to practice")
        start = link("Start", exact=True); expect(start).to_have_attribute("class", "btn btn-primary nudge"); start.click(); at("A2-Learn.html"); step("path: Start -> Step 1 Understand")

        # Steps 1-3 (existing flow)
        see("Learning path · 1 Understand")
        link("Try guided practice").click(); at("A3-Practice.html"); see("Learning path · 2 Practise"); step("Step 1 -> Step 2")
        expect(btn("Headland sequence")).to_have_attribute("class", "opt nudge"); step("practice hint on suggested option")
        btn("Guidance line setup").click(); see("Another possibility"); btn("Headland sequence", exact=False).click(); see("Suggested answer")
        btn("Continue").click(); btn("Review the recorded steps for today's implement").click(); btn("Continue").click()
        see("Step 3 of 3"); btn("Headland").click(); see("Suggested answer"); step("practice questions + tap step")
        link("Finish practice").click(); at("A4-Complete.html"); see("Learning path · 3 Apply at work"); step("Step 2 -> Step 3 Apply")
        expect(link("Return to task")).to_have_attribute("class", "btn btn-primary nudge")
        link("Explore more skills").click(); at("A1-Explore.html")
        expect(page.locator("a.node")).to_have_attribute("class", "node node-sel nudge"); page.locator("a.node").click(); at("A2-Learn.html"); step("overview: hinted Headland node -> Step 1")
        page.goto(base + "/A4-Complete.html"); at("A4-Complete.html"); link("Return to task").click(); at("A0-Home.html"); step("Apply: Return to task -> tractor screen")

        # Archived v1 still opens
        page.goto(base + "/v1/index.html"); page.wait_for_selector("#dc-stage > *"); see("Adaptive Operator Companion")
        link("Start from task screen").click(); page.wait_for_url("**/v1/B1-Task.html"); page.wait_for_selector("#dc-stage > *"); step("v1 archive opens (incl. Explain & Recover)")

        # Every link on every current page points at an existing page
        for f in sorted(DOCS.glob("*.html")):
            page.goto(f"{base}/{f.name}"); page.wait_for_selector("#dc-stage > *")
            for href in page.eval_on_selector_all("#dc-stage a[href]", "els => els.map(e => e.getAttribute('href'))"):
                if not (DOCS / href).exists():
                    errors.append(f"{f.name}: broken link {href}")
        step("no broken links")
        browser.close()
    httpd.shutdown()

    print(f"\n{len(passed)} checks passed")
    if errors:
        print("ERRORS:\n  " + "\n  ".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
