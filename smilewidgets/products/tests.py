import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Product


class ProductModelTests(TestCase):

    def setUp(self):
        self.widget = Product(name='test widget', code='test_widge', price=100)
        self.widget.save()
        self.now = datetime.date(2018, 9, 1)

    def test_product_default_price_with_no_related_prices(self):
        """get_price returns the default price if there are no related ProductPrice instances."""

        expected_price = 100
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_after_date(self):
        """
        get_price returns the default price if there is a related ProductPrice
        with an indefinite date range beginning after the date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2019, 1, 1))
        expected_price = 100
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_before_date(self):
        """
        get_price returns the default price if there is a related ProductPrice
        that begins and ends before the requested date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2017, 1, 1), date_end=datetime.date(2018, 1, 1))
        expected_price = 100
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_before_date_adjacent(self):
        """
        get_price returns the default price if there is a related ProductPrice
        that ends on the requested date (i.e., end_date is exclusive).
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1), date_end=self.now)
        expected_price = 100
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_related_price_in_range_indefinite(self):
        """
        get_price returns the amount of a related ProductPrice if it begins
        before the requested date and has no end date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1))
        expected_price = 200
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_related_price_in_range(self):
        """
        get_price returns the amount of a related ProductPrice if it begins
        before the requested date and ends after the requested date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1), date_end=datetime.date(2019, 1, 1))
        expected_price = 200
        actual_price = self.widget.get_price(self.now)
        self.assertEqual(expected_price, actual_price)