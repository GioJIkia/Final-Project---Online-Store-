from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import CustomUserCreationForm
from .models import Product, Review, CartItem, Order, OrderItem
from decimal import Decimal

# პროდუქტების კატალოგისა და მთავარი გვერდის ფუნქცია.
def cardList(request):

    # ვიღებთ პროდუქტებს პირდაპირ Django-ს ბაზიდან
    products_list = Product.objects.all()

    # ფილტრაციის და სორტირების პარამეტრები GET მოთხოვნიდან
    search_query = request.GET.get("search", "").strip()
    selected_category = request.GET.get("category", "").strip()
    selected_brand = request.GET.get("brand", "").strip()
    max_price = request.GET.get("price", "").strip()
    min_rating = request.GET.get("rating", "").strip()
    sort_by = request.GET.get("sort", "").strip()

    # სახელით ძებნის ფილტრი
    if search_query:
        products_list = products_list.filter(title__icontains=search_query)

    # ვამოწმებთ, რომ კატეგორია არ იყოს ცარიელი
    if selected_category:
        products_list = products_list.filter(category__icontains=selected_category)

    # ვამოწმებთ, რომ ბრენდი არ იყოს ცარიელი
    if selected_brand:
        products_list = products_list.filter(brand__iexact=selected_brand)

    # მაქსიმალური ფასის მიხედვით ფილტრაცია
    if max_price:
        try:
            products_list = products_list.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # მინიმალური რეიტინგის მიხედვით ფილტრაცია
    if min_rating:
        try:
            products_list = products_list.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    # სორტირება ფასის მიხედვით (ზრდადი ან კლებადი)
    if sort_by == "price_asc":
        products_list = products_list.order_by("price")
    elif sort_by == "price_desc":
        products_list = products_list.order_by("-price")

    # კონტექსტში გადავცემთ გაფილტრულ სიას და სორტირების პარამეტრს შაბლონისთვის
    context = {"products": products_list, "sort_by": sort_by}
    return render(request, "card-list.html", context)

# კონკრეტული პროდუქტის დეტალური გვერდი.
def productDetail(request, product_id):

    # ვეძებთ პროდუქტს ID-ით ან ვაბრუნებთ 404 შეცდომას თუ არ არსებობს
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        # თუ მომხმარებელი ავტორიზებული არ არის, რევიუს ვერ დატოვებს და გადამისამართდება ლოგინზე
        if not request.user.is_authenticated:
            return redirect("store:login")

        rating = request.POST.get("review_rating")
        comment = request.POST.get("comment", "").strip()

        # თუ რეიტინგი მითითებულია, ვქმნით ახალ Review ობიექტს ბაზაში
        if rating:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment if comment else None,
            )
        return redirect("store:product-detail", product_id=product.id)

    context = {"product": product}
    return render(request, "product-detail.html", context)

# რეგისტრაციის გვერდი (Class-Based View).
class RegisterPage(FormView):

    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("store:login")

    def form_valid(self, form):
        # ფორმის ვალიდაციის წარმატებით გავლისას ვინახავთ მომხმარებელს და ვწერთ მესიჯს
        form.save()
        messages.success(
            self.request, "რეგისტრაცია წარმატებით დასრულდა! გთხოვთ გაიაროთ ავტორიზაცია."
        )
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # თუ უკვე ავტორიზებული იუზერი ცდილობს რეგისტრაციის გვერდზე შესვლას, ვუბრუნებთ კატალოგს
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)

# მომხმარებლის ავტორიზაცია
class CustomLoginView(LoginView):

    template_name = "login.html"

    def get_success_url(self):
        # წარმატებული შესვლის შემდეგ აბრუნებს კატალოგის გვერდზე
        return reverse_lazy("store:card-list")

    def get(self, request, *args, **kwargs):
        # თუ უკვე შესულია სისტემაში, ლოგინის გვერდზე აღარ უშვებს
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)


# კალათის ფუნქციონალი, აჩვენებს მაშინ თუ დალოგინებულია სისტემაში

@login_required(login_url="store:login")
def cartView(request):

    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    cart_item_count = cart_items.count()

    # თითოეული ნივთისთვის პროდუქტის რევიუების რაოდენობის დათვლა (საჭიროებისამებრ)
    for item in cart_items:
        item.review_count = Review.objects.filter(product=item.product).count()

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_item_count": cart_item_count,
    }
    return render(request, "cart.html", context)

# ამატებს პროდუქტს კალათაში (ან ზრდის რაოდენობას, თუ ის უკვე კალათაშია)
@login_required(login_url="store:login")
def addToCart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("store:card-list")

# მართავს კალათაში არსებული ნივთის რაოდენობას GET მოთხოვნის action პარამეტრით:
# ზრდის ('increase'), ამცირებს ('decrease') ან სრულად შლის ('remove')
@login_required(login_url="store:login")
def updateCartItem(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.GET.get("action")

    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == "remove":
        cart_item.delete()

    return redirect("store:cart")

#  ჩვეულებრივი შეკვეთის გაფორმების (Checkout) გვერდი კალათიდან.
@login_required(login_url="store:login")
def checkoutView(request):

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("store:cart")

    # პროდუქტების ჯამური ღირებულება
    subtotal = sum(item.total_price for item in cart_items)
    shipping_fee = Decimal("5.00")  # მიტანის საფასური Decimal ტიპის
    total_price = subtotal + shipping_fee

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_type = request.POST.get("payment_type")
        bank_choice = (
            request.POST.get("bank_choice") if payment_type == "installment" else None
        )

        # შევქმნათ შეკვეთა Order ცხრილში
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            payment_type=payment_type,
            bank_choice=bank_choice,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_price=total_price,
        )

        # შევინახოთ შეკვეთაში შემავალი თითოეული პროდუქტი OrderItem ცხრილში
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )

        # გავასუფთავოთ კალათა შეკვეთის წარმატებით დასრულების შემდეგ
        cart_items.delete()

        return redirect("store:card-list")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "total_price": total_price,
    }
    return render(request, "checkout.html", context)

#  პირდაპირი ყიდვის ფუნქციონალი
@login_required(login_url="store:login")
def directCheckoutView(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # ავტომატურად ვქმნით ან ვიღებთ CartItem-ს ამ მომხმარებლისთვის
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        pass

    # ამის მერე უბრალოდ გამოვთვალოთ იგივე ლოგიკით, რაც ჩვეულებრივ checkout-შია
    cart_items = CartItem.objects.filter(user=request.user)

    subtotal = sum(item.total_price for item in cart_items)
    shipping_fee = Decimal("5.00")
    total_price = subtotal + shipping_fee

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_type = request.POST.get("payment_type")
        bank_choice = (
            request.POST.get("bank_choice") if payment_type == "installment" else None
        )

        # შეკვეთის ობიექტის შექმნა ბაზაში
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            payment_type=payment_type,
            bank_choice=bank_choice,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_price=total_price,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )

        # გავასუფთავოთ კალათა შეკვეთის შემდეგ
        cart_items.delete()

        return redirect("store:card-list")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "total_price": total_price,
    }

    return render(request, "checkout.html", context)

# მართავს კალათის/შეკვეთის გვერდზე ნივთების რაოდენობის ცვლილებას (+/-) ან წაშლას,
@login_required(login_url="store:login")
def updateCheckoutItem(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.GET.get("action")

    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == "remove":
        cart_item.delete()

    return redirect("store:checkout")

# ავტორიზებული მომხმარებლის შეკვეთების ისტორია
@login_required(login_url="store:login")
def my_ordersView(request):

    print("VIEW IS CALLED:", Order.objects.filter(user=request.user))
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "orders": orders,
    }
    return render(request, "my_orders.html", context)

#  მიტანის პირობების სტატიკური გვერდი
def delivery_view(request):
    return render(request, "delivery.html")

# 'ჩვენს შესახებ' სტატიკური გვერდის
def about_view(request):
    return render(request, "about.html")
