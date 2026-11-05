from django.db import models
from django.contrib.auth.models import User

# class Review(models.Model):
#     # რადგან API-დან მოგაქვს პროდუქტი, აქ პროდუქტის ID-ს ვინახავთ სტრიქონის სახით (_id)
#     product_id = models.CharField(max_length=100)
#     user_name = models.CharField(
#         max_length=150
#     )
#     rating = models.IntegerField()  # ვარსკვლავების რაოდენობა (1-დან 5-მდე)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user_name} - {self.rating} Stars"

# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     product_id = models.CharField(max_length=100)
#     title = models.CharField(max_length=255)
#     price = models.FloatField()
#     quantity = models.PositiveIntegerField(default=False)
#     thumbnail = models.URLField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.title} ({self.quantity})"
