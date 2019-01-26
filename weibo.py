import random
import constants
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

import time

phone_url = 'http://huoyun888.cn/api/do.php?action=getPhone&token=903e64acc9b2a43985353bc2e0809c9c&sid=1000'
response = requests.get(phone_url).text
phone = response.split('|')[1]

url = 'https://weibo.com/signup/signup.php'

chrome_options = Options()
# 在Linux需要禁用sandbox
chrome_options.add_argument('--no-sandbox')
# 谷歌文档提到需要加上这个属性来规避bug
# chrome_options.add_argument('--disable-gpu')
# 隐藏滚动条, 应对一些特殊页面
# chrome_options.add_argument('--hide-scrollbars')
# 不加载图片, 提升速度
# chrome_options.add_argument('blink-settings=imagesEnabled=false')
# https安全问题
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--headless')
# 添加代理
# chrome_options.add_argument("--proxy-server=socks5://" + PROXY)
# 随机user_agent
user_agent = random.choice(constants.USER_AGENTS)
chrome_options.add_argument('user-agent=%s' % user_agent)
# logging.info("opening chrome, catalog_url:%s", catalog_url)

browser = webdriver.Chrome(chrome_options=chrome_options)
browser.get(url)
browser.implicitly_wait(10)
wait = WebDriverWait(browser, 30)

password = 'renming'

browser.find_element("name", "username").send_keys(phone)
browser.find_element("name", "passwd").send_keys(password)
Select(browser.find_element_by_xpath("//select[@class='sel year']")).select_by_index("20")
Select(browser.find_element_by_xpath("//select[@class='sel month']")).select_by_index("3")
Select(browser.find_element_by_xpath("//select[@class='sel day']")).select_by_index("3")

browser.find_elements_by_xpath("//a[@class='W_btn_big'][1]")[0].click()
time.sleep(3)
html = browser.page_source
sel = etree.HTML(html)
message_content = sel.xpath("//dd[@class='msg_info']/span[1]/text()")[0]
addressee = sel.xpath("//dd[@class='msg_info']/span[2]/text()")[0]

putSentMessage = 'http://huoyun888.cn/api/do.php?action=putSentMessage&phone=' + phone + '&sid=' + '1000' + '&message=' + message_content + '&recvPhone=' + addressee + '&token=903e64acc9b2a43985353bc2e0809c9c'

print(message_content)
print(addressee)

getSentMessageStatus = 'http://huoyun888.cn/api/do.php?action=getSentMessageStatus&phone=' + phone + '&sid=' + '1000' + '&token=903e64acc9b2a43985353bc2e0809c9c'

while True:
    response = requests.get(getSentMessageStatus).text
    if '1' in response:
        print(response)
        break
