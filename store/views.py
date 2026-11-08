import requests
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import CustomUserCreationForm
from .models import Product, Review, CartItem


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

    if search_query:
        products_list = products_list.filter(title__icontains=search_query)

    if selected_category:
        products_list = products_list.filter(category__icontains=selected_category)

    if selected_brand:
        products_list = products_list.filter(brand__iexact=selected_brand)

    if max_price:
        try:
            products_list = products_list.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if min_rating:
        try:
            products_list = products_list.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    # სორტირება ფასის მიხედვით
    if sort_by == "price_asc":
        products_list = products_list.order_by("price")
    elif sort_by == "price_desc":
        products_list = products_list.order_by("-price")

    context = {"products": products_list}
    return render(request, "card-list.html", context)


def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("store:login")

        rating = request.POST.get("review_rating")
        comment = request.POST.get("comment", "").strip()

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


class RegisterPage(FormView):
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("store:login")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, "რეგისტრაცია წარმატებით დასრულდა! გთხოვთ გაიაროთ ავტორიზაცია."
        )
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        return reverse_lazy("store:card-list")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)


# ==========================================
# კალათის ფუნქციონალი
# ==========================================


@login_required(login_url="store:login")
def cartView(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    cart_item_count = cart_items.count()

    # თითოეული ნივთისთვის რევიუების დათვლა
    for item in cart_items:
        item.review_count = Review.objects.filter(product=item.product).count()

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_item_count": cart_item_count,  # ახლა უკვე განსაზღვრულია
    }
    return render(request, "cart.html", context)


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
