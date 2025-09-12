import requests
from app1.models import Review
from .models import Product, Cart, Order
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import auth
import razorpay
from django.conf import settings



# Create your views here.

def index(request):
    books = Product.objects.filter(is_avail=True).order_by("-id")
    param = {
        "books": books,
    }
    return render(request, 'index.html', param)

def logreg(request):
    if request.method == "POST":
        if request.POST["type"] == "login":
            username = request.POST["username"]
            password = request.POST["password"]
            user1 = auth.authenticate(request, username=username, password=password)

            if user1 is not None:
                auth.login(request, user1)
                return redirect("/")
            else:
                return HttpResponse("<script>alert('Invalid Data, try again!!');window.location.href='/logreg/';</script>")
        elif request.POST["type"] == "registration":
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            recaptcha_response = request.POST.get("g-recaptcha-response")
            data = {
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response

            }
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            response = requests.post(verify_url, data=data)
            final_result = response.json()

            if final_result.get("success"):
                if User.objects.filter(username=username).exists():
                    return HttpResponse("<script>alert('Username taken!!');window.location.href='/logreg/';</script>")
                else:
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    new_user.save()
                    return HttpResponse("<script>alert('Registration Success!!');window.location.href='/logreg/';</script>")
            else:
                return HttpResponse("<script>alert('Captcha Verification Failed!!');window.location.href='/logreg/';</script>")
    return render(request, 'logreg.html')


def LogOut(request):
    auth.logout(request)
    return redirect("/")


def all_books(request):
    books = Product.objects.filter(is_avail=True).order_by("-id")
    param = {
        "books": books,
    }
    return render(request, 'all_books.html', param)


def book_details(request, id):
    book = Product.objects.get(id=id)
    all_reviews = Review.objects.filter(book__id=id)
    try:
        if Cart.objects.filter(book__id=id, user=request.user, ordered=True).exists():
            allow = True
        else:
            allow =False
    except:
        pass
    context = {
        "book": book,
        "all_reviews": all_reviews,
        "allow": allow
    }
    return render(request, "book_details.html", context)


@login_required
def myCart(request):
    cart_total = 0
    my_cart = Cart.objects.filter(user=request.user, ordered=False)
    if not my_cart:
        return HttpResponse("<script>alert('Cart is empty!!');window.location.href='/';</script>")
    for p in my_cart:
        cart_total += p.sub_total
    context = {
        "my_cart": my_cart,
        "cart_total": cart_total
    }
    return render(request, "myCart.html", context)


@login_required
def add_to_cart(request, id):
    book = Product.objects.get(id=id)
    if Cart.objects.filter(book__id=id, ordered=False, user=request.user).exists():
        my_book = Cart.objects.get(book__id=id, ordered=False, user=request.user)
        my_book.quantity += 1
        my_book.sub_total += book.price
        my_book.save()
    else:
        new_cart = Cart.objects.create(
            user = request.user,
            book = book,
            sub_total = book.price
        )
        new_cart.save()
    return redirect("/myCart")


@login_required
def update_cart(request):
    my_id = request.GET["id"]
    my_qty = int(request.GET["qty"])

    try:
        my_book = Cart.objects.get(id=my_id, user=request.user, ordered=False)
        my_book.quantity = my_qty
        my_book.sub_total = my_book.book.price * my_qty
        my_book.save()
        return redirect("/myCart")
    except:
        return HttpResponse("<script>alert('Invalid Request!!');window.location.href='/myCart/';</script>")


@login_required
def remove_from_cart(request):
    my_id = int(request.GET["id"])

    try:
        my_book = Cart.objects.get(id=my_id, user=request.user, ordered=False)
        my_book.delete()
        return redirect("/myCart")
    except:
        return HttpResponse("<script>alert('Invalid Request!!');window.location.href='/myCart/';</script>")

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def checkout(request):
    if request.method == "POST":
        full_name = request.POST["billing_first_name"] + " " + request.POST["billing_last_name"]
        address = request.POST["billing_address_1"]
        city = request.POST["billing_city"]
        state = request.POST["billing_state"]
        zip = request.POST["billing_postcode"]
        phone = request.POST["billing_phone"]
        payment_mode = request.POST["ship-address"]
        cart_total = request.POST["order_total"]
        full_address = address + "," + city + "," + state
        if payment_mode == "COD":
            temp_cart = Cart.objects.filter(user=request.user, ordered=False)
            new_order = Order.objects.create(
                user = request.user,
                full_name = full_name,
                phone = phone,
                address = full_address,
                zip = zip,
                order_total = int(cart_total),
                ordered = True,
                payment_type = "COD"
            )
            new_order.my_books.add(*temp_cart)
            new_order.save()
            for item in temp_cart:
                item.ordered = True
                item.order_status = "Delivered" if item.book.format == "E-Book" else "Ordered"
                item.save()
            return redirect("order_success", id=new_order.id)
        elif payment_mode == "online":
            cart_total = int(request.POST["order_total"])
            currency = "INR"
            amount = cart_total * 100

            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                               currency=currency,
                                                               payment_capture='0'))
            razorpay_order_id = razorpay_order['id']
            callback_url = 'http://127.0.0.1:8000/payment_handler/'

            temp_cart = Cart.objects.filter(user=request.user, ordered=False)
            new_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=full_address,
                zip=zip,
                order_total=int(cart_total),
                payment_type="Online",
                online_payment_id=razorpay_order_id
            )
            new_order.my_books.add(*temp_cart)
            new_order.save()

            context = {}
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url

            request.session["order_id"] = new_order.id

            return render(request, "payment.html", context)
    else:
        cart_total = 0
        my_cart = Cart.objects.filter(user=request.user, ordered=False)
        for p in my_cart:
            cart_total += p.sub_total
        context = {
            "my_cart": my_cart,
            "cart_total": cart_total
        }
        return render(request, "checkout.html", context)


@csrf_exempt
def payment_handler(request):
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                if request.session["direct"]:
                    my_book_id = request.session["book_id"]
                    book = Product.objects.get(id=my_book_id)
                    amount = book.price * 100
                    try:
                        # capture the payment
                        razorpay_client.payment.capture(payment_id, amount)

                        temp_cart = Cart.objects.create(
                            user=request.user,
                            direct_buy=True,
                            book=book,
                            sub_total=book.price
                        )
                        temp_cart.save()

                        full_name = request.session["full_name"]
                        full_address = request.session["address"]
                        phone = request.session["phone"]
                        zip_code = request.session["zip_code"]

                        new_order = Order.objects.create(
                            user=request.user,
                            full_name=full_name,
                            phone=phone,
                            address=full_address,
                            zip=zip_code,
                            order_total=int(book.price),
                            payment_type="Online",
                            online_payment_id=razorpay_order_id,
                            ordered=True
                        )
                        new_order.my_books.add(temp_cart)
                        new_order.save()

                        temp_cart.ordered = True
                        temp_cart.order_status = "Delivered" if temp_cart.book.format == "E-Book" else "Ordered"
                        temp_cart.save()
                        return redirect("order_success", id=new_order.id)
                    except:

                        # if there is an error while capturing payment.
                        return HttpResponse(
                            "<script>alert('Payment Capture Failed!!');window.location.href='/myCart';</script>")
                else:
                    my_order_id = request.session["order_id"]
                    my_order = Order.objects.get(id=my_order_id)
                    amount = my_order.order_total * 100
                    try:
                        # capture the payment
                        razorpay_client.payment.capture(payment_id, amount)
                        my_order.ordered = True
                        my_order.save()
                        temp_cart = Cart.objects.filter(user=request.user, ordered=False)
                        for item in temp_cart:
                            item.ordered = True
                            item.order_status = "Delivered" if item.book.format == "E-Book" else "Ordered"
                            item.save()
                        return redirect("order_success", id=my_order.id)
                    except:

                        # if there is an error while capturing payment.
                        return HttpResponse("<script>alert('Payment Capture Failed!!');window.location.href='/myCart';</script>")
            else:

                # if signature verification fails.
                return HttpResponse("<script>alert('Payment Capture Failed!!');window.location.href='/myCart';</script>")
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


@login_required
def order_success(request, id):
    order = get_object_or_404(Order, id=id, user=request.user, ordered=True)
    return render(request, 'order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, ordered=True)
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def reviews(request):
    user = request.user
    book_id = request.POST["book_id"]
    review = request.POST["review"]
    review_book = Product.objects.get(id=book_id)

    try:
        check_review = Review.objects.get(user=user, book=review_book)
        check_review.review = review
        check_review.save()
        return HttpResponse(
            f"<script>alert('Review Updated!!');window.location.href='/book_details/{book_id}';</script>")
    except:
        new_review = Review.objects.create(
            user = user,
            book = review_book,
            review = review
        )
        new_review.save()
        return HttpResponse(f"<script>alert('Review Added!!');window.location.href='/book_details/{book_id}';</script>")


@login_required
def delete_review(request, id):
    get_review = Review.objects.get(id=id, user=request.user)
    get_review.delete()
    return HttpResponse(f"<script>alert('Review Deleted!!');window.location.href='/all_books/';</script>")


@login_required
def buy_now(request, id):
    if request.method == "POST":
        my_book = Product.objects.get(id=id)
        full_name = request.POST["billing_first_name"] + " " + request.POST["billing_last_name"]
        address = request.POST["billing_address_1"]
        city = request.POST["billing_city"]
        state = request.POST["billing_state"]
        zip = request.POST["billing_postcode"]
        phone = request.POST["billing_phone"]
        payment_mode = request.POST["ship-address"]
        cart_total = request.POST["order_total"]
        full_address = address + "," + city + "," + state
        if payment_mode == "COD":
            temp_cart = Cart.objects.create(
                user=request.user,
                direct_buy=True,
                book=my_book,
                sub_total=my_book.price
            )
            temp_cart.save()

            new_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=full_address,
                zip=zip,
                order_total=int(cart_total),
                ordered=True,
                payment_type="COD"
            )
            new_order.my_books.add(temp_cart)
            new_order.save()

            temp_cart.ordered = True
            temp_cart.order_status = "Delivered" if temp_cart.book.format == "E-Book" else "Ordered"
            temp_cart.save()
            return redirect("order_success", id=new_order.id)
        elif payment_mode == "online":
            cart_total = int(request.POST["order_total"])
            my_book_id = id
            currency = "INR"
            amount = cart_total * 100

            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                               currency=currency,
                                                               payment_capture='0'))
            razorpay_order_id = razorpay_order['id']
            callback_url = 'http://127.0.0.1:8000/payment_handler/'

            context = {}
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url

            request.session["direct"] = True
            request.session["full_name"] = full_name
            request.session["address"] = full_address
            request.session["phone"] = phone
            request.session["zip_code"] = zip
            request.session["book_id"] = my_book_id

            return render(request, "payment.html", context)
    else:
        user = request.user
        book = get_object_or_404(Product, id=id)
        Cart.objects.filter(user=user, direct_buy=True, ordered=False).delete()
        context = {
            "direct": True,
            "sub_total": book.price,
            "cart_total": book.price,
            "book": book
        }
        return render(request, "checkout.html", context)
