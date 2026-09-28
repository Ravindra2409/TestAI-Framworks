import os
import json
import re
import time
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except ImportError:
    pass

# ╔══════════════════════════════════════════════════════════════╗
# ║  FRAMEWORK SELECTION — Change this ONE variable to switch   ║
# ║  Options: "selenium", "playwright"                          ║
# ╚══════════════════════════════════════════════════════════════╝
FRAMEWORK = "playwright"   # or "playwright"

# Load test suite JSON
with open("test_suite.json", "r", encoding="utf-8") as f:
    test_suite = json.load(f)

# Load step mappings from external file
with open("step_map.json", "r", encoding="utf-8") as f:
    step_map = json.load(f)


def normalize_step(step: str) -> str:
    normalized = step.lower().strip()
    normalized = re.sub(r"[.,;:!?]", "", normalized)
    normalized = re.sub(r"\b(a|an|the|button|field)\b", "", normalized)
    normalized = " ".join(normalized.split())
    return normalized

# ╔══════════════════════════════════════════════════════════════╗
# ║  SELENIUM IMPLEMENTATION                                    ║
# ╚══════════════════════════════════════════════════════════════╝
def run_with_selenium(test_suite, step_map):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
 
    
    driver.implicitly_wait(10)  # wait for page load
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)

    for category, cases in test_suite["test_suite"].items():
        print(f"\n--- Running {category.upper()} TEST CASES ---")
        for case in cases:
            print(f"Running {case['id']} - {case['title']}")
            for step in case["steps"]:
                normalized_step = normalize_step(step)
                mapped = step_map.get(normalized_step)
                if not mapped:
                    print(f"⚠️ No mapping found for step: {step} (normalized: {normalized_step})")
                    continue

                action = mapped.get("action")
                selector = mapped.get("selector")
                url = mapped.get("url") or selector

                try:
                    if action == "goto":
                        if url and url.startswith(("http://", "https://")):
                            print(f"Navigating to: {url}")
                            driver.get(url)
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                        else:
                            print(f"⚠️ Invalid or missing URL: {url}")
                    elif action == "fill":
                        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        element.clear()
                        element.send_keys(mapped.get("value", ""))
                    elif action == "click":
                        clickable = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        clickable.click()
                    else:
                        print(f"⚠️ Unsupported action: {action}")
                except Exception as exc:
                    print(f"❌ Selenium action failed for step '{step}': {exc}")

            print("Expected:", case["expected_result"])
            time.sleep(2)

    driver.quit()


# ╔══════════════════════════════════════════════════════════════╗
# ║  PLAYWRIGHT IMPLEMENTATION                                  ║
# ╚══════════════════════════════════════════════════════════════╝
def run_with_playwright(test_suite, step_map):
    from playwright.sync_api import sync_playwright

    normalized_step_map = {normalize_step(k): v for k, v in step_map.items()}
    default_start_url = normalized_step_map.get("open login page", {}).get("selector")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for category, cases in test_suite["test_suite"].items():
            print(f"\n--- Running {category.upper()} TEST CASES ---")
            for case in cases:
                print(f"Running {case['id']} - {case['title']}")

                if default_start_url:
                    try:
                        print(f"Navigating to start page for test case: {default_start_url}")
                        page.goto(default_start_url)
                        page.wait_for_load_state("networkidle")
                    except Exception as exc:
                        print(f"❌ Failed to navigate to start page: {exc}")
                        continue

                for step in case["steps"]:
                    normalized_step = normalize_step(step)
                    mapped = normalized_step_map.get(normalized_step)
                    if not mapped:
                        print(f"⚠️ No mapping found for step: {step} (normalized: {normalized_step})")
                        continue

                    action = mapped.get("action")
                    selector = mapped.get("selector")
                    url = mapped.get("url") or selector

                    if action == "goto":
                        if url and url.startswith(("http://", "https://")):
                            print(f"Navigating to: {url}")
                            try:
                                page.goto(url)
                                page.wait_for_load_state("networkidle")
                            except Exception as exc:
                                print(f"❌ Navigation failed for {url}: {exc}")
                        else:
                            print(f"⚠️ Invalid or missing URL: {url}")
                    elif action in ("fill", "click"):
                        try:
                            page.wait_for_selector(selector, timeout=15000)
                        except Exception as exc:
                            print(f"❌ Playwright selector wait failed for '{selector}': {exc}")
                            continue

                        try:
                            if action == "fill":
                                page.fill(selector, mapped.get("value", ""))
                            else:
                                page.click(selector)
                        except Exception as exc:
                            print(f"❌ Playwright action failed for '{action}' on '{selector}': {exc}")
                    else:
                        print(f"⚠️ Unsupported action: {action}")

                print("Expected:", case["expected_result"])
                try:
                    page.wait_for_timeout(2000)
                except Exception:
                    pass

        browser.close()


# ╔══════════════════════════════════════════════════════════════╗
# ║  MAIN RUNNER                                                ║
# ╚══════════════════════════════════════════════════════╝
if FRAMEWORK == "selenium":
    run_with_selenium(test_suite, step_map)
elif FRAMEWORK == "playwright":
    run_with_playwright(test_suite, step_map)
else:
    raise ValueError("Unknown framework. Use 'selenium' or 'playwright'.")

