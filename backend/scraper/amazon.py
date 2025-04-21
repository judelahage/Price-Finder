from asyncio import gather
#gets all the information from amazon
async def getStock(productDiv):
    elements = await productDiv.query_selector_all('.a-size-base')
    filteredElements = [element for element in elements if 'stock' in await element.inner_text()]
    return filteredElements

async def getProduct(productDiv):
    imageElementFuture = productDiv.query_selector('img.s-image')
    nameElementFuture = productDiv.query_selector('h2 a span')
    priceElementFuture = productDiv.query_selector('span.a-offscreen')
    urlElementFuture = productDiv.query_selector('a.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')

    imageElement, nameElement, priceElement, urlElement = await gather(imageElementFuture, nameElementFuture, priceElementFuture, urlElementFuture)
    
    imageUrl = await imageElement.get_attribute('src') if imageElement else None
    productName = await nameElement.inner_text() if nameElement else None
    try:
        print((await priceElement.inner_text()).replace("$", "").replace(",","").strip())
        productPrice = float((await priceElement.inner_text()).replace("$", "").replace(",", "").strip()) if priceElement else None
    except:
        productPrice = None
    productUrl = "/".join((await urlElement.get_attribute('href')).split("/")[:4]) if urlElement else None
    
    return {"img": imageUrl, "name": productName, "price": productPrice, "url": productUrl}
