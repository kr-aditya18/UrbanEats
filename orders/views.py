from django.http import JsonResponse
from django.shortcuts import render, redirect
from marketplace.views import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from menu.models import FoodItem
from decimal import Decimal
from .utils import generate_order_number
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import base64
import json


def make_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(i) for i in obj]
    return obj


def send_notification(mail_subject, mail_template, context):
    """Reusable email sender."""
    message = render_to_string(mail_template, context)
    to_email = context.get('to_email')
    mail = EmailMessage(mail_subject, message, to=[to_email])
    mail.content_subtype = 'html'
    mail.send()


def get_paypal_access_token():
    """
    Exchanges PAYPAL_CLIENT_ID + PAYPAL_SECRET for a Bearer access token.
    Reads from settings.py:
        PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
        PAYPAL_SECRET    = config('PAYPAL_SECRET')      ← matches your settings.py
        PAYPAL_MODE      = 'sandbox'
    """
    client_id     = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_SECRET          # ✅ matches your settings.py
    mode          = getattr(settings, 'PAYPAL_MODE', 'sandbox')

    base_url = (
        "https://api-m.sandbox.paypal.com"
        if mode == 'sandbox'
        else "https://api-m.paypal.com"
    )

    response = requests.post(
        f"{base_url}/v1/oauth2/token",
        headers={
            "Accept":          "application/json",
            "Accept-Language": "en_US",
        },
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
    )

    data = response.json()
    if 'access_token' not in data:
        raise Exception(f"Could not get PayPal access token: {data}")

    return data['access_token']


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    if cart_items.count() <= 0:
        return redirect('marketplace')

    # If user goes back to edit, delete the pending unordered order and clear session
    if request.method == 'GET' and 'order_number' in request.session:
        try:
            old_order = Order.objects.get(
                order_number=request.session['order_number'],
                is_ordered=False
            )
            request.session['billing_data'] = {
                'first_name': old_order.first_name,
                'last_name':  old_order.last_name,
                'phone':      old_order.phone,
                'email':      old_order.email,
                'address':    old_order.address,
                'country':    old_order.country,
                'city':       old_order.city,
                'pin_code':   old_order.pin_code,
            }
            old_order.delete()
        except Order.DoesNotExist:
            pass
        del request.session['order_number']

    cart_amounts = get_cart_amounts(request)
    subtotal    = cart_amounts['subtotal']
    total_tax   = cart_amounts['tax']
    grand_total = cart_amounts['grand_total']
    tax_data    = cart_amounts['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name     = form.cleaned_data['first_name']
            order.last_name      = form.cleaned_data['last_name']
            order.phone          = form.cleaned_data['phone']
            order.email          = form.cleaned_data['email']
            order.address        = form.cleaned_data['address']
            order.country        = form.cleaned_data['country']
            order.city           = form.cleaned_data['city']
            order.pin_code       = form.cleaned_data['pin_code']
            order.user           = request.user
            order.total          = float(grand_total)
            order.tax_data       = make_serializable(tax_data)
            order.total_tax      = float(total_tax)
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            request.session['order_number'] = order.order_number

            cart_items_display = []
            for item in cart_items:
                cart_items_display.append({
                    'food_title': item.fooditems.food_title,
                    'price':      item.fooditems.price,
                    'quantity':   item.quantity,
                    'amount':     item.fooditems.price * item.quantity,
                })

            context = {
                'order':       order,
                'cart_items':  cart_items_display,
                'subtotal':    subtotal,
                'total_tax':   total_tax,
                'grand_total': grand_total,
                'tax_dict':    tax_data,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)

    billing_data = request.session.pop('billing_data', {})
    return render(request, 'orders/place_order.html', {
        'billing_data': billing_data,
        'subtotal':     subtotal,
        'grand_total':  grand_total,
        'tax_dict':     tax_data,
    })


@csrf_exempt
def create_order(request):
    try:
        order_number = request.session.get('order_number')
        if not order_number:
            return JsonResponse({"error": "No order found in session"}, status=400)

        order        = Order.objects.get(order_number=order_number, user=request.user)
        access_token = get_paypal_access_token()

        order_res = requests.post(
            "https://api-m.sandbox.paypal.com/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type":  "application/json"
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": str(round(order.total, 2))
                    }
                }]
            }
        )

        order_data = order_res.json()
        if 'id' not in order_data:
            return JsonResponse({"error": "Failed to create PayPal order", "details": order_data}, status=500)

        return JsonResponse({"id": order_data['id']})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)
    except Exception as e:
        import traceback
        print("FULL ERROR:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def capture_order(request, order_id):
    try:
        access_token = get_paypal_access_token()

        capture_res = requests.post(
            f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type":  "application/json"
            }
        )
        capture_data = capture_res.json()

        if capture_data.get('status') == 'COMPLETED':
            order_number = request.session.get('order_number')
            order        = Order.objects.get(order_number=order_number, user=request.user)
            transaction  = capture_data['purchase_units'][0]['payments']['captures'][0]

            # Save Payment
            payment = Payment.objects.create(
                user=request.user,
                transaction_id=transaction['id'],
                payment_method='PayPal',
                amount=transaction['amount']['value'],
                status=transaction['status'],
            )

            # Update Order
            order.payment    = payment
            order.is_ordered = True
            order.status     = 'Accepted'
            order.save()

            # Save OrderedFood + collect vendors
            cart_items   = Cart.objects.filter(user=request.user)
            vendors_seen = set()

            for item in cart_items:
                ordered_food          = OrderedFood()
                ordered_food.order    = order
                ordered_food.payment  = payment
                ordered_food.user     = request.user
                ordered_food.fooditem = item.fooditems
                ordered_food.quantity = item.quantity
                ordered_food.price    = item.fooditems.price
                ordered_food.amount   = item.fooditems.price * item.quantity
                ordered_food.save()
                vendors_seen.add(item.fooditems.vendor)

            # Confirmation email to customer
            ordered_food_to_customer = OrderedFood.objects.filter(order=order)
            customer_context = {
                'user':         request.user,
                'order':        order,
                'payment':      payment,
                'ordered_food': ordered_food_to_customer,
                'to_email':     order.email,
            }
            send_notification(
                'Your Order Has Been Placed',
                'orders/emails/order_confirmation.html',
                customer_context
            )

            # Email each vendor
            for vendor in vendors_seen:
                vendor_food = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
                vendor_context = {
                    'order':        order,
                    'payment':      payment,
                    'ordered_food': vendor_food,
                    'vendor':       vendor,
                    'to_email':     vendor.user.email,
                }
                send_notification(
                    'You Have Received a New Order',
                    'orders/emails/order_received_vendor.html',
                    vendor_context
                )

            # Clear cart + session
            cart_items.delete()
            del request.session['order_number']

            capture_data['order_number'] = order.order_number
            capture_data['payment_id']   = payment.transaction_id

        return JsonResponse(capture_data)

    except Exception as e:
        import traceback
        print("FULL ERROR:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id   = request.GET.get('payment_id')

    try:
        order        = Order.objects.get(order_number=order_number, is_ordered=True)
        payment      = Payment.objects.get(transaction_id=payment_id)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal     = sum(item.amount for item in ordered_food)

        context = {
            'order':        order,
            'payment':      payment,
            'ordered_food': ordered_food,
            'subtotal':     subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except Exception:
        return redirect('home')