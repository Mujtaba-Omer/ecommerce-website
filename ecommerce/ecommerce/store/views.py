from math import fabs
from cv2 import exp
from django.shortcuts import render
from numpy import product
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import CookieData, cartData, guestOrder
# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    context = {'products':products, 'cartItems':cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,'store/cart.html',context)

def checkout(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('productId: ',productId)
    print('action: ', action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, create = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1) 
    elif action=='remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()    

    return JsonResponse('item was add..', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, create = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    order.transaction_id = transaction_id
    total = float(data['form']['total'])

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == 'True':
        ShippingInfo.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode']
        )

    return JsonResponse('Payment complete', safe=False)
