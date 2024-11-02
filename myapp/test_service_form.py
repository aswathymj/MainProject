from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Initialize Edge driver
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

# Go to the service form page
driver.get('http://127.0.0.1:8000/repair')  # Replace with the actual form URL

# Wait until the form is loaded
wait = WebDriverWait(driver, 10)

# Fill the form
category_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'phone-category')))
category_dropdown.send_keys('1')  # Select a category (replace with actual category)

subcategory_dropdown = driver.find_element(By.ID, 'phone-subcategory')
subcategory_dropdown.send_keys('1')  # Select a subcategory (replace with actual subcategory)

model_dropdown = driver.find_element(By.ID, 'phone-model')
model_dropdown.send_keys('1')  # Select a model (replace with actual model)

complaint_dropdown = driver.find_element(By.ID, 'phone-complaint')
complaint_dropdown.send_keys('1')  # Select a complaint (replace with actual complaint)

# Fill the rest of the fields
pickup_date = driver.find_element(By.ID, 'phone-date')
pickup_date.send_keys('2024-10-10')

phone_number = driver.find_element(By.ID, 'phone-number')
phone_number.send_keys('9876543210')

issue_description = driver.find_element(By.ID, 'issue-description')
issue_description.send_keys('Screen is cracked')

pickup_address = driver.find_element(By.ID, 'phone-address')
pickup_address.send_keys('123 Street, City')

# Agree to terms
terms_checkbox = driver.find_element(By.ID, 'terms')
terms_checkbox.click()

# Submit the form
submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
submit_button.click()

# Wait for the redirection to the repair_status page
wait.until(EC.url_contains('repair_status'))

# Verify the URL is the repair_status page
assert 'repair_status' in driver.current_url, "Form submission failed or incorrect redirect"

# Close the browser
driver.quit()
