from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
from tqdm import tqdm

crawl_delay = 2

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.implicitly_wait(20)
driver.maximize_window()

driver.get('https://bol.com/')

# driver.find_element(By.XPATH, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]').click()
# driver.find_element(By.CLASS_NAME, 'js_category_menu_button').click()

# get categories
cats = [BeautifulSoup(cat.get_attribute('innerHTML'), 'html.parser').span for cat in
        driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li')][1:]

# get category links
cats_links = [link.get_attribute('href') for link in
              driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li/a')]

# get subcategories from categories
subcats_links = []
for category in cats_links[1:]:
    driver.get(category)
    subcats = BeautifulSoup(driver.find_element(By.ID, 'mainContent').get_attribute('innerHTML'),
                            'html.parser').findAll('li')

    links = [subcat.a['href'] for subcat in subcats]

    subcats_links += links

date = datetime.date.today()
week = datetime.date.today().isocalendar().week

# get products from subcategories
products = []
for subcat in tqdm(subcats_links):  # remove filter!

    start = time.time()
    driver.get('https://bol.com{}'.format(subcat))
    end = time.time()
    time.sleep(max(0, crawl_delay - (start - end)))

    cat1 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[1].text if \
        driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[1] else "NA"
    cat2 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[2].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 2 else "NA"
    cat3 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[3].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 3 else "NA"
    cat4 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[4].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 4 else "NA"

    # iterate through pages
    for page in tqdm(range(1, 2)):
        if page != 1:
            try:
                start = time.time()
                driver.get('https://bol.com{0}?page={1}'.format(subcat, page))
                end = time.time()
                time.sleep(max(0, crawl_delay - (start - end)))
            except:
                pass

        # iterate through products
        for i in range(len(driver.find_elements(By.XPATH, '//ul[@data-test="products"]/li'))):
            product = driver.find_elements(By.XPATH, '//ul[@data-test="products"]/li')[i]
            soup = BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser')

            if soup.find('span', attrs={'class': 'product-seller__name'}):
                seller = soup.find('span', attrs={'class': 'product-seller__name'}).text
            elif soup.find('div', attrs={'data-test': 'plazaseller-link'}):
                seller = soup.find('div',
                                   attrs={'data-test': 'plazaseller-link'}).text.strip().replace('Verkoop door ', '')
            else:
                seller = 'NA'

            product = {
                'date': date,
                'week': week,
                'timestamp': datetime.datetime.now().time(),
                'cat1': cat1,
                'cat2': cat2,
                'cat3': cat3,
                'cat4': cat4 if cat4 else "NA",
                'page': page,
                'position': i,
                'id': product.get_attribute('data-id'),
                'seller': seller,
                'brand': soup.find('a', attrs={'data-test': 'party-link'}).text if soup.find('a', attrs={
                    'data-test': 'party-link'}) else "NA",
                'name': soup.find('a', attrs={'data-test': 'product-title'}).text if soup.find('a', attrs={
                    'data-test': 'product-title'}) else "NA",
                'sponsored': True if soup.find('div', attrs={'data-test': 'sponsored-product'}) else False,
                'link': soup.find('a', attrs={'data-test': 'product-title'})['href'] if soup.find('a', attrs={
                    'data-test': 'product-title'}).has_attr('href') else "NA",
                'rating': soup.find('div', attrs={'data-test': 'rating-stars'})['title'].split(' ')[1] if soup.find(
                    'div', attrs={'data-test': 'rating-stars'}).has_attr('title') else "NA",
                'reviews': soup.find('div',
                                     attrs={'data-test': 'rating-stars'})['data-count'] if soup.find('div', attrs={
                    'data-test': 'rating-stars'}).has_attr('data-count') else "NA",
                'delivery': "".join(soup.find('div', attrs={'data-test': 'delivery-notification'}).findAll(text=True,
                                                                                                           recursive=False)).strip() if soup.find(
                    'div', attrs={'data-test': 'delivery-notification'}) else "NA",
                'price': soup.find('span', attrs={'data-test': 'price'}).text if soup.find('span', attrs={
                    'data-test': 'price'}) else "NA"
            }

            product['price'] = product['price'].replace('\n  ', '.').strip()

            products.append(product)

        # remember current tab
        current_window = driver.current_window_handle

        # add products to basket (in new tab)
        for product in tqdm(driver.find_elements(By.XPATH, '//a[@data-test="add-to-basket"]'), position=0, leave=True):
            start = time.time()
            driver.execute_script('window.open(arguments[0]);', product.get_attribute('href'))
            end = time.time()
            time.sleep(max(0, crawl_delay - (start - end)))

        # close tabs
        for handle in driver.window_handles[::-1]:
            driver.switch_to.window(handle)
            if handle != current_window:
                driver.close()

        # return to original tab
        driver.switch_to.window(current_window)

# turn into dataframe
df_products = pd.DataFrame(products)
df_products['id'] = [product[-2] for product in df_products['link'].str.split('/')]

# get product stock from order basket
driver.get('https://www.bol.com/nl/order/basket.html')

# for product in driver.find_elements(By.XPATH, '//div[@class="shopping-cart"]/div'):

# remember current tab
current_window = driver.current_window_handle

# iterate through products and set order quantity to maximum
for link in driver.find_elements(By.NAME, 'id'):
    driver.execute_script('window.open(arguments[0]);',
                          'https://www.bol.com/nl/order/basket/updateItemQuantity.html?id={}&quantity=500'.format(
                              link.get_attribute('value')))
    driver.switch_to.window(driver.window_handles[-1])
    if driver.current_window_handle != current_window:
        driver.close()
    driver.switch_to.window(current_window)

# reload
driver.get('https://www.bol.com/nl/order/basket.html')

# get product stocks
product_stock = []
for product in driver.find_elements(By.XPATH, '//div[@class="product"]'):
    soup = BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser')

    output = {
        'link': soup.find('a', {'class': 'product-details__title'})['href'] if soup.find('a', {
            'class': 'product-details__title'}) else "NA",
        'stock': soup.find('option', {'selected': 'selected'}).text if soup.find('option',
                                                                                 {'selected': 'selected'}) else 1
    }

    # output['name'] = "".join(line.strip() for line in output['name'].split("\n"))

    product_stock.append(output)

df_products = df_products.merge(pd.DataFrame(product_stock), how='outer', on='link')

# GRAVEYARD ======================================================================================================
#
# driver.find_elements(By.XPATH, '//a[@data-test="add-to-basket"]')[1].click()

# ActionChains(driver).move_to_element(subcats[5]).perform()
# ActionChains(driver).move_to_element(driver.find_element(By.CLASS_NAME, 'wsp-sub-nav-group__title')).perform()


# subcats = driver.find_elements(By.CLASS_NAME, 'wsp-sub-nav-group')
#
# subsubcats = [name.text for subcat in subcats for name in
#               BeautifulSoup(subcat.get_attribute('innerHTML'), 'html.parser').find_all('a')]
#
# subsubcats_links = [name['href'] for subcat in subcats for name in
#                     BeautifulSoup(subcat.get_attribute('innerHTML'), 'html.parser').find_all('a')]
#
# driver.get('https://bol.com/{}'.format(subsubcats_links[3]))
#
# # [product.click() for product in driver.find_elements(By.CLASS_NAME, 'product-title')]

#
# current_url = driver.current_url
#
#
# webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable(product)).click()
# # driver.execute_script("arguments[0].click();", product)
# # product.click()  # add to basket
#
# # WebDriverWait(driver, 10).until(lambda driver: driver.current_url != current_url)
#
# # close_button = driver.find_element(By.XPATH, '//div[@data-test="modal-window-close"]')
# WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, '//div[@data-test="modal-window-close"]')))
# try:
#     driver.execute_script("arguments[0].click();",
#                           driver.find_element(By.XPATH, '//div[@data-test="modal-window-close"]'))
# except:
#     pass
# # WebDriverWait(driver, 10).until(lambda driver: driver.current_url == current_url)
#
# while 'modal_open' in str(driver.current_url):
#     # try:
#     webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
#
#     # except None:
#     #     continue
#
#
# for i in range(len(driver.find_elements(By.NAME, 'quantity'))):
#     order = driver.find_elements(By.NAME, 'quantity')[i]
#     if order.get_attribute('data-quantity-option'):
#         pass
#     else:
#         # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(order))
#
#         # remember current tab
#         current_window = driver.current_window_handle
#
#         link = 'https://www.bol.com/nl/order/basket/updateItemQuantity.html?id={}&quantity=500'.format(
#             driver.find_elements(By.NAME, 'id')[i].get_attribute('value'))
#
#         driver.execute_script('window.open(arguments[0]);', link)
#
#         # close tabs
#         for handle in driver.window_handles[::-1]:
#             driver.switch_to.window(handle)
#             if handle != current_window:
#                 driver.close()
#
#         # return to original tab
#         driver.switch_to.window(current_window)
#
#         #
#         # if order.find_elements(By.CSS_SELECTOR, 'option')[-1].text.isnumeric():
#         #     # stock = order.find_elements(By.CSS_SELECTOR, 'option')[-1].text   # faster by getting text instead of clicking
#         #     order.find_elements(By.CSS_SELECTOR, 'option')[-1].click()
#         # elif order.find_elements(By.CSS_SELECTOR, 'option')[-1].text == 'meer':
#         #     order.find_elements(By.CSS_SELECTOR, 'option')[-1].click()
#         #     driver.find_element(By.XPATH, '//input[@type="tel"]').send_keys('1000')
#         #     driver.find_element(By.XPATH, '//input[@type="tel"]/following-sibling::div').click()
