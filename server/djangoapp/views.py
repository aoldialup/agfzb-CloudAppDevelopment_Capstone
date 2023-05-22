from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from datetime import datetime
from .restapis import POST_DEALERSHIP_REVIEW_URL
import json

def get_dealerships(request):
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context={ "dealerships": get_dealers_from_cf() })
        
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        return render(request, 'djangoapp/dealer_details.html', context={ "reviews": get_dealer_reviews_from_cf(dealer_id) })

def add_review(request, dealer_id: int):
    if request.method == "GET":
        context = {
            "cars": CarModel.objects.all(),
            "dealer": get_dealers_from_cf(dealer_id)[0],
        }
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        form = request.POST
        review = {
            "name": f"{request.user.first_name} {request.user.last_name}",
            "dealership": dealer_id,
            "review": form["content"],
            "purchase": "true" if form.get("purchase_check") == 'on' else "false",
        }
        if form.get("purchase_check"):
            car = CarModel.objects.get(pk=form["car"])
            review["purchase_date"] = datetime.strptime(form.get("purchase_date"), "%m/%d/%Y").isoformat() 
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
          
        print(post_request(POST_DEALERSHIP_REVIEW_URL, review));
    
    return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')

def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')

def login_request(request): 
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password) 
        if user is not None:
            login(request, user)
            return render(request, 'djangoapp/index.html')
        else:
            return render(request, 'djangoapp/index.html')
    else:
        return render(request, 'djangoapp/index.html')

def logout_request(request):
    logout(request)
    print("Log out the user `{}`".format(request.user.username))
    return render(request, 'djangoapp/index.html')

def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            print(f'{username} has registered')
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html')
        else:
            return render(request, 'djangoapp/index.html')