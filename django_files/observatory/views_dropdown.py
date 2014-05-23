from django.http import HttpResponse

import json

from observatory.models import Hs4, Sitc4


def api_dropdown_products(request, product_class="hs4"):
    """

    can also set  lang=foo

    """

    lang = request.session.get('django_language', "en")
    lang = request.GET.get("lang", lang)

    if product_class == "sitc4":
        products = Sitc4.objects.get_all(lang)
    elif product_class == "hs4":
        products = Hs4.objects.get_all(lang)

    return HttpResponse(json.dumps([(p["name"], p["code"]) for p in products]),
                        content_type="application/json")


def api_dropdown_countries(request):
    return HttpResponse("", content_type="application/json")
