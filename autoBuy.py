# coding=utf-8
import base64
import threading
import time
import requests
from lxml.etree import HTML
from selenium import webdriver
import winsound
import logging
import settings
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

id = settings.id
pwd = settings.pwd
path = settings.path
links = settings.links
count1 = settings.count1
count2 = settings.count2
asins = settings.asins
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] '
                           '- %(levelname)s: %(message)s', level=logging.INFO)
chrome_options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'permissions.default.stylesheet': 2,
    }
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument(f'--user-data-dir={path}')
chrome_options.add_argument("--disable-application-cache")
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
driver = webdriver.Chrome("chromedriver.exe", desired_capabilities=capa, options=chrome_options)  #
countlist1 = [count1 - 1, count1, count1 + 1, count1 + 2, count1 + 3, count1 + 4]
countlist2 = [count2 - 1, count2, count2 + 1, count2 + 2, count2 + 3, count2 + 4]


def discern(disUrl):
    data = {"userid": 'yux2023', "apikey": 'FpD7OQT8NJxOVKzmQtay',
            "data": base64.b64encode(requests.get(disUrl).content).decode()}
    result = requests.post('https://api.apitruecaptcha.org/one/gettext', json=data).json()
    logging.info(result)
    code = result["result"]
    return code


def sound():
    duration = 3000
    freq = 900
    winsound.Beep(freq, duration)


def deletAsin():
    global asins
    while True:
        try:
            a = input("Please enter the asin to be deleted:")
            asins.remove(a)
            logging.info(f"Removed {a} from asins")
        except Exception as e1:
            logging.error(e1)


if __name__ == '__main__':
    if input("Have you logged in:") == '1':
        driver.get("https://www.amazon.com/gp/your-account/order-history")
    driver.execute_script(f'window.open("{links[0]}");')
    time.sleep(5)
    handles = driver.window_handles
    count = 0
    captcha_count = 0
    driver.switch_to.window(handles[1])
    t1 = threading.Thread(target=deletAsin)
    t1.start()
    while True:
        for link in links:
            time.sleep(0.4)
            driver.get(link)
            wait = WebDriverWait(driver, 10, 0.2)
            wait.until(lambda driver: driver.find_element_by_xpath("//div[@data-index='9']"))
            text = driver.page_source
            html = HTML(text)
            now_asins = {}
            try:
                now_asins = set(html.xpath("//div/@data-asin"))-{'" data-index=',''}
            except:
                pass
            for count in range(2):
                if links.index(link) == 0:
                    countlist = countlist1
                else:
                    countlist = countlist2
                while now_asins.__len__() not in countlist:
                    # print(str(links.index(link)) + ': ' + str(now_asins.__len__()))
                    time.sleep(0.2)
                    text = driver.page_source
                    html = HTML(text)
                    try:
                        now_asins = set(html.xpath("//div/@data-asin"))-{'" data-index=',''}
                        if html.xpath("//input[@id='captchacharacters']"):
                            if captcha_count > 1:
                                t = threading.Thread(target=sound)
                                t.start()
                                logging.error("There is a problem with verification code recognition")
                                time.sleep(10)
                            else:
                                time.sleep(2)
                                captcha_count += captcha_count
                                captcha_url = html.xpath("//div[@class='a-box']//img/@src")[0]
                                field_keywords = discern(captcha_url)
                                driver.find_element_by_xpath("//input[@name='field-keywords']").send_keys(
                                    field_keywords)
                                driver.find_element_by_xpath("//button[@type='submit']").send_keys(Keys.ENTER)
                                captcha_count = 0
                                driver.refresh()
                    except:
                        pass
            # print(str(links.index(link)) + ': ' + str(now_asins.__len__()))
            try:
                count += 1
                buy_asins = now_asins - asins
                if buy_asins:
                    count = 0
                    t = threading.Thread(target=sound)
                    t.start()
                    for asin in buy_asins:
                        url = html.xpath(
                            f"//div[@data-asin='{asin}']//span[@data-component-type='s-product-image']/a/@href")[0]
                        driver.execute_script(f'window.open("https://www.amazon.com{url}");')
                        asins.update({asin})
                        logging.info(f"asin:<{asin}> Loading,Added it toasins")
                    buy_asins = {}
                    handle_temp = driver.window_handles[-1]
                    driver.switch_to.window(handle_temp)
                    try:
                        element = wait.until(EC.presence_of_element_located((By.ID, "buy-now-button")), message="111")
                        driver.execute_script(
                            'document.getElementById("buy-now-button").click()')
                        c = 30
                        while c > 0:
                            try:
                                c = c - 1
                                time.sleep(0.2)
                                driver.execute_script('document.getElementById("turbo-checkout-pyo-button").click()')
                            except:
                                pass
                        time.sleep(15)
                    except Exception as e3:
                        logging.info("Error in automatic purchase")
                        logging.error(e3)
                        time.sleep(15)
                if count % 90 == 0:
                    driver.switch_to.window(handles[0])
                    driver.refresh()
                    time.sleep(2)
                    html = HTML(driver.page_source)
                    try:
                        if html.xpath("//input[@type='password']"):
                            driver.find_element_by_id("ap_password").send_keys(pwd)
                            time.sleep(1)
                            driver.find_element_by_id("signInSubmit").send_keys(Keys.ENTER)
                            time.sleep(1)
                    except Exception as e2:
                        logging.error(e2)
                    driver.switch_to.window(handles[1])
            except Exception as e:
                logging.error(e)
