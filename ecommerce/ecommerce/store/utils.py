import json
from .models import *

def CookieData(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        
    items = []
    order = {'get_cart_total':0, 'get_item_total':0, 'shipping':False}
    cartItems = order['get_item_total']
    
    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_item_total'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'items':items, 'order':order, 'cartItems':cartItems}

def cartData(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, create = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_item_total
    else:
        cookie_data = CookieData(request)
        items = cookie_data['items']
        order = cookie_data['order']
        cartItems = cookie_data['cartItems']

    return {'items':items, 'order':order, 'cartItems':cartItems}

def guestOrder(request, data):
    print('User is not logged-in')
    print('COOKIES: ',request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    cookieItem = CookieData(request)
    items = cookieItem['items']

    customer, created = Customer.objects.get_or_create(
        email = email
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id']) 
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        ) 
        
    return customer, order