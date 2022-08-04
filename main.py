from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get('https://bol.com/')

driver.find_element(By.XPATH, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]').click()

cats = driver.find_elements(By.CLASS_NAME, 'wsp-sub-nav-group__link')

cats_links = [category.get_attribute('href') for category in cats]

driver.find_element(By.CLASS_NAME, 'wsp-main-nav__item').click()

# [cat.click() for cat in driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li')]

cats = driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li')

cats[2].click()
ActionChains(driver).move_to_element(subcats[5]).perform()

subcats
for cat in cats:
    cat.click()

    subcats = driver.find_elements(By.CLASS_NAME, 'wsp-sub-nav-group__title')
    for subcat in subcats:
        ActionChains(driver).move_to_element(subcat).perform()

ActionChains(driver).move_to_element(driver.find_element(By.CLASS_NAME, 'wsp-sub-nav-group__title')).perform()
