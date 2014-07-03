from django.http import HttpResponse
from django.views.decorators.cache import cache_control

import json

from observatory.models import Hs4, Sitc4, Country


@cache_control(max_age=900)
def api_dropdown_products(request, product_class="hs4"):
    """API to dynamically fill in a product dropdown, product name to code. Can
    also set lang=foo to get a specific language, but it'll default to the
    django user locale. """

    lang = request.session.get('django_language', "en")
    lang = request.GET.get("lang", lang)

    if product_class == "sitc4":
        products = Sitc4.objects.get_all(lang)
    elif product_class == "hs4":
        products = Hs4.objects.get_all(lang)

    return HttpResponse(json.dumps([(p["name"], p["code"]) for p in products]),
                        content_type="application/json")

@cache_control(max_age=900)
def api_dropdown_countries(request):
    """API to dynamically fill in a country dropdown, product name to code. Can
    also set lang=foo to get a specific language, but it'll default to the
    django user locale. """

    lang = request.session.get('django_language', "en")
    lang = request.GET.get("lang", lang)

    countries = Country.objects.get_all(lang)
    return HttpResponse(json.dumps([(c["name"], c["name_3char"].lower()) for c in countries]),
                        content_type="application/json")
