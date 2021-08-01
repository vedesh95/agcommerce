from django.shortcuts import redirect, render, HttpResponse
from django.http.response import HttpResponse
from django.contrib.auth import authenticate,login,logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from .models import * 
import datetime

from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

# Create your views here.
def getdictionary(request):
    products=Product.objects.all()
    username = request.user
    order, created = Order.objects.get_or_create(username=username, complete=False)
    items = order.orderitem_set.all()
    cartItems=order.get_cart_items
    context={'items':items,'order':order,"cartItems":cartItems,"products":products}
    return context
def store(request):
    if request.user.is_authenticated:
        context=getdictionary(request)
    else:
        products=Product.objects.all()
        context = {'products':products,"cartItems":0}
    return render(request,'store/store.html',context)

def viewproduct(request,id):
    product=Product.objects.get(id=int(id))
    if request.user.is_authenticated:
        context=getdictionary(request)
        context["product"]=product
        return render(request, 'store/viewproduct.html',context)
    context={"product":product}
    return render(request, 'store/viewproduct.html',context)

def cart(request):
    if request.user.is_authenticated:
        context=getdictionary(request)
        return render(request, 'store/cart.html', context)
    return redirect('/login')
    
def updateItem(request,id,action):
    if request.user.is_authenticated:
        productId = int(id) 
        action = action
        flag=0
        if(action=='addhome'):
            action='add' 
            flag=1
        print('Action:', action)
        print('Product:', productId)

        username = request.user
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(username=username, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()
        if flag==1:
            messages.success(request,'Item is added to cart')
            return redirect('/viewproduct/'+str(id))
        return redirect("/cart")
    else:
        return redirect('/login')

def checkout(request):
    if request.user.is_authenticated:
        context=getdictionary(request)
        return render(request, 'store/checkout.html', context)
    return redirect('/login')

def processorder(request):
    if request.user.is_authenticated and request.method=="POST":
        city=request.POST.get('city')
        address=request.POST.get('address')
        state=request.POST.get('state')
        zipcode=request.POST.get('zipcode')
        print("city=",city,"state=",state,address,zipcode)
        if(city=='' or address=='' or state=='' or zipcode==''):
            messages.warning(request,"Pleasde fill all details")
            return redirect('/checkout')
        username = request.user
        order, created = Order.objects.get_or_create(username=username, complete=False)
        order.address=address+city+state+zipcode
        order.save()
        amount=order.get_cart_total
        cust_id=request.user.username
        param_dict = {
                'ORDER_ID': str(order.id)+'D'+str(datetime.datetime.now().timestamp()),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': cust_id,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'https://agcommerce.herokuapp.com/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'store/paytm.html', {'param_dict': param_dict})
    else:
        return redirect('/checkout')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    
    if verify:
        if response_dict['RESPCODE'] == '01':
            id=response_dict["ORDERID"].partition('D')
            id=int(id[0])
            order = Order.objects.get(pk=int(id))
            order.complete = True
            order.transaction_id=datetime.datetime.now().timestamp()
            order.date_ordered=datetime.datetime.now()
            order.save()
            return render(request,"store/transactionsucessfull.html",{'cartItems':0})
    print(response_dict)
    return HttpResponse('order was not successful because<br>' + response_dict['RESPMSG']+'<br><a href="/checkout">Go back to checkout</a>')

def signup(request):
    if request.method=="POST":
        username=request.POST.get('username')
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')

        if pass1!=pass2:
            messages.warning(request,'Password is not matching')
            return redirect('/signup')

        try:
            if User.objects.get(username=username):
                messages.warning(request,"username is already taken")
                return redirect('/signup')
        except Exception as Identifier:
            pass

        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email is already taken")
                return redirect('/signup')
        except Exception as Identifier:
            pass

        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.save()
        messages.success(request,"User is Created Please Login")
        return redirect('/login')
    cartItems=0
    context = {"cartItems":cartItems}
    return render(request,"store/signup.html",context)
def handlelogin(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        myuser=authenticate(username=username,password=password)
        if myuser is not None:
            login(request,myuser)
            return redirect('/')
        else:
            messages.warning(request,"Invalid Credentials")
    return render(request,"store/login.html")
def handlelogout(request):
    logout(request)
    messages.success(request,'Successfully Logged Out')
    return redirect('/login')

def usertransactions(request):
    if request.user.is_authenticated:    
        orderdict=[]
        for order in Order.objects.filter(username=request.user,complete=True):
            listobj=[]
            for item in order.orderitem_set.all():    
                product=Product.objects.get(pk=item.product_id)
                listobj.append({"name":product.name,"desc":product.desc,"image":product.image,"price":product.price,"quantity":item.quantity})
            orderdict.append({"products":listobj,"date_ordered":order.date_ordered,"address":order.address,"orderid":order.id,"total":order.get_cart_total})
        orderdict.reverse()
        context=getdictionary(request)
        return render(request,"store/adminorders.html",{'orderdict':orderdict,'cartItems':context['cartItems']})
    return redirect('/login')
        
def adminorders(request):
    if request.user.is_authenticated and request.user.is_superuser:    
        orderdict=[]
        for order in Order.objects.filter(complete=True):
            listobj=[]
            for item in order.orderitem_set.all():    
                product=Product.objects.get(pk=item.product_id)
                listobj.append({"name":product.name,"desc":product.desc,"image":product.image,"price":product.price,"quantity":item.quantity})
            orderdict.append({"products":listobj,"date_ordered":order.date_ordered,"address":order.address,"orderid":order.id,"total":order.get_cart_total})
        orderdict.reverse()
        context=getdictionary(request)
        return render(request,"store/adminorders.html",{'orderdict':orderdict,'cartItems':context['cartItems']})
    return HttpResponse('You are not authorized to view this page<br><a href="/">Home</a>') 
