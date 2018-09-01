import datetime
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import GiftCard, Product


def get_price(request):
    product_code = request.GET['productCode']

    date_iso = request.GET['date']
    year, month, day = date_iso.split('-')
    date = datetime.date(int(year), int(month), int(day))

    gift_card_code = request.GET.get('giftCardCode', None)

    product = get_object_or_404(Product, code=product_code)
    subtotal = product.get_price_for_date(date)

    gift_cards = GiftCard.gift_card_for_date_range(gift_card_code, date)
    discounts = sum([gc.amount for gc in gift_cards])

    total = max(0, subtotal - discounts)

    json_body = json.dumps(dict(price=total))
    return HttpResponse(json_body, content_type='application/json')