import requests
import os
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import logging
from dotenv import load_dotenv

load_dotenv()

NLU_URL = os.getenv('NLU_URL')
NLU_API_KEY = os.getenv('NLU_API_KEY')
NLU_URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/c1e5f399-ab56-41d8-bd95-c3b176a7d31f"

GET_DEALERSHIP_URL = "https://us-east.functions.appdomain.cloud/api/v1/web/30e0adc7-a28d-4345-923c-9d7b60860107/dealership-package/get-dealership.json"
GET_DEALERSHIP_REVIEW_URL = "https://us-east.functions.appdomain.cloud/api/v1/web/30e0adc7-a28d-4345-923c-9d7b60860107/dealership-package/get-review.json"
POST_DEALERSHIP_REVIEW_URL = "https://us-east.functions.appdomain.cloud/api/v1/web/30e0adc7-a28d-4345-923c-9d7b60860107/dealership-package/post-review.json"

def get_dealers_from_cf(id: int = None):
    results = []

    if id == None:
        json_result = get_request(GET_DEALERSHIP_URL)
    else:
        json_result = get_request(GET_DEALERSHIP_URL, id=id)

    if json_result:
        dealers = json_result["dealerships"]
        for dealer_doc in dealers:
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj) 
    return results

def get_dealer_reviews_from_cf(id: int):
    json_result = get_request(GET_DEALERSHIP_REVIEW_URL, id=id)
    results = []

    if json_result:    
        for review_doc in json_result['entries']:
            if review_doc is not None:
                review = DealerReview(
                    dealership = review_doc.get("dealership", ""),
                    name = review_doc.get("name", ""),
                    purchase = review_doc.get("purchase", ""),
                    review = review_doc.get("review", ""),
                    purchase_date = review_doc.get("purchase_date", ""),
                    car_make = review_doc.get("car_make", ""),
                    car_model = review_doc.get("car_model", ""),
                    car_year = review_doc.get("car_year", ""),
                    sentiment = analyze_review_sentiments(review_doc.get("review", "")),
                    id = review_doc.get("id", "")
                )
                results.append(review)
    return results

def analyze_review_sentiments(text: str):
    params = json.dumps({"text": text, "features": {"sentiment": {}}})
    response = requests.post(NLU_URL, data=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', NLU_API_KEY))
    print(response)
    try:
        return response.json()['sentiment']['document']['label']
    except KeyError:
        return 'neutral'

def get_request(url, **kwargs):
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        print("Network exception occurred")
    finally:
        print(f'GET from {url} with {kwargs} returned {response.status_code}')
        return response.json()

def post_request(url: str, review):
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, params=review)
        print(response)
    except:
        print("Network exception occurred")
    finally:
        json_data = {} if not response.text else json.loads(response.text)
        print(f"POST to {url} with {review} returned {response.status_code}") 
        return response.json() 
        #return json_data