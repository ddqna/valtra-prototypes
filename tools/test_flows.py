#!/usr/bin/env python3
"""Click through both prototype flows in a headless browser.

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
        # The sandbox may not reach Google Fonts; skip them so pages load fast (system font fallback).
        page.route(lambda u: "fonts.googleapis" in u or "fonts.gstatic" in u, lambda r: r.abort())
        expect.set_options(timeout=4000)

        def at(name):
            page.wait_for_url(f"**/{name}", wait_until="domcontentloaded")
            page.wait_for_selector("#dc-stage > *")
            if SAVE:
                SHOTS.mkdir(exist_ok=True)
                page.screenshot(path=str(SHOTS / f"{len(passed):02d}-{name.replace('.html', '')}.png"))

        def step(label):
            passed.append(label)
            print("  ok ", label)

        def click(text, role="link", exact=False):
            page.get_by_role(role, name=text, exact=exact).first.click()

        def see(text):
            expect(page.get_by_text(text, exact=False).first).to_be_visible()

        # ---------- Prototype A ----------
        print("Prototype A — Skill Tree")
        page.goto(base + "/index.html"); at("index.html"); step("launcher loads")
        click("Start from tractor screen"); at("A0-Home.html"); step("launcher -> A0")
        click("Hitch", "button"); see("isn't part of this prototype"); click("OK", "button")
        expect(page.get_by_text("isn't part of this prototype")).to_have_count(0); step("A0 other functions show + dismiss notice")
        click("Help & learn"); at("A1-Explore.html"); step("A0 Help & learn -> A1")
        click("Field guidance", "button"); see("No content for"); click("OK", "button"); step("A1 other category shows notice")
        click("Back to tractor"); at("A0-Home.html"); click("Help & learn"); at("A1-Explore.html"); step("A1 Back to tractor -> A0")
        page.locator("a.node").click(); at("A2-Learn.html"); step("A1 Headland management -> A2")
        click("More information", "button"); see("full instructions"); click("Back to overview", "button"); see("How it works"); step("A2 More information toggles")
        click("Back to Skill Tree"); at("A1-Explore.html"); page.locator("a.node").click(); at("A2-Learn.html"); step("A2 Back to Skill Tree -> A1")
        click("Try guided practice"); at("A3-Practice.html"); see("Step 1 of 3"); step("A2 Try guided practice -> A3")
        expect(page.get_by_role("button", name="Continue")).to_be_disabled(); step("A3 Continue disabled before choosing")
        click("Guidance line setup", "button"); see("Another possibility — suggested: Headland sequence"); step("A3 non-suggested answer feedback")
        click("Headland sequence", "button"); see("Suggested answer"); see("SUGGESTED"); step("A3 suggested answer feedback")
        click("Continue", "button"); see("Step 2 of 3"); click("Previous step", "button"); see("Step 1 of 3"); see("Suggested answer"); step("A3 Previous step keeps answer")
        click("Continue", "button"); click("Review the recorded steps for today's implement", "button"); see("Suggested answer"); click("Continue", "button")
        see("Step 3 of 3"); see("Simplified screen preview"); step("A3 step 2 -> step 3")
        click("PTO", "button"); see("Another possibility"); click("Headland", "button", exact=True); see("Suggested answer"); step("A3 tap step feedback")
        click("Finish practice"); at("A4-Complete.html"); see("You've completed a guided introduction to headland sequences."); step("A3 Finish practice -> A4")
        tog = page.locator("button.toggle"); tog.click(); expect(tog).to_have_attribute("aria-pressed", "true"); tog.click(); expect(tog).to_have_attribute("aria-pressed", "false"); step("A4 reminder toggle")
        click("Review instructions"); at("A2-Learn.html"); page.go_back(); at("A4-Complete.html"); step("A4 Review instructions -> A2")
        click("Explore more skills"); at("A1-Explore.html"); page.go_back(); at("A4-Complete.html"); step("A4 Explore more skills -> A1")
        click("Return to task"); at("A0-Home.html"); step("A4 Return to task -> A0")
        page.goto(base + "/A3-Practice.html"); at("A3-Practice.html")
        click("Skip step", "button"); see("Step 2 of 3"); click("Skip step", "button"); see("Step 3 of 3"); click("Skip & finish"); at("A4-Complete.html"); step("A3 skip path -> A4")
        page.goto(base + "/A3-Practice.html"); at("A3-Practice.html"); click("Exit practice"); at("A2-Learn.html"); step("A3 Exit practice -> A2")
        click("Prototype menu"); at("index.html"); step("Prototype menu -> launcher")

        # ---------- Prototype B ----------
        print("Prototype B — Explain & Recover")
        click("Start from task screen"); at("B1-Task.html"); see("Sequence “Field edge A”"); step("launcher -> B1")
        click("Help", exact=True); at("B2-Confirm.html"); page.go_back(); at("B1-Task.html"); step("B1 top-bar Help -> B2")
        click("Help with this task"); at("B2-Confirm.html"); see("What isn't working as expected?"); step("B1 Help with this task -> B2")
        click("Something else", "button"); see("What's happening instead?")
        click("I don't understand a message on the screen", "button"); see("This path isn't built in the prototype yet"); step("B2 Something else -> correction + placeholder")
        click("Back to suggested issue", "button"); see("What isn't working as expected?"); step("B2 back to suggested issue")
        click("Back to task"); at("B1-Task.html"); click("Help with this task"); at("B2-Confirm.html"); step("B2 Back to task -> B1")
        click("Yes, that's the issue"); at("B3-Checks.html"); see("0 of 3 checked"); step("B2 confirm -> B3")
        page.get_by_role("button", name="I've checked this").first.click(); see("1 of 3 checked"); see("Checked")
        page.get_by_role("button", name="Checked").first.click(); see("0 of 3 checked"); step("B3 check toggles + counter")
        page.get_by_role("button", name="Why check this?").nth(1).click(); see("[Insert a short reason from verified documentation.]")
        expect(page.get_by_role("button", name="Why check this?").nth(1)).to_have_attribute("aria-expanded", "true"); step("B3 Why check this? expands")
        click("Change"); at("B2-Confirm.html"); page.go_back(); at("B3-Checks.html"); step("B3 Change -> B2")
        click("Still need help"); at("B4-Resolve.html"); page.go_back(); at("B3-Checks.html"); step("B3 Still need help -> B4")
        click("Continue"); at("B4-Resolve.html"); see("Did this help resolve the issue?"); step("B3 Continue -> B4")
        page.locator("button.big").click(); see("Let's find more help"); step("B4 No -> escalation panel")
        click("Contact support", "button"); see("No contact details in this prototype"); step("B4 support option shows placeholder")
        click("Back to checks"); at("B3-Checks.html"); page.go_back(); at("B4-Resolve.html"); step("B4 Back to checks -> B3")
        page.locator("button.big").click(); click("Return to task"); at("B1-Task.html"); step("B4 escalation Return to task -> B1")
        page.goto(base + "/B4-Resolve.html"); at("B4-Resolve.html"); page.locator("a.big-yes").click(); at("B1-Task.html"); step("B4 Yes -> B1")

        # Every link on every page points at an existing page
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
