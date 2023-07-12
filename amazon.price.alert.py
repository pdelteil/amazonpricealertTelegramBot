import requests
from bs4 import BeautifulSoup
import time
import configparser
import telegram
import asyncio

#PARAMS
SLEEP_TIME=0.25 
RUN_EVERY=900 #seconds = 15 minutes
PRODUCTS_FILE= 'products.ini'
CONFIG_FILE = 'config.ini'

# Read params from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

TELEGRAM_TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
apiURL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

def get_amazon_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.amazon.com/',
        }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element that contains the price information
    price_whole_element = soup.find(class_='a-price-whole')
    price_decimal_element = soup.find(class_='a-price-fraction')

    if price_decimal_element is None or price_whole_element is None:
        return -1
    # Extract the price text
    price_text = price_whole_element.get_text() + price_decimal_element.get_text()

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
        current_price = get_amazon_price(url)
        if current_price == -1:
            print("Error with price")
            return False
        if current_price != previous_price:
            print("Price has changed for", name)
            print("Previous price: ", previous_price)
            print("Current price: ", current_price)
            # Send notification to Telegram
            await send_telegram_notification(name, previous_price, current_price, url)
            # Update the price in the config file
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

    while True:
        # Read product information from config file
        products_file = configparser.ConfigParser()
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
