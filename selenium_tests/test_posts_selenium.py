from selenium.webdriver.common.by import By

from selenium_tests.test_auth_selenium import register_user, login_user


def test_create_post(driver, base_url):
    username = "post_user"
    email = "post_user@example.com"

    register_user(driver, base_url, username, email)
    login_user(driver, base_url, username)

    driver.get(f"{base_url}/index")

    driver.find_element(By.NAME, "post").send_keys("Hello from Selenium")
    driver.find_element(By.NAME, "submit").click()

    assert "Hello from Selenium" in driver.page_source


