import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Product, ProductPrice


class ProductModelTests(TestCase):

    def setUp(self):
        self.widget = Product(name='test widget', code='test_widge', price=100)
        self.widget.save()
        self.now = datetime.date(2018, 9, 1)

    def test_product_default_price_with_no_related_prices(self):
        """get_price returns the default price if there are no related ProductPrice instances."""

        expected_price = 100
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_after_date(self):
        """
        get_price returns the default price if there is a related ProductPrice
        with an indefinite date range beginning after the date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2019, 1, 1))
        expected_price = 100
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_before_date(self):
        """
        get_price returns the default price if there is a related ProductPrice
        that begins and ends before the requested date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2017, 1, 1), date_end=datetime.date(2018, 1, 1))
        expected_price = 100
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_default_price_related_prices_before_date_adjacent(self):
        """
        get_price returns the default price if there is a related ProductPrice
        that ends on the requested date (i.e., end_date is exclusive).
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1), date_end=self.now)
        expected_price = 100
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_related_price_in_range_indefinite(self):
        """
        get_price returns the amount of a related ProductPrice if it begins
        before the requested date and has no end date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1))
        expected_price = 200
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)

    def test_product_related_price_in_range(self):
        """
        get_price returns the amount of a related ProductPrice if it begins
        before the requested date and ends after the requested date.
        """

        self.widget.productprice_set.create(amount=200, date_start=datetime.date(2018, 1, 1), date_end=datetime.date(2019, 1, 1))
        expected_price = 200
        actual_price = self.widget.get_price_for_date(self.now)
        self.assertEqual(expected_price, actual_price)


class ProductPriceModelTests(TestCase):

    def setUp(self):
        self.widget = Product(name='test widget', code='test_widge', price=100)
        self.widget.save()

    def test_save(self):
        product_price = ProductPrice(product=self.widget, amount=200, date_start=datetime.date(2018, 1, 1))
        product_price.save()
        pk = product_price.pk

        selected_product_price = ProductPrice.objects.get(pk=pk)
        expected_amount = 200
        expected_date_start = datetime.date(2018, 1, 1)
        self.assertEqual(expected_amount, selected_product_price.amount)
        self.assertEqual(expected_date_start, selected_product_price.date_start)

    def test_save_prevent_overlapping_indefinite_ranges_for_same_product(self):
        """
        Prevent a ProductPrice from saving if there's already an indefinite one for the
        same Product covering this date range.
        """

        product_price_january = ProductPrice(product=self.widget, amount=200, date_start=datetime.date(2018, 1, 1))
        product_price_january.save()
        product_price_june = ProductPrice(product=self.widget, amount=300, date_start=datetime.date(2018, 6, 1))

        with self.assertRaises(ProductPrice.DateOverlapError):
            product_price_june.save()

    def test_save_prevent_overlapping_ranges_for_same_product(self):
        """
        Prevent a ProductPrice from saving if it partially overlaps into
        one for the same Product.
        """

        product_price_june = ProductPrice(product=self.widget, amount=300, date_start=datetime.date(2018, 6, 1), date_end=datetime.date(2018, 7, 1))
        product_price_june.save()
        product_price_january_june = ProductPrice(product=self.widget, amount=200, date_start=datetime.date(2018, 1, 1), date_end=datetime.date(2018, 6, 15))

        with self.assertRaises(ProductPrice.DateOverlapError):
            product_price_january_june.save()

    def test_save_prevent_new_indefinite_overlapping_range_for_same_product(self):
        """
        Prevent a ProductPrice from saving if it is indefinite and another
        ProductPrice range is supposed to start later.
        """

        product_price_june = ProductPrice(product=self.widget, amount=300, date_start=datetime.date(2018, 6, 1))
        product_price_june.save()
        product_price_january = ProductPrice(product=self.widget, amount=200, date_start=datetime.date(2018, 1, 1))

        with self.assertRaises(ProductPrice.DateOverlapError):
            product_price_january.save()

    def test_save_adjacent_ranges_for_same_product(self):
        """
        date_end is exclusive, so it's ok if date_end==date_start for another
        ProductPrice for the same Product.
        """

        product_price_january_may = ProductPrice(product=self.widget, amount=200, date_start=datetime.date(2018, 1, 1), date_end=datetime.date(2018, 6, 1))
        product_price_january_may.save()
        product_price_june = ProductPrice(product=self.widget, amount=300, date_start=datetime.date(2018, 6, 1))
        product_price_june.save()