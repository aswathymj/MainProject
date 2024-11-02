from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# Set up the Edge WebDriver using webdriver-manager
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

# Define login credentials and URLs
login_url = "http://127.0.0.1:8000/login/"
admin_view_url = "http://127.0.0.1:8000/admin_view/"
email = "mobicare123@gmail.com"
password = "Int@1234"

try:
    # Step 1: Open the login page
    driver.get(login_url)

    # Step 2: Find and fill the email field
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "semail"))  # Adjust name if necessary
    )
    email_field.send_keys(email)

    # Step 3: Find and fill the password field
    password_field = driver.find_element(By.NAME, "spassword")  # Adjust name if necessary
    password_field.send_keys(password)

    # Step 4: Submit the form
    password_field.send_keys(Keys.RETURN)

    # Step 5: Wait for the redirection to the admin view page
    WebDriverWait(driver, 10).until(
        EC.url_to_be(admin_view_url)
    )

    # Step 6: Navigate to the Manage Technicians page
    manage_technicians_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Manage Technicians"))
    )
    manage_technicians_link.click()

    # Step 7: Wait for the technicians list to load
    time.sleep(3)  # Adjust the sleep time as necessary for the page to load

    # Step 8: Click on the Download PDF button for the first technician (adjust if necessary)
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//td/a[contains(@class, 'btn btn-primary btn-sm')]"))
    )
    download_button.click()

    # Optional: Add a confirmation message
    print("Successfully clicked the Download PDF button.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Step 9: Close the browser after tests
    time.sleep(5)  # Optional: wait a moment before closing to see the result
    driver.quit()
