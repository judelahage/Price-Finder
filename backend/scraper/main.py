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

