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

    # Step 7: Wait for the product list to load and locate the "View Details" button for "boAt Airdopes"
    view_details_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h4[contains(text(), 'boAt Airdopes')]/../a[contains(@class, 'btn btn-primary')]")
        )
    )
    
    # Click on the "View Details" button
    view_details_button.click()

    # Step 8: Wait for the wishlist button to be clickable and click on it
    wishlist_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @class='wishlist-button']"))
    )
    wishlist_button.click()

    # Optional: Add a confirmation message
    print("Successfully added 'boAt Airdopes' to the wishlist.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Step 9: Close the browser after tests
    time.sleep(5)  # Optional: wait a moment before closing to see the result
    driver.quit()
