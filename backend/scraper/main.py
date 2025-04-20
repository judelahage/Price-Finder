import asyncio
from playwright.async_api import async_playwright
import json
import os
from amazon import getProduct as getAmazonProduct
from requests import post

AMAZON = "https://amazon.com" #going to be getting data specifically from amazon, other websites can be added
URLS = {
    AMAZON: {
        "searchFieldQuery": 'input[name = "field-keywords"]',
        "searchButtonQuery": 'input[value = "Go"]',
        "productSelector": "div.s-card-container"
    }
}
availableUrls = URLS.keys()

def load_auth():
    FILE = os.path.join("Scraper", "auth.json")
    with open(FILE, "r") as f:
        return json.load(f)

#bright data credentials are in auth.json file with the following keys: "username", "password", and "host"
#connecting to bright data browser
cred = load_auth()
auth  = f'{cred["username"]}:{cred["password"]}'
browserUrl = f'wss://{auth}@{cred["host"]}'

async def search(metadata, page, searchText): #filling input field
    print(f"Searching for {searchText} on {page.url}")
    searchFieldQuery = metadata.get("searchFieldQuery")
    searchButtonQuery = metadata.get("searchButtonQuery")
    
    if searchFieldQuery and searchButtonQuery:
        print("Filling input field")
        searchBox = await page.wait_for_selector(searchFieldQuery)
        await searchBox.type(searchText)
        print("Pressing search button")
        button = await page.wait_for_selector(searchButtonQuery)
        await button.click()
    else:
        raise Exception("Could not search")
    await page.wait_for_load_state()
    return page

async def getProducts(page, searchText, selector, getProduct): #retrieves products based on search query
    print("Retreiving products.")
    productDivs = await page.query_selector_all(selector)
    validProducts = []
    words = searchText.split(" ")
    
    async with asyncio.TaskGroup() as tg:
        for div in productDivs:
            async def task(pDiv):
                product = await getProduct(pDiv)
                if not product["price"] or not product["url"]:
                    return
                
                for word in words:
                    if not product["name"] or word.lower() not in product["name"].lower():
                        break;
                    
                else:
                    validProducts.append(product)
                
            tg.create_task(task(div))
        
    return validProducts

def saveResults(results): #saves search results
    data = {"restuls": results}
    FILE = os.path.join("Scraper", "results.json")
    with open(FILE, "w") as f:
        json.dump(data, f)
            
def postResults(results, endpoint, searchText, source): #posts results to backend so they get saved to database
    headers = {
        "Content-Type": "application/json"
    }
    data = {"data": results, "searchText": searchText, "source": source}
    print("Sending request to", endpoint)
    response  = post("http://localhost:5000" + endpoint, headers = headers, json = data)
    print("Status code: ", response.status_code)

async def main(url, searchText, responseRoute): #connecting to browser, accessing amazon and getting information from it
    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return
    
    async with async_playwright() as pw:
        print('Connecting to browser.')
        browser = await pw.chromium.connect_over_cdp(browserUrl)
        page = await browser.new_page()
        print("Connected")
        await page.goto(url, timeout = 120000)
        print("Loaded intial page.")
        searchPage = await search(metadata, page, searchText)
        
        def func(x): return None
        if url == AMAZON:
            func = getAmazonProduct
        else:
            raise Exception('Invalid URL')
        
        results = await getProducts(searchPage, searchText, metadata["productSelector"], func)
        print("Saving results.")
        postResults(results, responseRoute, searchText, url)
        
        await browser.close()

if __name__ == "__main__":
    #testing
    asyncio.run(main(AMAZON, "ryzen 9 7950x 3d"))
