from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from users.models import UserPoints
from decimal import Decimal
from django.contrib import messages
from django.db import transaction



def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    
    query = request.GET.get('q')
    if query:
        
        products = products.filter(name__icontains=query)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query  
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})

@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('shop:cart_detail')

@login_required
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart/detail.html', {'cart': cart})


@login_required
def order_create(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            total_price = cart.get_total_price()
            points_to_use = int(total_price)
            
            wallet, _ = UserPoints.objects.get_or_create(user=request.user)
            
            if wallet.points < points_to_use:
                messages.error(request, "Não tens pontos suficientes para esta compra.")
                return redirect('shop:cart_detail')

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.save()

                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                    
                    wallet.subtract_points(points_to_use)
                    
                    cart.clear()

                try:
                    subject = f'Fatura da sua encomenda #{order.id} - Reboot Verde'
                    html_message = render_to_string('shop/order/email_fatura.html', {'order': order})
                    send_mail(
                        subject,
                        f'Olá {order.first_name}, obrigado pela sua compra!',
                        'rebootverde123@gmail.com',
                        [order.email],
                        html_message=html_message,
                        fail_silently=True
                    )
                except Exception:
                    pass

                return render(request, 'shop/order/created.html', {'order': order})

            except Exception as e:
                messages.error(request, "Ocorreu um erro ao processar a sua encomenda. Tente novamente.")
    else:
        form = OrderCreateForm()
    
    return render(request, 'shop/order/create.html', {'cart': cart, 'form': form})