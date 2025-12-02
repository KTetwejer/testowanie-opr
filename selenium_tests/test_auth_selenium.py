from selenium.webdriver.common.by import By


def register_user(driver, base_url, username, email):
    driver.get(f"{base_url}/auth/register")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys("Secret123")
    driver.find_element(By.NAME, "password2").send_keys("Secret123")
    driver.find_element(By.NAME, "submit").click()


def login_user(driver, base_url, username, password="Secret123"):
    driver.get(f"{base_url}/auth/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()


def test_register_and_login(driver, base_url):
    register_user(driver, base_url, "selenium_user", "selenium@example.com")
    login_user(driver, base_url, "selenium_user")
    assert "/index" in driver.current_url or "Your post" in driver.page_source


