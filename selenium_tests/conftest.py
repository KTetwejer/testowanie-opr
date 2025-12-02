import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def driver():
    options = Options()

    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(5)
    try:
        yield driver
    finally:
        driver.quit()


