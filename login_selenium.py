from seleniumwire import webdriver  # 注意用 seleniumwire 以便抓包
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import logging
from colorama import Fore, Style
import colorama

def LoginWithSelenium(username, password):
    colorama.init(autoreset=True)
    LOGIN_URL = 'https://www.baomi.org.cn/login?siteId=95'  # 登录页URL
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    token = None
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)  # 等待页面加载

        # 输入用户名和密码（根据实际页面元素调整）
        driver.find_element(By.CSS_SELECTOR, '.input_item_phone input').send_keys(username)
        driver.find_element(By.CSS_SELECTOR, '.password-item input[type=password]').send_keys(password)

        # 拖动滑块
        slider = driver.find_element(By.CSS_SELECTOR, '.el-slider__button-wrapper')
        slider_bar = driver.find_element(By.CSS_SELECTOR, '.el-slider__runway')
        width = slider_bar.size['width']

        actions = ActionChains(driver)
        actions.click_and_hold(slider).pause(0.2)

        move_distance = width  # 可以适当减小，防止超界
        step = move_distance // 10
        for i in range(10):
            actions.move_by_offset(step, 0).pause(0.05)
        actions.move_by_offset(move_distance % 10, 0).pause(0.3)
        actions.release().perform()

        driver.find_element(By.CSS_SELECTOR, '.loginBtn').click()  # 假设登录按钮是submit

        # 等待登录请求发出
        time.sleep(3)

        # 遍历所有请求，找到登录接口的响应
        for request in driver.requests:
            if request.response and 'loginInNew.do' in request.url:
                if request.response.status_code != 200:
                    logging.error(f"{Fore.RED}登录请求失败，状态码: {request.response.status_code}{Style.RESET_ALL}")
                    raise Exception(f"登录请求失败，状态码: {request.response.status_code}")
                response_data = json.loads(request.response.body.decode())
                token = response_data.get('token')
                if not token:
                    error_msg = response_data.get('error', {}).get('errorMsg', '未知错误')
                    logging.error(f"{Fore.RED}登录失败: {error_msg}{Style.RESET_ALL}")
                    raise Exception(f"登录失败: {error_msg}")
                break
    finally:
        driver.quit()
    return token

if __name__ == "__main__":
    USERNAME = 'foo'
    PASSWORD = 'bar'
    token = LoginWithSelenium(USERNAME, PASSWORD)
    print('登录token:', token)
