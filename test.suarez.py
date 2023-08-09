from bs4 import BeautifulSoup
import requests
import json
import sys

# Function to extract Product Title
def get_name(soup, url):
    try:
        title = ""
        if "suarezclothing.com" in url:
            title = soup.find("h1", attrs={"class":'vtex-store-components-3-x-productNameContainer mv0 t-heading-4'})
            title = title.find("span", attrs={"class":'vtex-store-components-3-x-productBrand'}).text

        title = title.strip().replace(",", " ")

    except AttributeError:
        title = ""

    return title
# Function to extract Product Price
def get_price_name(name,url):
    price = "-1"
    print(url)
    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Accept-Language': 'en-US, en;q=0.5'})

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        print("status 200") 
    else: 
        exit()
    #print(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # if name is empty -> get_name
    if name is None or len(name) == 0 :
        name = get_name(soup, url)
        print(name)

    if "suarezclothing.com" in url:
        #script_tag = soup.find('script', type='application/ld+json')
        div_tags =soup.find_all("div", attrs={"class":'vtex-flex-layout-0-x-flexColChild vtex-flex-layout-0-x-flexColChild--content__pdp pb0'})
         # Iterate over each div tag and find the desired element within it
        for idx, div_tag in enumerate(div_tags, 1):
        # Find the element with class 'vtex-product-price-1-x-currencyInteger' within the div tag
            currency_integer_element = div_tag.find("span", class_="vtex-product-price-1-x-currencyInteger")

            # Check if the element was found and print its text
            if currency_integer_element:
                print(f"Div tag {idx}:")
                print(currency_integer_element.text)
                print("=" * 50)
        #script_tag= script_tag.find("div", attrs={"class":'vtex-product-price-1-x-currencyInteger'})
        #print(script_tag)
        #if script_tag is not None:
        #    json_data = json.loads(script_tag.string)
        #    if 'offers' in json_data:
        #        price = str(json_data['offers']['lowPrice']).replace('.', '')
        #        print(f"Price: {price}")
        #    else:
        #        print("No 'offers' data found in the script tag.")
            #price = str(json_data['offers']['lowPrice']).replace('.','')

    # Remove currency symbols and convert to float
    price = price.replace('£', '').replace('$', '').replace(',', '')

    return price, name

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)

    # Get the URL from the command-line argument
    url = sys.argv[1]
    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Accept-Language': 'en-US, en;q=0.5'})
    #case product/size not available 
    #URL="https://co.suarezclothing.com/guantes-de-ciclismo-cortos-colombia-federacion/p?property__Color=Azul&skuId=2008"
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")

    # Function calls to display all necessary product information
    name=get_name(soup, url)

    print("Product Title =", name)
    print("Product Price =", get_price_name(name, url))
    print()
    name = ""
