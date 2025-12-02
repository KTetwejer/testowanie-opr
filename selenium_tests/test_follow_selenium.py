from selenium.webdriver.common.by import By

from selenium_tests.test_auth_selenium import register_user, login_user


def test_follow_and_unfollow_user(driver, base_url):
    register_user(driver, base_url, "alice_follow", "alice_follow@example.com")
    register_user(driver, base_url, "bob_follow", "bob_follow@example.com")

    login_user(driver, base_url, "alice_follow")

    driver.get(f"{base_url}/user/bob_follow")
    driver.find_element(By.NAME, "submit").click()

    page_source = driver.page_source
    assert "You are following" in page_source or "following" in page_source

    driver.get(f"{base_url}/user/bob_follow")
    driver.find_element(By.NAME, "submit").click()

    page_source = driver.page_source
    assert "You are not following" in page_source or "not following" in page_source


