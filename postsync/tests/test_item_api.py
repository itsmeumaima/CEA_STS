
import json
import re
import html
from pathlib import Path

import pytest

BASE_URL = "http://127.0.0.1:8000"

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# ---------- API CONTEXT ----------
@pytest.fixture
def api_context(playwright):
    context = playwright.request.new_context(base_url=BASE_URL)
    yield context
    context.dispose()


# ---------- TEST ITEM FIXTURE ----------
@pytest.fixture
def test_item(api_context):
    response = api_context.post(
        "/item/api/",
        data={
            "name": "Playwright API Test Item",
            "description": "Item created for API testing",
            "price": 1500,
            "category": 1,
            "created_by": 1,
            "quantity": 10,
            "actual_quantity": 10,
        },
    )

    assert response.status == 201, response.text()
    item = response.json()

    yield item

    # Clean up test data after the test.
    api_context.delete(f"/item/api/{item['id']}/")


# ---------- SCREENSHOT HELPER ----------
def take_test_screenshot(page, test_name, method, endpoint, response):
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", test_name)
    screenshot_path = SCREENSHOT_DIR / f"{safe_name}.png"

    try:
        response_body = json.dumps(
            response.json(), indent=2
        )
    except (ValueError, TypeError):
        response_body = response.text()

    page.set_content(f"""
        <html>
        <head>
            <title>{html.escape(test_name)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f3f4f6;
                    padding: 35px;
                }}
                .card {{
                    max-width: 800px;
                    margin: auto;
                    padding: 28px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 3px 12px #ddd;
                }}
                h1 {{ color: #6d28d9; }}
                .status {{
                    display: inline-block;
                    padding: 8px 14px;
                    border-radius: 6px;
                    background: #dcfce7;
                    color: #166534;
                    font-weight: bold;
                }}
                pre {{
                    padding: 15px;
                    background: #f3f4f6;
                    border-radius: 6px;
                    white-space: pre-wrap;
                    overflow-wrap: anywhere;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>PostSync API Test Report</h1>
                <h2>{html.escape(test_name)}</h2>
                <p><b>HTTP Method:</b> {html.escape(method)}</p>
                <p><b>Endpoint:</b> {html.escape(endpoint)}</p>
                <p><b>HTTP Status:</b>
                    <span class="status">{response.status}</span>
                </p>
                <h3>API Response</h3>
                <pre>{html.escape(response_body)}</pre>
            </div>
        </body>
        </html>
    """)

    page.screenshot(path=str(screenshot_path), full_page=True)

    # Save screenshot path for the HTML report hook.
    return screenshot_path


# ---------- HTML REPORT SCREENSHOT ATTACHMENT ----------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        path = getattr(item, "_screenshot_path", None)

        if path and path.exists():
            try:
                import pytest_html

                extras = getattr(report, "extras", [])
                extras.append(pytest_html.extras.image(str(path)))
                report.extras = extras
            except (ImportError, AttributeError):
                pass


# ---------- CREATE TEST ----------
def test_api_create_item(api_context, page, request):
    response = api_context.post(
        "/item/api/",
        data={
            "name": "API Created Item",
            "description": "Testing create",
            "price": 2500,
            "category": 1,
            "created_by": 1,
            "quantity": 5,
            "actual_quantity": 5,
        },
    )

    path = take_test_screenshot(
        page, "Create Item", "POST", "/item/api/", response
    )
    request.node._screenshot_path = path

    assert response.status == 201
    data = response.json()
    assert data["name"] == "API Created Item"
    assert data["price"] == 2500

    # Remove the temporary test item.
    api_context.delete(f"/item/api/{data['id']}/")


# ---------- READ TEST ----------
def test_api_read_item(api_context, test_item, page, request):
    endpoint = f"/item/api/{test_item['id']}/"
    response = api_context.get(endpoint)

    path = take_test_screenshot(
        page, "Read Item", "GET", endpoint, response
    )
    request.node._screenshot_path = path

    assert response.status == 200
    data = response.json()
    assert data["id"] == test_item["id"]
    assert data["name"] == "Playwright API Test Item"


# ---------- UPDATE TEST ----------
def test_api_update_item(api_context, test_item, page, request):
    endpoint = f"/item/api/{test_item['id']}/"

    response = api_context.put(
        endpoint,
        data={
            "name": "Updated API Test Item",
            "price": 3000,
        },
    )

    path = take_test_screenshot(
        page, "Update Item", "PUT", endpoint, response
    )
    request.node._screenshot_path = path

    assert response.status == 200
    data = response.json()
    assert data["name"] == "Updated API Test Item"
    assert data["price"] == 3000


# ---------- DELETE TEST ----------
def test_api_delete_item(api_context, test_item, page, request):
    item_id = test_item["id"]
    endpoint = f"/item/api/{item_id}/"

    response = api_context.delete(endpoint)

    path = take_test_screenshot(
        page, "Delete Item", "DELETE", endpoint, response
    )
    request.node._screenshot_path = path

    assert response.status == 200

    # Confirm the item no longer exists.
    check_response = api_context.get(endpoint)
    assert check_response.status == 404
