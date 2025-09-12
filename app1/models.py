import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

BOOK_FORMATS = (
    ('E-Book','E-Book'),
    ('Paper','Paper'),
)

class Product(models.Model):
    name = models.CharField(default="", max_length=50)
    format = models.CharField(choices=BOOK_FORMATS, max_length=50, default="E-Book")
    genre = models.CharField(default="", max_length=50)
    price = models.IntegerField(default=0)
    file = models.FileField(upload_to="EBooks_PDFs", blank=True, null=True)
    img = models.ImageField(default="", upload_to="BooksImgs")
    author = models.CharField(default="", max_length=50)
    stock = models.IntegerField(default=0)
    pages = models.IntegerField(default=0)
    lang = models.CharField(default="", max_length=50)
    short_desc = models.CharField(default="", max_length=50)
    desc = models.TextField(default="")
    publish_date = models.DateField(default=datetime.date.today)
    is_avail = models.BooleanField(default=True)

    def __str__(self):
        return self.name



ORDER_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Ordered', 'Ordered'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    sub_total = models.IntegerField(default=0)
    direct_buy = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS_CHOICES,default='Pending')

    def __str__(self):
        return f"Book: {self.book.name} - Quantity: {self.quantity}"



PAYMENT_TYPES = (
    ('COD','COD'),
    ('Online','Online'),
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    my_books = models.ManyToManyField(Cart)
    full_name = models.CharField(default="", max_length=50)
    phone = models.IntegerField(default=0000000000)
    address = models.TextField(default="")
    zip = models.IntegerField(default=000000)
    order_total = models.IntegerField(default=0)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES, blank=True, null=True)
    online_payment_id = models.CharField(max_length=100, default="NA")
    ordered = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    book = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    review = models.TextField(max_length=500, default="")
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
