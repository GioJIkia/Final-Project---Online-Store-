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
    comment = models.TextField(
        blank=True, null=True, verbose_name="კომენტარი"
    )  # არასავალდებულო კომენტარი
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
