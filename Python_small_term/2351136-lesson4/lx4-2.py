from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class tj_web(object):
    def __init__(self):
        self.tj_browser = webdriver.Chrome()
        self.First_page = 'https://www.tongji.edu.cn'
        self.wait_time = 3

    def auto_click(self, txt_list):
        for item in txt_list:
            self.tj_browser.get(self.First_page)
            time.sleep(self.wait_time)  # Adding a wait to ensure elements are loaded
            click_button = self.tj_browser.find_element(By.LINK_TEXT, item)
            click_button.click()
            filename = f"{item}.png"
            self.tj_browser.save_screenshot(filename)
            with open(f"{item}.txt", "w", encoding="utf-8") as text_file:
                text_file.write(self.tj_browser.page_source)

if __name__ == '__main__':
    tj = tj_web()  # Creating an instance of tj_web
    tj.auto_click(['科学研究', '招生就业', '交流合作'])  # Calling auto_click method with a list of link texts