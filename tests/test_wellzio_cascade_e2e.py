import os
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.getenv("BASE_URL", "https://www.wellzio.com/cascade/")
HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "20"))

CTA_KEYWORDS = [
    "contact",
    "demo",
    "learn more",
    "get started",
    "book",
    "schedule",
    "talk",
]


@pytest.fixture
def driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        browser = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(f"Chrome WebDriver could not be initialized in this environment: {exc}")

    yield browser
    browser.quit()


def _normalized_text(element):
    return " ".join(element.text.lower().split())


def _find_clickable_cta(driver):
    candidates = driver.find_elements(By.CSS_SELECTOR, "a,button")
    for element in candidates:
        text = _normalized_text(element)
        if not text:
            continue
        if any(keyword in text for keyword in CTA_KEYWORDS):
            return element
    return None


def _same_domain(url_a: str, url_b: str) -> bool:
    host_a = urlparse(url_a).netloc.replace("www.", "")
    host_b = urlparse(url_b).netloc.replace("www.", "")
    return host_a == host_b


def test_wellzio_cascade_e2e_smoke(driver):
    wait = WebDriverWait(driver, WAIT_SECONDS)

    driver.get(BASE_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    assert "wellzio" in driver.current_url.lower() or "cascade" in driver.current_url.lower()
    assert driver.title.strip(), "Expected non-empty page title"

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert (
        "cascade" in body_text or "wellzio" in body_text
    ), "Expected page content to include brand or product keyword"

    initial_url = driver.current_url
    cta = _find_clickable_cta(driver)
    assert cta is not None, "Expected at least one clickable CTA on landing page"

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cta)
    cta.click()

    state_changed = False
    try:
        wait.until(lambda d: d.current_url != initial_url)
        state_changed = True
    except TimeoutException:
        pass

    if not state_changed:
        current = driver.current_url
        if "#" in current and current != initial_url:
            state_changed = True
        else:
            updated_body = driver.find_element(By.TAG_NAME, "body").text.lower()
            state_changed = any(
                token in updated_body
                for token in ["contact", "book", "schedule", "form", "demo"]
            )

    assert state_changed, "CTA click did not produce an observable navigation or content change"
    assert _same_domain(BASE_URL, driver.current_url), "CTA flow unexpectedly left target domain"
