from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


# პროდუქტის მოდელი. ინახავს ტექნიკის ძირითად მონაცემებს:
# სახელს, ფასს, ფასდაკლებულ ფასს, ბრენდს, კატეგორიას, მარაგს, რეიტინგი და სურათის URL-ს.
class Product(models.Model):

    title = models.CharField(max_length=200, verbose_name="დასახელება")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ფასი")

    # ფასდაკლებული ფასი (არასავალდებულოა, შეიძლება ცარიელი იყოს)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="ფასდაკლებული ფასი",
    )
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

    @property
    def get_price(self):
        # თუ ფასდაკლებული ფასია მითითებული, დააბრუნებს მას, სხვა შემთხვევაში - ჩვეულებრივს
        if self.discount_price:
            return self.discount_price
        return self.price

    def update_rating(self):
        # ვთვლით ამ პროდუქტზე არსებული ყველა შეფასების საშუალო არითმეტიკულს
        avg_rating = self.reviews.aggregate(Avg("rating"))["rating__avg"]
        if avg_rating is not None:
            # ვამრგვალებთ ათწილადამდე (მაგ: 4.5)
            self.rating = round(avg_rating, 1)
        else:
            self.rating = 0.0
        # ვინახავთ მხოლოდ რეიტინგის ველს, რომ არ გამოიწვიოს უსარგებლო შეფერხებები
        self.save(update_fields=["rating"])


# პროდუქტის შეფასებებისა და კომენტარების მოდელი.
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # შეფასების დამატების/განახლების შემდეგ ავტომატურად ვანახლებთ პროდუქტის რეიტინგს
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product_obj = self.product
        super().delete(*args, **kwargs)
        # შეფასების წაშლის შემდეგაც ავტომატურად გადაითვლება რეიტინგი
        product_obj.update_rating()


# კალათის ნივთების მოდელი. ინახავს ინფორმაციას იმის შესახებ, თუ რომელი პროდუქტი და რა რაოდენობით აქვს მომხმარებელს კალათაში.
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
        # იყენებს მიმდინარე აქტიურ ფასს (ფასდაკლებულს ან ჩვეულებრივს) და ამრავლებს რაოდენობაზე
        return self.product.get_price * self.quantity


# შეკვეთის მთავარი მოდელი. ინახავს შეკვეთის დეტალებს: მიმღების სახელს, გვარს, ტელეფონს, მისამართს,
# გადახდის ტიპსა და არჩეულ ბანკს (განვადების შემთხვევაში), ასევე ჯამურ თანხებს.
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


# შეკვეთაში შემავალი ცალკეული პროდუქტების მოდელი. ინახავს კონკრეტული შეკვეთის დროს შეძენილ პროდუქტს, მის ფასსა და რაოდენობას.
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
