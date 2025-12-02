from selenium.webdriver.common.by import By

from selenium_tests.test_auth_selenium import register_user, login_user


def test_send_and_read_message(driver, base_url):
    register_user(driver, base_url, "alice_msg", "alice_msg@example.com")
    register_user(driver, base_url, "bob_msg", "bob_msg@example.com")

    login_user(driver, base_url, "alice_msg")

    driver.get(f"{base_url}/send_message/bob_msg")
    driver.find_element(By.NAME, "message").send_keys("Hello Bob from Selenium!")
    driver.find_element(By.NAME, "submit").click()

    page_source = driver.page_source
    assert "Your message has been sent." in page_source or "message has been sent" in page_source

    driver.get(f"{base_url}/auth/logout")
    login_user(driver, base_url, "bob_msg")
    driver.get(f"{base_url}/messages")

    assert "Hello Bob from Selenium!" in driver.page_source


