from app1.models import Order
from django.contrib import admin
from .models import Product, Cart, Order, Review

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "format"]

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Product, ProductAdmin)
