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
user_view_url = "http://127.0.0.1:8000/user_view/"
accessories_url = "http://127.0.0.1:8000/accessories/"
status_url = "http://127.0.0.1:8000/repair_status/"
email = "aswathymj2002@gmail.com"
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

    # Step 5: Wait for the redirection to the user view page
    WebDriverWait(driver, 10).until(
        EC.url_to_be(user_view_url)
    )

    # Step 6: Navigate to the accessories page
    driver.get(accessories_url)

    # Step 7: Wait for the services dropdown to be clickable and click on it
    services_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Services"))  # Adjust text if necessary
    )
    services_dropdown.click()

    # Step 8: Wait for the status link to be clickable and click on it
    status_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Status"))  # Adjust text if necessary
    )
    status_link.click()

    # Step 9: Wait for the status page to load
    WebDriverWait(driver, 10).until(
        EC.url_to_be(status_url)
    )

    # Optional: Add a confirmation message
    print("Successfully navigated to the status page.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Step 10: Close the browser after tests
    time.sleep(5)  # Optional: wait a moment before closing to see the result
    driver.quit()
