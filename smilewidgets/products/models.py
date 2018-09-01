from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product')
    price = models.PositiveIntegerField(help_text='Price of product in cents if no ProductPrice in date range')

    def get_product_price_schedule(self, date):
        """Return the ProductPrice covered by the date or None."""

        return self.productprice_set.exclude(date_start__gt=date).exclude(date_end__lte=date).first()

    def get_price_for_date(self, date):
        """Return the price in cents for this product for the requested date."""

        try:
            return self.get_product_price_schedule(date).amount
        except AttributeError:
            return self.price
    
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

    class DateOverlapError(Exception):
        pass

    def save(self, *args, **kwargs):
        """Prevent overlapping price schedules for a product in order to simplify price lookup."""

        # First make sure that this price schedule doesn't start inside another:
        if self.product.get_product_price_schedule(self.date_start) is not None:
            raise ProductPrice.DateOverlapError('Starts inside ProductPrice for same Product')

        # Then make sure that it doesn't end inside another:
        if self.date_end and self.product.get_product_price_schedule(self.date_end) is not None:
            raise ProductPrice.DateOverlapError('Partially overlaps with ProductPrice for same Product')

        # If this new price schedule is indefinite, make sure that there isn't an existing
        # range that would start inside it:
        if self.date_end is None and self.product.productprice_set.filter(date_start__gte=self.date_start).first():
            raise ProductPrice.DateOverlapError('Indefinite ProudctPrice would overlap with existing later range')

        super().save(*args, **kwargs)