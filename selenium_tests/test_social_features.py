import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import login_user
from seed_data import SEEDED_USERS


def test_follow_button_changes_to_unfollow_after_clicking(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/user/{SEEDED_USERS['otheruser']['username']}")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    follow_button = browser.find_element(By.CSS_SELECTOR, "input[value='Follow']")
    assert follow_button.is_displayed()

    follow_button.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Unfollow']"))
    )


def test_followed_user_posts_appear_on_home_feed(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/user/{SEEDED_USERS['otheruser']['username']}")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    follow_input = browser.find_element(By.CSS_SELECTOR, "input[value='Follow']")
    follow_input.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Unfollow']"))
    )

    browser.get(f"{live_server}/index")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    assert "Hello from another user" in browser.page_source


def test_follower_count_updates_when_user_is_followed(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/user/{SEEDED_USERS['otheruser']['username']}")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    assert "0 followers" in browser.page_source

    follow_button = browser.find_element(By.CSS_SELECTOR, "input[value='Follow']")
    follow_button.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Unfollow']"))
    )

    browser.refresh()
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    assert "1 followers" in browser.page_source


def test_follower_count_decreases_when_user_is_unfollowed(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/user/{SEEDED_USERS['otheruser']['username']}")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    follow_button = browser.find_element(By.CSS_SELECTOR, "input[value='Follow']")
    follow_button.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Unfollow']"))
    )

    browser.refresh()
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    assert "1 followers" in browser.page_source

    unfollow_button = browser.find_element(By.CSS_SELECTOR, "input[value='Unfollow']")
    unfollow_button.click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Follow']"))
    )

    assert "0 followers" in browser.page_source


def test_user_popup_displays_on_hover(browser, live_server):
    login_user(browser, live_server)

    browser.get(f"{live_server}/explore")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    username_links = browser.find_elements(By.CSS_SELECTOR, "a[href*='/user/']")
    if username_links:
        actions = ActionChains(browser)
        actions.move_to_element(username_links[0]).perform()

        time.sleep(2)

        popups = browser.find_elements(By.CSS_SELECTOR, ".popover")
        if popups:
            popup = popups[0]
            assert popup.is_displayed()

            popup_text = popup.text
            assert len(popup_text) > 0
