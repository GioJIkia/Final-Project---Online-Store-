from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="დასახელება")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ფასი")
    brand = models.CharField(max_length=100, verbose_name="ბრენდი")
    category = models.CharField(max_length=100, verbose_name="კატეგორია")
    stock = models.PositiveIntegerField(default=0, verbose_name="მარაგი (საწყობში)")
    rating = models.FloatField(default=0.0, verbose_name="რეიტინგი")
    issue_date = models.DateField(
        null=True, blank=True, verbose_name="გამოშვების თარიღი"
    )
    thumbnail = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="სურათის URL"
    )
    detailed_specs = models.TextField(
        blank=True, null=True, verbose_name="დეტალური მახასიათებლები"
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="პროდუქტი",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="მომხმარებელი"
    )
    rating = models.PositiveIntegerField(verbose_name="რეიტინგი (1-5)")
    comment = models.TextField(blank=True, null=True, verbose_name="კომენტარი")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating}★)"


class CartItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="მომხმარებელი"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="პროდუქტი"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="რაოდენობა")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity} ცალი)"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    BANK_CHOICES = [
        ("georgia", "საქართველოს ბანკი"),
        ("tbc", "თიბისი ბანკი"),
        ("liberty", "ლიბერთი ბანკი"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="მომხმარებელი"
    )
    first_name = models.CharField(max_length=100, verbose_name="სახელი")
    last_name = models.CharField(max_length=100, verbose_name="გვარი")
    phone = models.CharField(max_length=20, verbose_name="ტელეფონი")
    address = models.TextField(verbose_name="მისამართი")

    payment_type = models.CharField(
        max_length=20,
        choices=[("direct", "პირდაპირი ყიდვა"), ("installment", "განვადება")],
        default="direct",
        verbose_name="გადახდის ტიპი",
    )
    bank_choice = models.CharField(
        max_length=20, choices=BANK_CHOICES, blank=True, null=True, verbose_name="ბანკი"
    )

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="პროდუქტების ფასი", default=0.00
    )
    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=5.00, verbose_name="მიტანის საფასური"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="სრული თანხა"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="შექმნის თარიღი")

    def __str__(self):
        return f"შეკვეთა #{self.id} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE, verbose_name="შეკვეთა"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, verbose_name="პროდუქტი"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ფასი")
    quantity = models.PositiveIntegerField(default=1, verbose_name="რაოდენობა")

    def __str__(self):
        return f"{self.product.title if self.product else 'წაშლილი პროდუქტი'} ({self.quantity} ცალი)"
