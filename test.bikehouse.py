from bs4 import BeautifulSoup
import requests

# Function to extract Product Title
def get_title(soup):
    
    try:
        title = soup.find("h1", attrs={"class":'product_title entry-title'})
        title_value = title.string
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""   

    return title_string

# Function to extract Product Price
def get_price(soup):

    try:
        price1 = soup.find('span', class_='price_varies')
        if price1 is not None:
            price = price1.find('ins').find('span', class_='money').text
        else:
            price = soup.find('span', class_='money').text

    except AttributeError:
        price = ""  

    return price

if __name__ == '__main__':

    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    # List of URLs
    URLs = [
    "https://bikehouse.co/collections/cables-y-candados-bicicletas/products/cadenas-cables-y-candados-de-seguridad-bicicletas-ulac-ulac-diesel",
    "https://bikehouse.co/collections/outlet/products/jersey-de-ciclismo-mujer-colombia-federacion?variant=44474153828585" ]

    for url in URLs:
        webpage = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "lxml")

        # Function calls to display all necessary product information
        print("Product Title =", get_title(soup))
        print("Product Price =", get_price(soup))
        print()
