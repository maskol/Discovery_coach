#!/usr/bin/env python3
"""
Test Strategic Initiative tab switching behavior
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_strategic_initiative_tab():
    """Test that messages appear in the correct tab"""

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Load the frontend
        driver.get(
            "file:///Users/mats/Egna-Dokument/Utveckling/Jobb/Discovery_coach/frontend/index.html"
        )

        # Wait for page to load
        time.sleep(2)

        # Check initial state
        epic_tab = driver.find_element(By.ID, "epicsTab")
        si_tab = driver.find_element(By.ID, "strategicInitiativesTab")

        print(
            f"Initial - Epic tab active: {'active' in epic_tab.get_attribute('class')}"
        )
        print(f"Initial - SI tab active: {'active' in si_tab.get_attribute('class')}")

        # Click Strategic Initiatives tab
        si_tab.click()
        time.sleep(1)

        # Check state after clicking
        epic_tab = driver.find_element(By.ID, "epicsTab")
        si_tab = driver.find_element(By.ID, "strategicInitiativesTab")

        print(
            f"After click - Epic tab active: {'active' in epic_tab.get_attribute('class')}"
        )
        print(
            f"After click - SI tab active: {'active' in si_tab.get_attribute('class')}"
        )

        # Check which content is visible
        epic_content = driver.find_element(By.ID, "epicsContent")
        si_content = driver.find_element(By.ID, "strategicInitiativesContent")

        print(f"Epic content display: {epic_content.value_of_css_property('display')}")
        print(f"SI content display: {si_content.value_of_css_property('display')}")

        # Try to send a message
        si_input = driver.find_element(By.ID, "messageInputStrategicInitiatives")
        print(f"SI input visible: {si_input.is_displayed()}")

        driver.quit()

    except Exception as e:
        print(f"Error: {e}")
        driver.quit() if "driver" in locals() else None


if __name__ == "__main__":
    test_strategic_initiative_tab()
