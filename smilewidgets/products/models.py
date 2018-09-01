from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product')
    price = models.PositiveIntegerField(help_text='Price of product in cents if no ProductPrice in date range')

    def get_price(self, date):
        """Return the price in cents for this product on the requested date."""

        active_price_on_date = self.product_price_set.exclude(start_date__gt=date).exclude(end_date__lte=date).all()[0]

        return active_price_on_date or self.price
    
    def __str__(self):
        return '{} - {}'.format(self.name, self.code)


class BasePriceSchedule(models.Model):
    amount = models.PositiveIntegerField(help_text='Value in cents')
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def formatted_amount(self):
        return '${0:.2f}'.format(self.amount / 100)


class GiftCard(BasePriceSchedule):
    code = models.CharField(max_length=30)

    def __str__(self):
        return '{} - {}'.format(self.code, self.formatted_amount)


class ProductPrice(BasePriceSchedule):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)