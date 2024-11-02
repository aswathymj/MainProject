from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

# Set up the Edge WebDriver using webdriver-manager
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

# Define test credentials for different users
users = [
    {"email": "mobicare123@gmail.com", "password": "Int@1234", "expected_url": "http://127.0.0.1:8000/admin_view/"},
    {"email": "aswathymj2002@gmail.com", "password": "Int@1234", "expected_url": "http://127.0.0.1:8000/user_view/"},
    {"email": "abhikanth2001@gmail.com", "password": "Int@1234", "expected_url": "http://127.0.0.1:8000/technician_view/"}
]

# Function to perform login and check redirection
def test_login(user):
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

    # Check if the user is redirected to the correct page
    if driver.current_url == user['expected_url']:
        print(f"Login test passed for {user['email']}")
    else:
        print(f"Login test failed for {user['email']} - Redirected to {driver.current_url} instead of {user['expected_url']}")

# Run tests for all users
for user in users:
    test_login(user)

# Close the browser after tests
driver.quit()
