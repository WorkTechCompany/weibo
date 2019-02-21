import random
import constants
from lxml import etree
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cardcode import CardCode
import time
import os


def getphone():

    while True:
        phone_url = 'http://huoyun888.cn/api/do.php?action=getPhone&token=903e64acc9b2a43985353bc2e0809c9c&sid=11818&phoneType=CMCC'
        response = requests.get(phone_url).text
        if '余额不足' in response:
            url = 'http://huoyun888.cn/api/do.php?action=cancelAllRecv&token=903e64acc9b2a43985353bc2e0809c9c&sid=11818phoneType=CMCC'
            requests.get(url)
        else:
            phone = response.split('|')[1]
            return phone


def putSentMessage(phone, message_content, addressee):
    author = 'daidaicu'
    putSentMessage = 'http://huoyun888.cn/api/do.php?action=putSentMessage&phone=' + phone + '&sid=' + '11818' + '&message=' + message_content + '&recvPhone=' + addressee + '&token=903e64acc9b2a43985353bc2e0809c9c' + '&author=' + author
    # print(putSentMessage)
    while True:
        response = requests.get(putSentMessage).text
        time.sleep(3)
        if '1' in response:
            print(response)
            return phone
        if '提交失败' in response:
            return -1


def getSentMessageStatus(phone):
    flag = True
    getSentMessageStatus = 'http://huoyun888.cn/api/do.php?action=getSentMessageStatus&phone=' + phone + '&sid=' + '11818' + '&token=903e64acc9b2a43985353bc2e0809c9c'
    # print(getSentMessageStatus)
    while True:
        response = requests.get(getSentMessageStatus).text
        time.sleep(3)
        print(response)
        if '1' in response:
            flag = False
            print('发送成功')
            return flag
        if '发送失败' in response:
            return flag
        if '手机号不在线或手机号已释放，可尝试检查发码是否成功。' in response:
            return flag

def save_image(image_url):
    try:
        os.makedirs("./image")
    except:
        pass
    finally:
        response = requests.get(image_url[0])
        print(response.content)
        address = "./image/code.png"
        with open(address, 'wb') as f:
            f.write(response.content)
        return address

def sendmessage(user, password, name):
    url = 'https://login.sina.com.cn/signup/signin.php'

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
    browser.implicitly_wait(3)
    # browser.set_page_load_timeout(10)  # 10秒
    # wait = WebDriverWait(browser, 30)

    browser.find_element("name", "username").send_keys(user)
    browser.find_element("name", "password").send_keys(password)
    time.sleep(3)
    browser.find_elements_by_xpath("//input[@class='W_btn_a btn_34px']")[0].click()

    html = browser.page_source
    sel = etree.HTML(html)
    while True:
        captcha_url = sel.xpath("//img[@id='check_img']/@src")
        address = save_image(captcha_url)
        result = cardcode.__vaild__(address)
        browser.find_elements_by_xpath("//input[@id='door']")[0].clear()
        browser.find_element("name", "door").send_keys(result)
        browser.find_elements_by_xpath("//input[@class='W_btn_a btn_34px']")[0].click()
        time.sleep(2)
        if browser.current_url == 'http://my.sina.com.cn/':
            break
        html = browser.page_source
        sel = etree.HTML(html)
        check_result = sel.xpath("//span[@class='form_prompt']/i/text()")[0]
        if check_result != '输入的验证码不正确':
            break

    # browser.find_elements_by_xpath("//li[@class='l_pdt l_pdt1']/a/span")[0].click()
    # time.sleep(2)
    url = 'http://control.blog.sina.com.cn/myblog/htmlsource/blog_notopen.php?uid=' + name + '&version=7'
    browser.get(url)
    browser.refresh()

    while True:
        try:
            time.sleep(3)
            phone = getphone()
            browser.find_elements_by_xpath(
                "//div[@class='focus open-blog-phone-border']/input | //div[@class='open-blog-phone-border']/input")[
                0].clear()
            browser.find_elements_by_xpath(
                "//div[@class='focus open-blog-phone-border']/input | //div[@class='open-blog-phone-border']/input")[
                0].send_keys(phone)
            time.sleep(3)
            html = browser.page_source
            sel = etree.HTML(html)
            error = sel.xpath("//p[@id='blogPhoneNumError']/text()")[0]
            print(error)
            if len(error) > 1 or error != '名称不能为空':
                continue
        except:
            print(phone)
            time.sleep(3)
            html = browser.page_source
            sel = etree.HTML(html)
            messaging = sel.xpath("//div[@class='send-msg-tip']/p/text()")
            if len(messaging) == 0:
                continue
            message_content = messaging[0].split('送')[1].split('到')[0]
            addressee = messaging[0].split('到')[1].split('进')[0]

            print(message_content)
            print(addressee)

            phone = putSentMessage(phone, message_content, addressee)
            if phone == -1:
                continue
            flag = getSentMessageStatus(phone)
            if flag:
                browser.find_elements_by_xpath("//input[@id='blogPhoneNum']")[0].clear()
                browser.find_elements_by_xpath("//input[@id='blogPhoneNum']")[0].send_keys(phone)
            else:
                break
    browser.find_elements_by_xpath("//a[@class='btn']")[0].click()
    browser.quit()
    time.sleep(3)

if __name__ == '__main__':
    cardcode = CardCode()
    # result = cardcode.__vaild__(b'pin.png')
    # print(result)
    card_number = []
    with open('blog.txt', 'r') as f:
        for i in f.readlines():
            card_number.append(i.replace('卡号:', '').strip())

        for card in card_number:
            result = card.split('----')
            user = result[0]
            password = result[1]
            name = result[2]
            sendmessage(user, password, name)
