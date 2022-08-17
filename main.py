from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
from tqdm import tqdm
import traceback

crawl_delay = 2


# define delay function to avoid rate limit
def delay_function(ping):
    start = time.time()
    ping
    end = time.time()
    time.sleep(max(0, crawl_delay - (start - end)))


chrome_options = Options()
chrome_options.add_argument("--headless")

# avoid detection
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# avoid detection
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

driver.implicitly_wait(2)
driver.maximize_window()

delay_function(driver.get('https://bol.com/'))

# close cookies window
if '--headless' not in chrome_options.arguments:
    delay_function(
        driver.find_element(By.XPATH, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]').click())
    delay_function(driver.find_element(By.CLASS_NAME, 'js_category_menu_button').click())

# get categories
cats = [BeautifulSoup(cat.get_attribute('innerHTML'), 'html.parser').span for cat in
        driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li')][1:]

# get category links
cats_links = [link.get_attribute('href') for link in
              driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li/a')]

# get subcategories from categories
subcats_links = []
for category in cats_links[2:]:
    driver.get(category)
    subcats = BeautifulSoup(driver.find_element(By.ID, 'mainContent').get_attribute('innerHTML'),
                            'html.parser').findAll('li')

    links = [subcat.a['href'] for subcat in subcats if 'Alle' not in subcat.text]

    subcats_links += links

date = datetime.date.today()
week = datetime.date.today().isocalendar().week

# get products from subcategories
products = pd.DataFrame(
    columns=['date', 'week', 'timestamp', 'cat1', 'cat2', 'cat3', 'cat4', 'page', 'position', 'id', 'seller', 'brand',
             'name', 'sponsored', 'link', 'rating', 'reviews', 'delivery', 'price', 'stock'])

for subcat in tqdm(subcats_links[:100], desc="Subcategories", position=0):  # remove filter!
    driver.get('https://bol.com{}'.format(subcat))

    cat1 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[1].text if \
        driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li') else "NA"
    cat2 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[2].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 2 else "NA"
    cat3 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[3].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 3 else "NA"
    cat4 = driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')[4].text if \
        len(driver.find_elements(By.XPATH, '//ul[@data-test="breadcrumb"]/li')) > 4 else "NA"

    # iterate through pages
    for page in range(1, 2):
        if page != 1:
            try:
                driver.get('https://bol.com{0}?page={1}'.format(subcat, page))
            except Exception:
                traceback.print_exc()
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
            products = pd.concat([products, pd.Series(product).to_frame().T], ignore_index=True)

        # remember current tab
        current_window = driver.current_window_handle

        # add products to basket
        links_to_baskets = [product.get_attribute('href') for product in
                            driver.find_elements(By.XPATH, '//a[@data-test="add-to-basket"]')]

        for product in links_to_baskets:
            try:
                driver.execute_script('window.open(arguments[0]);', product)
            except Exception:
                traceback.print_exc()
                pass

        # close tabs
        for handle in driver.window_handles[::-1]:
            driver.switch_to.window(handle)
            if handle != current_window:
                driver.close()

        # return to original tab
        driver.switch_to.window(current_window)

        # get product stock from order basket
        driver.get('https://www.bol.com/nl/order/basket.html')

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
                                                                                         {
                                                                                             'selected': 'selected'}) else 1
            }

            products.loc[products['link'] == output['link'], 'stock'] = output['stock']

        # remove all products from basket
        for product in driver.find_elements(By.XPATH, '//a[@data-test="remove-link-large"]'):
            driver.execute_script('window.open(arguments[0]);', product.get_attribute('href'))
            driver.switch_to.window(driver.window_handles[-1])
            if driver.current_window_handle != current_window:
                driver.close()
            driver.switch_to.window(current_window)

products.to_excel('Bol_{}.xlsx'.format(datetime.datetime.today().date()))

