import requests
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import CustomUserCreationForm


# 1. მთავარი გვერდი (პროდუქტების სია API-დან)
def cardList(request):
    api_url = "https://api.everrest.educata.dev/shop/products/all"
    products_list = []

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            raw_products = data.get("products", [])

            for item in raw_products:
                product_data = {
                    "title": item.get("title"),
                    "thumbnail": item.get("thumbnail"),
                    "price": item.get("price", {}).get("current"),
                    "rating": item.get("rating"),
                    "issue_date": item.get("issueDate"),
                    "brand": item.get("brand"),
                    "stock": item.get("stock"),
                }
                products_list.append(product_data)
        print("API Response Status:", response.status_code)
        print("API Data:", response.json())
    except Exception as e:
        print("შეცდომა API-სთან:", e)

    context = {"products": products_list}
    # მთავარი გვერდის შაბლონი (მაგალითად: store/home.html ან card_list.html)
    return render(request, "card-list.html", context)


# 2. რეგისტრაციის ხედი (Class-Based View)
class RegisterPage(FormView):
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("store:login")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "User registration completed successfully! Please log in.",
        )
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)


# 3. ლოგინის ხედი (Class-Based View)
class CustomLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        return reverse_lazy("store:card-list")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("store:card-list")
        return super().get(request, *args, **kwargs)

# import requests
# from django.contrib import messages
# from django.contrib.auth.views import LoginView
# from django.shortcuts import redirect, render
# from django.urls import reverse_lazy
# from django.views.generic import FormView
# from .forms import CustomUserCreationForm


# def cardList(request):
#     api_url = "https://api.everrest.educata.dev/shop/products/all"
#     products_list = []

#     search_query = request.GET.get("search", "").lower()

#     try:
#         response = requests.get(api_url)
#         if response.status_code == 200:
#             data = response.json()
#             raw_products = data.get("products", [])

#             for item in raw_products:
#                 title = item.get("title", "")

#                 if search_query and search_query not in title.lower():
#                     continue

#                 product_data = {
#                     "id": item.get("_id") or item.get("id"),
#                     "title": title,
#                     "thumbnail": item.get("thumbnail"),
#                     "price": item.get("price", {}).get("current"),
#                     "rating": item.get("rating"),
#                     "issue_date": item.get("issueDate"),
#                     "brand": item.get("brand"),
#                     "stock": item.get("stock"),
#                 }
#                 products_list.append(product_data)
#     except Exception as e:
#         print("შეცდომა API-სთან:", e)

#     context = {"products": products_list}
#     return render(request, "card-list.html", context)


# class RegisterPage(FormView):
#     template_name = "register.html"
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy("store:login")

#     def form_valid(self, form):
#         form.save()
#         messages.success(
#             self.request, "რეგისტრაცია წარმატებით დასრულდა! გთხოვთ გაიაროთ ავტორიზაცია."
#         )
#         return super().form_valid(form)

#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             return redirect("store:card-list")
#         return super().get(request, *args, **kwargs)


# class CustomLoginView(LoginView):
#     template_name = "login.html"

#     def get_success_url(self):
#         return reverse_lazy("store:card-list")

#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             return redirect("store:card-list")
#         return super().get(request, *args, **kwargs)
