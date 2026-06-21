from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import  login
from django.contrib import messages
from .models import Product, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def product_list(request):
    products = Product.objects.all()
    
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(
        request,
        'myapp/product_list.html',
        {'products': products,
         'cart_count':cart_count}
    )
    
    
def product_detail(request,id):
    product=get_object_or_404(Product,id=id)
    
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    
    return render(
        request,
        'myapp/product_detail.html',
        {'product': product,
         'cart_count':cart_count}
    )
 
 
def add_to_cart(request, product_id):
    product=get_object_or_404(Product,id=product_id)  
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)]=+1
        
    else:
        cart[str(product_id)]=1
        
    request.session['cart']=cart
    request.session.modified=True
    
    messages.success(request,f"{product.name} added to cart!")
    
    return redirect('product_list')


def delete_from_cart(request, product_id):
    cart=request.session.get('cart',{})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart']=cart
        request.session.modified=True
        messages.success(request,"Item removed from cart!")
        
    return redirect('view_cart')

def update_cart(request, product_id):
    
    if request.method=='POSI':
        quantity=int(request.POST.get('quantity',1))
        cart=request.session.get('cart',{})
        
        if quantity > 0:
            cart[str(product_id)]= quantity
            
        elif str(product_id) in cart:
            del cart[str(product_id)]
            
        request.session['cart']=cart
        request.session.modified=True
        
        messages.success(request,"Cart Updated!")
        
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = float(product.price) * quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            pass
    
    # Calculate tax (10%)
    tax_amount = total_price * 0.1
    grand_total = total_price + tax_amount
    
    return render(request, 'myapp/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
        'cart_count': sum(cart.values())
    })

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)  # Don't save yet
                user.save()  # Now save to database
                username = form.cleaned_data.get('username')
                messages.success(request, f"Account created for {username}!")
                login(request, user)
                return redirect('product_list')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return render(request, 'myapp/register.html', {'form': form})
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'myapp/register.html', {'form': form})
    
    
def order_confirmation(request, order_id):
    order=get_object_or_404(Order,id=order_id,user=request.user)
    
    return render(
        request,
        'myapp/order_confirmation.html',
        {
            'order': order,
            'cart_count': 0
        }
    )
    
@login_required(login_url='login')
def my_orders(request):
    orders=Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(
        request,
        'myapp/my_orders.html',
        {
            'orders':orders,
            'cart_count':len(request.session.get('cart',{}))
        }
    )        



@login_required(login_url='login')
def checkout(request):
    if request.method=='POST':
        cart=request.session.get('cart',{})
        
        if not cart:
            messages.error(request,"Your cart is empty!")
            return redirect('view_cart')
        
        total_price=0
        order=Order.objects.create(user=request.user)
        
        for product_id, quantity in cart.items():
            try:
                product=Product.objects.get(id=int(product_id))
                price=float(product.price)
                item_total=price* quantity
                total_price += item_total
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
            except Product.DoesNotExist:
                pass
            
        order.total_price= total_price
        order.save()
        
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, "Order placed successfully!")
        return redirect('order_confirmation', order_id=order.id)
    
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = float(product.price) * quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            pass
        
    tax_amount = total_price * 0.1
    grand_total = total_price + tax_amount
    
    return render(request, 'myapp/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax_amount': tax_amount,          # ← Add this
        'grand_total': grand_total,         # ← Add this
        'cart_count': sum(cart.values())
    })
            
        
