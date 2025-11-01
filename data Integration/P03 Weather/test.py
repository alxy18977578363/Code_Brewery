from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

driver = webdriver.Chrome()

driver.get('https://www.baidu.com')

driver.quit()