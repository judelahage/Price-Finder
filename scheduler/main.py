from requests import post
URL = "http://localhost:5000/updateTrackedProducts"
#hits the url once a day in order to update the product information once a day
if __name__ == "__main__":
    print("Sending request to", URL)
    response = post(URL)
    print("Status code", response.status_code)

