from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

import json

from observatory import helpers
from observatory.models import Hs4, Sitc4, Country


@cache_control(max_age=settings.CACHE_VERY_SHORT)
def api_dropdown_products(request, product_class="hs4"):
    """API to dynamically fill in a product dropdown, product name to code. Can
    also set lang=foo to get a specific language, but it'll default to the
    django user locale. """

    lang = helpers.get_language(request)['code']

    if product_class == "sitc4":
        products = Sitc4.objects.get_all(lang)
    elif product_class == "hs4":
        products = Hs4.objects.get_all(lang)
        products = [x for x in products if len(x["code"]) > 3]

    return HttpResponse(json.dumps([(p["name"], p["code"]) for p in products]),
                        content_type="application/json")


@cache_control(max_age=settings.CACHE_VERY_SHORT)
def api_dropdown_countries(request):
    """API to dynamically fill in a country dropdown, product name to code. Can
    also set lang=foo to get a specific language, but it'll default to the
    django user locale. """

    lang = helpers.get_language(request)['code']

    countries = Country.objects\
        .filter_lang(lang)\
        .filter(originally_included=True)\
        .values("name", "name_3char")

    country_info = list((c["name"], c["name_3char"].lower())
                        for c in countries)

    return HttpResponse(json.dumps(country_info),
                        content_type="application/json")
