from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "store"

urlpatterns = [
    path("", views.cardList, name="card-list"),
    path("register/", views.RegisterPage.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="store:login"), name="logout"),
    path("product/<int:product_id>/", views.productDetail, name="product-detail"),
    path("cart/", views.cartView, name="cart"),
    path("cart/add/<int:product_id>/", views.addToCart, name="add-to-cart"),
    path("cart/update/<int:item_id>/", views.updateCartItem, name="update-cart"),
    path("checkout/", views.checkoutView, name="checkout"),
    path("my-orders/", views.my_ordersView, name="my-orders"),
]


# 127.0.0.1:8000/
# 127.0.0.1:8000/register
# 127.0.0.1:8000/login
# 127.0.0.1:8000/logout
# 127.0.0.1:8000/product/<int:product_id>/
# 127.0.0.1:8000/cart
# 127.0.0.1:8000/cart/add/<int:product_id>/
# 127.0.0.1:8000/cart/update/<int:item_id>/
# 127.0.0.1:8000/checkout
# 127.0.0.1:8000/my-orders
