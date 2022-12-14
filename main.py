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
import os.path
from git import Repo
import re

crawl_delay = 2


# define delay function to avoid rate limit
def delay_function(ping):
    start = time.time()
    ping
    end = time.time()
    time.sleep(max(0, crawl_delay - (start - end)))


def git_push():
    try:
        repo = Repo(r'.git')
        repo.git.add(all=True)
        repo.index.commit('Update {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))  # commit message
        origin = repo.remote(name='origin')
        origin.push()
        print('Pushed to GitHub')
    except Exception:
        traceback.print_exc()


print('Initializing driver...')

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

print('Opening bol.com...')
delay_function(driver.get('https://bol.com/'))

# close cookies window
if '--headless' not in chrome_options.arguments:
    delay_function(
        driver.find_element(By.XPATH,
                            '//*[@id="modalWindow"]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]').click())
    delay_function(driver.find_element(By.CLASS_NAME, 'js_category_menu_button').click())

# get categories
cats = [BeautifulSoup(cat.get_attribute('innerHTML'), 'html.parser').span for cat in
        driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li')][1:]

# get category links
cats_links = [link.get_attribute('href') for link in
              driver.find_elements(By.XPATH, '//ul[@class="wsp-category-nav-ab"]/li/a')]

# get subcategories from categories
subcats_links = []
for category in tqdm(cats_links, desc='Get subcategories'):
    driver.get(category)
    subcats = BeautifulSoup(driver.find_element(By.ID, 'mainContent').get_attribute('innerHTML'),
                            'html.parser').findAll('li')

    links = ['https://bol.com{}'.format(subcat.a['href']) for subcat in subcats if 'Alle' not in subcat.text]

    subcats_links += links

subcats_links = list(set(subcats_links))

date = datetime.date.today()
week = datetime.date.today().isocalendar().week

# get products from subcategories
products = pd.DataFrame(
    columns=['date', 'week', 'timestamp', 'cat1', 'cat2', 'cat3', 'cat4', 'cat_link', 'page', 'position', 'id',
             'seller', 'brand',
             'name', 'sponsored', 'link', 'rating', 'reviews', 'delivery', 'price', 'stock'])

cats_df = pd.DataFrame()
# if existing output exists, then only select subcategories not already in output
# if os.path.exists(r"Output/Bol.com_{}.xlsx".format(datetime.datetime.today().date())):
#     if len(pd.read_excel(r"Output/Bol.com_{}.xlsx".format(datetime.datetime.today().date()))) > 0:
#         df_existing = pd.read_excel(r"Output/Bol.com_{}.xlsx".format(datetime.datetime.today().date()))
#         existing_links = list(df_existing.cat_link.unique())
#         subcats_links = [link for link in subcats_links if link not in existing_links]
#
#
# pd.Series(subcats_links).to_excel('subcategories.xlsx')
# driver.get(subcats_links[-1])
#
# len(set(subcats_links))
#
#         missing_stock = df_existing[df_existing.stock.isna()].cat_link.unique() # check for products with missing stock
#         subcats_links = list(set([*subcats_links,*missing_stock])) # add cat links where stock is missing

start_time = datetime.datetime.now()
print('{}: Start scraping'.format(start_time))

# run through subcategories to get products
try:
    for subcat in tqdm(subcats_links, desc="Get products", position=0):
        cats_df = pd.concat([cats_df, pd.Series({datetime.datetime.now(): subcat})])
        print(subcat)
        driver.get(subcat)

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
                                       attrs={'data-test': 'plazaseller-link'}).text.strip().replace('Verkoop door ',
                                                                                                     '')
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
                    'cat_link': subcat,
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
                        'div', attrs={'data-test': 'rating-stars'}) else "NA",
                    'reviews': (soup.find('div',
                                          attrs={'data-test': 'rating-stars'})['data-count'] if soup.find('div', attrs={
                        'data-test': 'rating-stars'}).has_attr('data-count') else "NA") if soup.find('div', attrs={
                        'data-test': 'rating-stars'}) else "NA",
                    'delivery': "".join(
                        soup.find('div', attrs={'data-test': 'delivery-notification'}).findAll(text=True,
                                                                                               recursive=False)).strip() if soup.find(
                        'div', attrs={'data-test': 'delivery-notification'}) else "NA",
                    'price': soup.find('span', attrs={'data-test': 'price'}).text if soup.find('span', attrs={
                        'data-test': 'price'}) else "NA",
                    'price_original': soup.find('del', attrs={'data-test': 'from-price'}).text if soup.find('del',
                                                                                                            attrs={
                                                                                                                'data-test': 'from-price'}) else "NA"
                }

                product['price'] = product['price'].replace('\n  ', '.').strip()
                products = pd.concat([products, pd.Series(product).to_frame().T], ignore_index=True)

            # remember current tab
            current_window = driver.current_window_handle

            # add products to basket
            # links_to_baskets = [product.get_attribute('href') for product in
            #                     driver.find_elements(By.XPATH, '//a[@data-test="add-to-basket"]')]

            # work in progress --------------------------------------------------------------------
            # links_to_baskets = []
            for product in driver.find_elements(By.XPATH, '//ul[@data-test="products"]/li'):
                soup = BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser')
                if soup.find('a', {'data-test': 'add-to-basket'}):
                    link = soup.find('a', {'data-test': 'add-to-basket'})['href']
                    try:
                        driver.execute_script('window.open(arguments[0]);', link)
                    except Exception:
                        print('Error adding to basket: {}'.format(link))
                        traceback.print_exc()

                elif soup.find('a', {'class': 'product-seller__link'}):
                    strings = re.split(r'\?|\&', soup.find('a', {'class': 'product-seller__link'})['data-js-href'])
                    offerId = "".join(re.findall(r"\d+", *[string for string in strings if 'offerId' in string]))
                    productId = "".join(re.findall(r"\d+", *[string for string in strings if 'productId' in string]))
                    link = '/nl/order/basket/addItems.html?productId={0}&offerId={1}&quantity=1'.format(productId,
                                                                                                        offerId)
                    try:
                        driver.execute_script('window.open(arguments[0]);', link)
                    except Exception:
                        print('Error adding to basket: {}'.format(link))
                        traceback.print_exc()

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

        completed = [subcat for subcat in subcats_links[:subcats_links.index(subcat) + 1] if
                     subcat in products.cat_link.unique()]
        skipped = [subcat for subcat in subcats_links[:subcats_links.index(subcat) + 1] if
                   subcat not in products.cat_link.unique()]
        print('Completed: {1}. Skipped: {2}.'.format(len(completed), len(skipped)))

    print('{0}: Scraping completed. \nTotal time: {1}'.format(datetime.datetime.now(),
                                                              datetime.datetime.now() - start_time))
except Exception:
    print("{}: Error occurred while getting products".format(datetime.datetime.now()))
    traceback.print_exc()

# output to excel
if os.path.exists(r"Output/Bol.com_{}.xlsx".format(datetime.datetime.today().date())):
    current_excel = pd.read_excel(r"Output/Bol.com_{}.xlsx".format(datetime.datetime.today().date()))
    new_excel = pd.concat([current_excel.iloc[:, 1:], products], ignore_index=True)
    new_excel.to_excel('Output/Bol.com_{}.xlsx'.format(datetime.datetime.today().date()))
else:
    products.to_excel('Output/Bol.com_{}.xlsx'.format(datetime.datetime.today().date()))

print('Pushed to Excel')
git_push()  # push to Github
