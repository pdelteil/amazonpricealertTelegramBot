import requests
from bs4 import BeautifulSoup
import time
import configparser
import telegram  
import asyncio
import json

#PARAMS
SLEEP_TIME=0.25 #between attemps to fetch the price
RUN_EVERY=300 #seconds = 5 minutes
PRODUCTS_FILE= 'products.ini'
CONFIG_FILE = 'config.ini' 
PRICE_DIFFERENCE=1 #1 dollar, min price difference to notify
# Read params from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

TELEGRAM_TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
apiURL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

def get_name(soup, url):
    try:
        if "co.suarezclothing.com" in url:
            title = soup.find("h1", attrs={"class":'vtex-store-components-3-x-productNameContainer mv0 t-heading-4'})
            title = title.find("span", attrs={"class":'vtex-store-components-3-x-productBrand'}).text
            title = title.strip().replace(",", " ")

        if "www.amazon.com" in url:
            title = soup.find("span", attrs={"id":'productTitle'})
            title = title.string
            title = title.strip().replace(",", " ")
        if "cyclewear.com.co" or "www.bikeexchange.com.co" in url:
            title = soup.find("h1", attrs={"class":'h3 CProductHeader-title t-productHeaderHeading'})
            title = title.string
            title = title.strip().replace(",", " ")

    except AttributeError:
        title = ""

    return title

def get_price_name(name,url):
    price = "0"
    print(len(name))
    print(url)
    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")

    # if name is empty -> get_name
    if name is None or len(name) == 0 :
        name = get_name(soup, url)
        print(name)

    if "www.amazon.com" in url:
        price_span = soup.find("span",attrs={"class":'a-price aok-align-center reinventPricePriceToPayMargin priceToPay'})

        if price_span is None:
            return "-1", name
        price_text = price_span.find("span", attrs={"class": "a-offscreen"}).text
        # Remove currency symbols and convert to float
        price = float(price_text.replace('£', '').replace('$', '').replace(',', ''))

    if "co.suarezclothing.com" in url:
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag is not None:
            json_data = json.loads(script_tag.string)
            price = json_data['offers']['lowPrice']
    if "cyclewear.com.co" in url or "www.bikeexchange.com.co" in url:
        div_element = soup.find('div', class_='yotpo-main-widget')
        # Extract the 'data-price' attribute value
        price = div_element.get('data-price')

    return price, name

async def send_telegram_notification(item, previous_price, current_price, url):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = f"Price has changed for <b> {item} </b>\n"
    message += f"Previous price: {previous_price}\n"
    message += f"Current price: {current_price}\n"
    message += f"URL: {url}"

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')

async def check_price_change(id, name, previous_price, url):
    products_file = configparser.RawConfigParser()
    products_file.read(PRODUCTS_FILE)

    try:
        current_price, name_new = get_price_name(name, url)
        current_price = float(current_price)
        if current_price == -1:
            print("Error with price")
            return False
        if len(name)==0:
            print("Name updated from ", name, "to: ", name_new)
            products_file.set('PRODUCTS', id,f'{name_new},${current_price},{url}')
            with open(PRODUCTS_FILE, 'w') as productsFile:
                products_file.write(productsFile)

        if current_price != previous_price:
            if abs(current_price - previous_price) >= PRICE_DIFFERENCE:
                print("Price has changed for", name_new)
                print("Previous price: ", previous_price)
                print("Current price: ", current_price)
                # Send notification to Telegram
                await send_telegram_notification(name_new, previous_price, current_price, url)
            # Update the price in the config file
            print("Price changed but not more than ", PRICE_DIFFERENCE)
            products_file.set('PRODUCTS', id,f'{name_new},${current_price},{url}')
            with open(PRODUCTS_FILE, 'w') as productsFile:
                products_file.write(productsFile)

        else:
            print("Price has not changed. Still ", current_price)

        return True
    except requests.exceptions.HTTPError as err:
        print("Error occurred during the request:", err)
        return False

async def main():
    products_file = configparser.RawConfigParser()

    while True:
        # Read product information from config file
        products_file.read(PRODUCTS_FILE)

        products = products_file.items('PRODUCTS')

        for id, info in products:
            name, price, url = info.split(',')
            price=float(price.replace('$', ''))

            while True:
                status = await check_price_change(id, name, price, url)
                if not status:
                        print(".")
                else:
                   break
                time.sleep(SLEEP_TIME)
        print("Waiting ", RUN_EVERY)
        time.sleep(RUN_EVERY)

# Run the main function
asyncio.run(main())
