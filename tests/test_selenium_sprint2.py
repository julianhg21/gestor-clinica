import os

import pytest

BASE = os.getenv("STAGING_BASE_URL", "").rstrip("/")


pytestmark = pytest.mark.selenium


@pytest.mark.skipif(not BASE, reason="Defina STAGING_BASE_URL para ejecutar Selenium")
def test_login_screen_and_navigation_with_chrome():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1000")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(BASE)
        assert "DUALITY" in driver.page_source
        assert driver.find_element(By.ID, "login-email").is_displayed()
        assert driver.find_element(By.ID, "login-password").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "#login-form button").is_displayed()
    finally:
        driver.quit()
