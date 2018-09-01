from django.contrib import admin

from .models import GiftCard, Product, ProductPrice


admin.site.register(GiftCard)
admin.site.register(Product)
admin.site.register(ProductPrice)