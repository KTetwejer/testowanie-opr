import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import login_user
from seed_data import SEEDED_USERS


def test_user_registration_creates_new_account(browser, live_server):
    browser.get(f"{live_server}/auth/register")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    browser.find_element(By.NAME, "username").send_keys("newuser")
    browser.find_element(By.NAME, "email").send_keys("newuser@example.com")
    browser.find_element(By.NAME, "password").send_keys("NewUser2024!")
    browser.find_element(By.NAME, "password2").send_keys("NewUser2024!")
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 5).until(EC.url_contains("/auth/login"))
    assert "Congratulations, you are now a registered user!" in browser.page_source


def test_registration_rejects_duplicate_username(browser, live_server):
    browser.get(f"{live_server}/auth/register")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    browser.find_element(By.NAME, "username").send_keys("testuser")
    browser.find_element(By.NAME, "email").send_keys("newuser@example.com")
    browser.find_element(By.NAME, "password").send_keys("password123")
    browser.find_element(By.NAME, "password2").send_keys("password123")
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".invalid-feedback"))
    )

    error_div = browser.find_element(By.CSS_SELECTOR, ".invalid-feedback")
    assert "Please use a different username." in error_div.text


def test_successful_login_redirects_to_homepage(browser, live_server):
    login_user(browser, live_server)
    assert "Hi, testuser!" in browser.page_source


def test_login_with_invalid_credentials_shows_error_message(browser, live_server):
    browser.get(f"{live_server}/auth/login")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    username_field = browser.find_element(By.NAME, "username")
    username_field.clear()
    username_field.send_keys("nonexistent")

    password_field = browser.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys("IncorrectPass2024!")

    submit_button = browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    )
    submit_button.click()

    WebDriverWait(browser, 5).until(
        EC.url_contains("/auth/login")
    )
    
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-info"))
    )

    alert = browser.find_element(By.CSS_SELECTOR, ".alert.alert-info")
    assert "Invalid username or password" in alert.text


def test_logout_redirects_to_login_page(browser, live_server):
    login_user(browser, live_server)
    browser.get(f"{live_server}/auth/logout")

    WebDriverWait(browser, 5).until(EC.url_contains("/auth/login"))

    browser.get(f"{live_server}/")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "nav"))
    )

    assert "Login" in browser.page_source


def test_password_reset_workflow_completes_successfully(browser, live_server, app_instance):
    browser.get(f"{live_server}/auth/reset_password_request")
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, "email")))

    browser.find_element(By.NAME, "email").send_keys(SEEDED_USERS["testuser"]["email"])
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 10).until(
        lambda driver: "/auth/login" in driver.current_url
    )
    
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-info"))
    )
    
    alert = browser.find_element(By.CSS_SELECTOR, ".alert.alert-info")
    assert (
        "Check your email for the instructions to reset your password"
        in alert.text
    )

    from app.models import User
    from app import db

    with app_instance.app_context():
        user = db.session.scalar(
            db.select(User).where(User.username == SEEDED_USERS["testuser"]["username"])
        )
        if not user:
            pytest.fail("Test user not found")
        reset_token = user.get_reset_password_token()

    browser.get(f"{live_server}/auth/reset_password/{reset_token}")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

    assert browser.find_element(By.NAME, "password")
    assert browser.find_element(By.NAME, "password2")
    assert browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    )

    new_password = "ResetPassword2024#"
    password_field = browser.find_element(By.NAME, "password")
    password_field.send_keys(new_password)
    password2_field = browser.find_element(By.NAME, "password2")
    password2_field.send_keys(new_password)
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 5).until(EC.url_contains("/auth/login"))
    assert "Your password has been reset." in browser.page_source

    # Step 4: Login with new password
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    browser.find_element(By.NAME, "username").send_keys("testuser")
    browser.find_element(By.NAME, "password").send_keys(new_password)

    submit_button = browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    )
    submit_button.click()

    WebDriverWait(browser, 5).until(EC.url_contains("/index"))
    assert "Hi, testuser!" in browser.page_source

    browser.get(f"{live_server}/auth/logout")
    WebDriverWait(browser, 5).until(
        lambda driver: "/index" in driver.current_url
        or "/auth/login" in driver.current_url
    )

    browser.get(f"{live_server}/auth/login")
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    browser.find_element(By.NAME, "username").send_keys(
        SEEDED_USERS["testuser"]["username"]
    )
    browser.find_element(By.NAME, "password").send_keys(
        SEEDED_USERS["testuser"]["password"]
    )
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 5).until(EC.url_contains("/auth/login"))
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-info"))
    )
    assert (
        "Invalid username or password"
        in browser.find_element(By.CSS_SELECTOR, ".alert.alert-info").text
    )

    browser.find_element(By.NAME, "username").clear()
    browser.find_element(By.NAME, "password").clear()
    browser.find_element(By.NAME, "username").send_keys(
        SEEDED_USERS["testuser"]["username"]
    )
    browser.find_element(By.NAME, "password").send_keys(new_password)
    browser.find_element(
        By.CSS_SELECTOR, "input[type=submit], button[type=submit]"
    ).click()

    WebDriverWait(browser, 5).until(EC.url_contains("/index"))
    assert "Hi, testuser!" in browser.page_source
