from pathlib import Path
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"

Path("screenshots").mkdir(exist_ok=True)
def login_user(page: Page):
    page.goto(BASE_URL)
    # Click Login
    page.get_by_role("link", name="Login").click()
    page.locator("#username").fill("umaimagul")
    page.locator("#password").fill("umgu1234")
    page.get_by_role("button", name="Sign in").click()
    expect(page).not_to_have_url(f"{BASE_URL}/login/")

# UI-01: Verify homepage loading
def test_UI_01_homepage_loads(page: Page):
    response = page.goto(BASE_URL)
    assert response is not None
    assert response.status == 200
    expect(page.locator("body")).to_be_visible()
    page.wait_for_timeout(3000)
    # Take screenshot after the test passes
    page.screenshot(
        path="screenshots/UI-01_homepage_loading.png",
        full_page=True
    )

# UI-02: Verify website title
def test_UI_02_website_title(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title("Welcome | PostSync")
    # Take screenshot after the test passes
    page.wait_for_timeout(3000)
    page.screenshot(
        path="screenshots/UI-02_website_title.png",
        full_page=True
    )

# UI-03: Verify navigation bar
def test_UI_03_navigation_bar(page: Page):
    page.goto(BASE_URL)
    navbar = page.locator("nav")
    expect(navbar).to_be_visible()
    logo = navbar.get_by_role("link", name="PostSync")
    expect(logo).to_be_visible()
    browse_link = navbar.get_by_role("link", name="Browse")
    expect(browse_link).to_be_visible()
    page.wait_for_timeout(3000)
    # Take screenshot after the test passes
    page.screenshot(
        path="screenshots/UI-03_navigation_bar.png",
        full_page=True
    )

# UI-04: Verify website logo
def test_UI_04_website_logo(page: Page):
    page.goto(BASE_URL)
    # Verify the logo icon is visible
    logo_icon = page.locator("nav .fa-sync")
    expect(logo_icon).to_be_visible()
    # Verify the PostSync text link is visible
    logo_text = page.locator('nav a[href="/"]')
    expect(logo_text).to_be_visible()
    expect(logo_text).to_have_text("PostSync")
    page.wait_for_timeout(3000)
    # Take screenshot
    page.screenshot(
        path="screenshots/UI-04_website_logo.png",
        full_page=True
    )

# UI-05: Verify product listing layout
def test_UI_05_product_listing_layout(page: Page):
    page.goto(f"{BASE_URL}/item/")
    # Verify the products page is displayed
    expect(page.get_by_role("heading", name="Browse Items")).to_be_visible()
    # Verify the product grid is visible if products exist
    product_grid = page.locator("main .grid.grid-cols-1")
    expect(product_grid.first).to_be_visible()
    page.wait_for_timeout(3000)
    # Take screenshot
    page.screenshot(
        path="screenshots/UI-05_product_listing_layout.png",
        full_page=True
    )
