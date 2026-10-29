
import re
from pathlib import Path

from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"
ITEMS_URL = f"{BASE_URL}/item/"
CART_URL = f"{BASE_URL}/cart/"
LOGIN_URL = f"{BASE_URL}/login/"

TEST_USERNAME = "umaimagul"
TEST_PASSWORD = "umgu1234"

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# ---------- COMMON HELPERS ----------

def take_screenshot(page: Page, test_case_id: str):
    """Save a full-page screenshot for the test case."""
    screenshot_path = SCREENSHOT_DIR / f"{test_case_id}.png"

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )
        print(f"\nScreenshot saved: {screenshot_path}")
    except Exception as error:
        print(f"\nScreenshot failed for {test_case_id}: {error}")


def login_user(page: Page):
    """Log in using the regular test account."""
    page.goto(LOGIN_URL)
    page.locator('input[name="username"]').fill(TEST_USERNAME)
    page.locator('input[name="password"]').fill(TEST_PASSWORD)

    page.locator(
        'button[type="submit"], input[type="submit"]'
    ).first.click()

    expect(page).not_to_have_url(LOGIN_URL)


def login_admin(page: Page):
    """Log in using the admin test account."""
    page.goto(LOGIN_URL)
    page.locator('input[name="username"]').fill("admin")
    page.locator('input[name="password"]').fill("123")

    page.locator(
        'button[type="submit"], input[type="submit"]'
    ).first.click()

    expect(page).not_to_have_url(LOGIN_URL)


def logout_user(page: Page):
    """Log out and verify the cart is protected."""
    logout_link = page.get_by_role(
        "link", name=re.compile("Logout", re.I)
    )

    if logout_link.is_visible():
        logout_link.click()

    page.goto(CART_URL)
    expect(page).not_to_have_url(CART_URL)


def first_product_id(page: Page) -> int:
    """Get the ID of the first product displayed."""
    page.goto(ITEMS_URL)

    product = page.locator(
        'a[href^="/item/"][href$="/"]'
    ).filter(has=page.locator("h3")).first

    expect(product).to_be_visible()

    href = product.get_attribute("href")
    match = re.search(r"/item/(\d+)/$", href or "")

    assert match is not None, "No product ID found"
    return int(match.group(1))


def submit_form(page: Page):
    """Submit the current form."""
    page.locator(
        'button[type="submit"], input[type="submit"]'
    ).first.click()


def fill_item_form(page: Page, name: str):
    """Fill the product form with valid default values."""
    page.locator('input[name="name"]').fill(name)

    page.locator('textarea[name="description"]').fill(
        "Created for Playwright testing"
    )

    page.locator('input[name="price"]').fill("1250")
    page.locator('input[name="quantity"]').fill("10")
    page.locator('input[name="actual_quantity"]').fill("10")
    page.locator('select[name="category"]').select_option(
        label="Flowers"
    )


# ==================================================
# FEATURE 1: SHOPPING CART
# ==================================================

def test_cart_add_item(page: Page):
    """TC-01: Logged-in user adds an item to the cart."""
    login_user(page)

    try:
        item_id = first_product_id(page)
        page.goto(f"{BASE_URL}/cart/add/{item_id}/")

        page.locator('input[name="quantity"]').fill("1")
        submit_form(page)

        expect(page).to_have_url(CART_URL)
        expect(page.locator("body")).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-01_cart_add_item")
        logout_user(page)


def test_cart_page_opens(page: Page):
    """TC-02: Logged-in user opens the cart."""
    login_user(page)

    try:
        page.goto(CART_URL)
        expect(page.locator("body")).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-02_cart_page_opens")
        logout_user(page)


def test_cart_requires_login(page: Page):
    """TC-03: Logged-out user cannot access the cart."""
    try:
        page.goto(CART_URL)

        # Django should redirect the user to the login page.
        expect(page).not_to_have_url(CART_URL)

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-03_cart_requires_login")


# ==================================================
# FEATURE 2: ADMIN PRODUCT MANAGEMENT
# ==================================================

def test_add_item_with_valid_data(page: Page):
    """TC-04: Admin creates a product with valid data."""
    login_admin(page)

    try:
        page.goto(f"{ITEMS_URL}new/")

        item_name = "E2E Valid Item 12345"
        fill_item_form(page, item_name)
        submit_form(page)

        expect(
            page.get_by_role("heading", name=item_name)
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-04_add_item_valid_data")
        logout_user(page)


def test_add_item_without_name(page: Page):
    """TC-05: Admin submits the product form without a name."""
    login_admin(page)

    try:
        page.goto(f"{ITEMS_URL}new/")

        fill_item_form(page, "Temporary name")
        page.locator('input[name="name"]').fill("")
        submit_form(page)

        expect(
            page.locator('input[name="name"]')
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-05_add_item_without_name")
        logout_user(page)


def test_add_item_with_invalid_price(page: Page):
    """TC-06: Admin submits a negative product price."""
    login_admin(page)

    try:
        page.goto(f"{ITEMS_URL}new/")

        fill_item_form(page, "E2E Invalid Price Item")
        page.locator('input[name="price"]').fill("-10")
        submit_form(page)

        expect(page).to_have_url(re.compile(r"/item/new/?$"))

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-06_add_item_invalid_price")
        logout_user(page)


# ==================================================
# FEATURE 3: PRODUCT SEARCH
# ==================================================

def test_search_existing_item(page: Page):
    """TC-07: User searches for an existing product."""
    login_user(page)

    try:
        page.goto(ITEMS_URL)

        product = page.locator(
            'a[href^="/item/"][href$="/"]'
        ).filter(has=page.locator("h3")).first

        expect(product).to_be_visible()
        item_name = product.locator("h3").inner_text().strip()

        page.locator(
            'input[name="query"][type="text"]'
        ).fill(item_name)

        page.get_by_role("button", name="Search").click()

        expect(
            page.get_by_text(item_name, exact=True).first
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-07_search_existing_item")
        logout_user(page)


def test_search_nonexistent_item(page: Page):
    """TC-08: User searches for a nonexistent product."""
    login_user(page)

    try:
        page.goto(ITEMS_URL)

        page.locator(
            'input[name="query"][type="text"]'
        ).fill("NoSuchProduct987654")

        page.get_by_role("button", name="Search").click()

        expect(
            page.get_by_role("heading", name="No items found")
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-08_search_nonexistent_item")
        logout_user(page)


def test_search_empty_input(page: Page):
    """TC-09: User submits an empty search."""
    login_user(page)

    try:
        page.goto(ITEMS_URL)

        page.locator(
            'input[name="query"][type="text"]'
        ).fill("")

        page.get_by_role("button", name="Search").click()

        expect(
            page.get_by_role("heading", name="All Items")
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-09_search_empty_input")
        logout_user(page)


# ==================================================
# FEATURE 4: PRODUCT FILTERING AND SORTING
# ==================================================

def test_filter_items_by_category(page: Page):
    """TC-10: User filters products by category."""
    login_user(page)

    try:
        page.goto(ITEMS_URL)

        category_links = page.locator('a[href*="category="]')
        expect(category_links.first).to_be_visible()
        category_links.first.click()

        expect(page).to_have_url(re.compile(r"category=\d+"))

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-10_filter_by_category")
        logout_user(page)


def test_sort_items_by_lowest_price(page: Page):
    """TC-11: User sorts products by lowest price."""
    login_user(page)

    try:
        page.goto(ITEMS_URL)

        page.locator(
            'select[name="sort"]'
        ).select_option("price_low")

        expect(page).to_have_url(re.compile(r"sort=price_low"))

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-11_sort_lowest_price")
        logout_user(page)


def test_invalid_category_shows_no_results(page: Page):
    """TC-12: An invalid category returns no products."""
    login_user(page)

    try:
        page.goto(f"{ITEMS_URL}?category=999999999")

        expect(page.locator("body")).to_be_visible()
        expect(
            page.get_by_role("heading", name="No items found")
        ).to_be_visible()

    finally:
        page.wait_for_timeout(3000)
        take_screenshot(page, "TC-12_invalid_category")
        logout_user(page)
