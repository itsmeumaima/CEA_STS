
from playwright.sync_api import Page, Route, expect

BASE_URL = "http://127.0.0.1:8000"


def test_products_page_returns_empty_state(page: Page):
    def handle(route: Route):
        route.fulfill(
            status=200,
            content_type="text/html",
            body="""
            <html>
                <body>
                    <h3>No items found</h3>
                </body>
            </html>
            """
        )

    page.route("**/item/", handle)
    page.goto(f"{BASE_URL}/item/")

    expect(page.get_by_role("heading", name="No items found")).to_be_visible()


def test_products_page_returns_server_error(page: Page):
    def handle(route: Route):
        route.fulfill(
            status=500,
            content_type="text/html",
            body="""
            <html>
                <body>
                    <h1>Internal Server Error</h1>
                </body>
            </html>
            """
        )

    page.route("**/item/", handle)
    response = page.goto(f"{BASE_URL}/item/")

    assert response is not None
    assert response.status == 500

    expect(
        page.get_by_role("heading", name="Internal Server Error")
    ).to_be_visible()
