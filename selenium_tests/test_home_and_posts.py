from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import create_post, login_user
from seed_data import SEEDED_USERS


def test_user_can_create_and_view_post(browser, live_server):
    login_user(browser, live_server)
    post_content = "My first post"

    create_post(browser, live_server, post_body=post_content)

    assert post_content in browser.page_source


def test_empty_post_form_does_not_create_post(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/index")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
    )
    
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()
    
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
    )

    assert "Your post is now live!" not in browser.page_source


def test_posts_appear_on_explore_page(browser, live_server):
    login_user(browser, live_server)
    post_content = "explore_test_post"

    create_post(browser, live_server, post_body=post_content)

    browser.get(f"{live_server}/explore")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert post_content in browser.page_source


def test_post_display_includes_user_info_and_timestamp(browser, live_server):
    login_user(
        browser,
        live_server,
        username=SEEDED_USERS["otheruser"]["username"],
        password=SEEDED_USERS["otheruser"]["password"],
    )

    post_content = "content body"
    create_post(browser, live_server, post_body=post_content)

    browser.get(f"{live_server}/explore")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert browser.find_element(By.CSS_SELECTOR, "a[href*='/user/'] img")
    timestamp = browser.find_element(By.CSS_SELECTOR, "[data-timestamp]")
    assert timestamp.text == "a few seconds ago"
    assert browser.find_element(
        By.CSS_SELECTOR, f"a[href='/user/{SEEDED_USERS['otheruser']['username']}']"
    )
    assert post_content in browser.page_source


def test_pagination_navigation_works_correctly(browser, live_server):
    login_user(browser, live_server)


    create_post(browser, live_server, post_body="pagination_test_post")
    create_post(browser, live_server, post_body="pagination_test_post_2")

    browser.get(f"{live_server}/explore")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "pagination_test_post" in browser.page_source

    next_link = browser.find_element(By.PARTIAL_LINK_TEXT, "Older posts")
    assert "page=2" in next_link.get_attribute("href")
    prev_link = browser.find_element(By.PARTIAL_LINK_TEXT, "Newer posts")
    assert "None" in prev_link.get_attribute("href")

    browser.execute_script(
        "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });",
        next_link,
    )
    next_link.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    next_link = browser.find_element(By.PARTIAL_LINK_TEXT, "Older posts")
    prev_link = browser.find_element(By.PARTIAL_LINK_TEXT, "Newer posts")
    assert "None" in next_link.get_attribute("href")
    assert "/explore?page=1" in prev_link.get_attribute("href")
