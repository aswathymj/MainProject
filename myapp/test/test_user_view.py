from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

# Set up the Edge WebDriver using webdriver-manager
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

# Define test credentials for the user
user = {"email": "aswathymj2002@gmail.com", "password": "Int@1234", "expected_url": "http://127.0.0.1:8000/user_view/"}

# Function to perform login, click on accessories, and check redirection
def test_login_and_navigate():
    driver.get("http://127.0.0.1:8000/login/")  # Your login URL

    # Find and fill the email field
    email_field = driver.find_element("name", "semail")
    email_field.send_keys(user['email'])

    # Find and fill the password field
    password_field = driver.find_element("name", "spassword")
    password_field.send_keys(user['password'])

    # Submit the form
    password_field.send_keys(Keys.RETURN)

    # Wait for the redirection to complete
    time.sleep(3)

    # Check if the user is redirected to the user view page
    if driver.current_url == user['expected_url']:
        print(f"Login test passed for {user['email']}")
        
        # Find and click on the 'Accessories' link in the navbar
        try:
            accessories_link = driver.find_element("link text", "Accessories")  # Adjust the locator as necessary
            accessories_link.click()

            # Wait for the page to load
            time.sleep(2)

            # Verify if the current URL is the accessories page
            if driver.current_url == "http://127.0.0.1:8000/accessories/":
                print(f"Navigation to Accessories page passed for {user['email']}")
            else:
                print(f"Failed to navigate to Accessories page for {user['email']} - Redirected to {driver.current_url} instead.")
        except Exception as e:
            print(f"Accessories link not found or failed to click: {e}")
    else:
        print(f"Login test failed for {user['email']} - Redirected to {driver.current_url} instead of {user['expected_url']}")

# Run the test
test_login_and_navigate()

# Close the browser after test
driver.quit()
