

from selenium import webdriver as wd
import time

from selenium.webdriver.common.by import By


class tj_bbs(object):
    bbs_browser=wd.Chrome()
    login_page='http://cyr985.net3v.club/bbs/login.asp'
    post_page='http://cyr985.net3v.club/bbs/topic.asp?id=4891&boardid=6&TB=1'
    waittime=5
    def __init__(self):
        pass
    def auto_login(self, username, password):
        self.bbs_browser.get(self.login_page)
        time.sleep(self.waittime)
        name_bt=self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[1]/div[1]/input')
        name_bt.send_keys(username)
        pwd_bt = self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[2]/div[1]/input')
        pwd_bt.send_keys(password)
        enter_button=self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[5]/input')
        enter_button.click()
        self.bbs_browser.get(self.post_page)
        time.sleep(self.waittime)
        _link=self.bbs_browser.find_element(by=By.XPATH,value='//*[@id="Board"]/div[6]/a')
        _link.click()
        _link2=self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table[3]/tbody/tr/td[2]/a[1]')
        _link2.click()
        time.sleep(self.waittime)
        _link3=self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/div[1]/a[3]/img')
        _link3.click()
        time.sleep(self.waittime)
        iframe = self.bbs_browser.find_element(By.ID, 'edit')
        self.bbs_browser.switch_to.frame(iframe)
        _space=self.bbs_browser.find_element(by=By.XPATH,value='/html/body')
        _space.click()
        _space.send_keys('2351136 李盛鹏')
        time.sleep(5)
        self.bbs_browser.switch_to.default_content()
        _bt=self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table/tbody/tr/td/div[2]/form[2]/div[5]/input[1]')
        _bt.click()
        pass

if __name__=='__main__':
    whw=tj_bbs()
    whw.auto_login('落星','Lsp20040618%')



