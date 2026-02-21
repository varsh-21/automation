# Selenium E2E automation for Wellzio Cascade

This repository contains a **Pytest + Selenium** end-to-end test for:

- https://www.wellzio.com/cascade/

## What the test covers

The test performs a practical user-journey smoke flow:

1. Opens the Cascade landing page.
2. Verifies the page title loads and URL is correct.
3. Confirms key marketing text is visible (`Cascade` / `Wellzio`).
4. Finds and clicks a primary CTA (for example: `Contact`, `Demo`, `Learn more`, `Get started`, `Book`, `Schedule`) if available.
5. Validates browser state changed after CTA interaction (URL change, anchor navigation, or contact/form content appearing).

## Prerequisites

- Python 3.10+
- Google Chrome or Chromium installed

> Selenium 4 uses Selenium Manager to resolve browser drivers automatically.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest -q
```

To run headed mode (non-headless):

```bash
HEADLESS=false pytest -q
```

To override target URL:

```bash
BASE_URL="https://www.wellzio.com/cascade/" pytest -q
```
