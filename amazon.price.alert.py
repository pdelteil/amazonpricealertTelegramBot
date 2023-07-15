import requests
from bs4 import BeautifulSoup
import time
import configparser
import telegram
import asyncio
import json

#PARAMS
SLEEP_TIME=0.25 #between attemps to fetch the price
RUN_EVERY=900 #seconds = 15 minutes
PRODUCTS_FILE= 'products.ini'
CONFIG_FILE = 'config.ini' 
PRICE_DIFFERENCE=1 #1 dollar, min price difference to notify
# Read params from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

TELEGRAM_TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
apiURL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

def get_price(url):
    price_value = 0
    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")
    
    if "co.suarezclothing.com" in url:
        price_span = soup.find("div",attrs={"class":'vtex-product-context-provider'})
        script_tag = soup.find('script', type='application/ld+json')
        json_data = json.loads(script_tag.string)
        price = json_data['offers']['lowPrice']

    if "www.amazon.com" in url:

        price_span = soup.find("span",attrs={"class":'a-price aok-align-center reinventPricePriceToPayMargin priceToPay'})

        if price_span is None:
            return -1
        price_text = price_span.find("span", attrs={"class": "a-offscreen"}).text
        # Remove currency symbols and convert to float
        price = float(price_text.replace('£', '').replace('$', '').replace(',', ''))

    return price

async def send_telegram_notification(item, previous_price, current_price, url):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = f"Price has changed for {item}\n"
    message += f"Previous price: {previous_price}\n"
    message += f"Current price: {current_price}\n"
    message += f"URL: {url}"

    await bot.send_message(chat_id=CHAT_ID, text=message)

async def check_price_change(id, name, previous_price, url):
    products_file = configparser.ConfigParser()
    products_file.read(PRODUCTS_FILE)

    try:
        current_price = get_price(url)
        if current_price == -1:
            print("Error with price")
            return False
        if current_price != previous_price:
            if abs(current_price - previous_price) >= PRICE_DIFFERENCE:
                print("Price has changed for", name)
                print("Previous price: ", previous_price)
                print("Current price: ", current_price)
                # Send notification to Telegram
                await send_telegram_notification(name, previous_price, current_price, url)
            # Update the price in the config file
            print("Price changed but not more than ", PRICE_DIFFERENCE)
            products_file.set('PRODUCTS', id,f'{name},${current_price},{url}')
            with open(PRODUCTS_FILE, 'w') as productsFile:
                products_file.write(productsFile)

        else:
            print("Price has not changed. Still ", current_price)

        return True
    except requests.exceptions.HTTPError as err:
        print("Error occurred during the request:", err)
        return False

async def main():
    products_file = configparser.ConfigParser()

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
