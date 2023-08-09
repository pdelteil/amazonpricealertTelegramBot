from bs4 import BeautifulSoup
import requests

# Function to extract Product Title
def get_title(soup):
    
    try:
        # Outer Tag Object
        # Find the div element with the class 'yotpo-main-widget'
        title = soup.find("h1", attrs={"class":'h3 CProductHeader-title t-productHeaderHeading'})
        #title = soup.find("div", attrs={"data-react-class":'ProductAdvertPrice'})
        # Inner NavigableString Object
        title_value = title.string

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""   

    return title_string

# Function to extract Product Price
def get_price(soup):

    try:
        div_element = soup.find('div', class_='yotpo-main-widget')
        # Extract the 'data-price' attribute value
        price = div_element.get('data-price')

    except AttributeError:
        price = ""  

    return price

if __name__ == '__main__':

    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    # The webpage URL
    #URL = "https://www.amazon.com/Sony-PlayStation-Pro-1TB-Console-4/dp/B07K14XKZH/"
    URL = "https://cyclewear.com.co/a/llantas-para-bicicletas-de-ruta/continental/antioquia/sabaneta/llanta-de-ruta-continental-grand-prix-4-season/100261521?variant_id=789188"

    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")

    # Function calls to display all necessary product information
    print("Product Title =", get_title(soup))
    print("Product Price =", get_price(soup))
    print()
