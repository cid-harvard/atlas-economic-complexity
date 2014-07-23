import json

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse

from observatory.models import (Country, Hs4, Hs4_cpy, Sitc4, Sitc4_cpy,
                                Hs4_ccpy, Sitc4_ccpy)
from observatory import helpers

import msgpack


def calculate_export_value_rca(items, trade_flow="export", sum_val=False):
    """Given a cpy queryset and trade flow value, calculate trade flow value
    and rca.

    :param sum_val: If true, aggregate sum the trade flow value
    """

    if trade_flow == "net_export":
        select_dict = {'val': 'export_value - import_value',
                       'rca': 'export_rca'}
    elif trade_flow == "net_import":
        select_dict = {'val': 'import_value - export_value',
                       'rca': 'null'}
    elif trade_flow == "export":
        select_dict = {'val': 'export_value', 'rca': 'export_rca'}
    else:
        select_dict = {'val': 'import_value', 'rca': 'null'}

    if sum_val:
        select_dict['val'] = "sum(%s)" % select_dict['val']
        select_dict['rca'] = 'null'

    return items.extra(select=select_dict)

def api_casy(request, trade_flow, country1, year):
    """<COUNTRY> / all / show / <YEAR>"""

    # Get session / request vars
    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))
    lang = helpers.get_language(request)['code']
    name = "name_%s" % lang
    single_year = 'single_year' in request.GET
    country1 = Country.objects.get(name_3char=country1)

    query_params = request.GET.copy()
    query_params["lang"] = lang
    query_params["product_classification"] = prod_class

    world_trade = helpers.get_world_trade(prod_class=prod_class)
    attr = helpers.get_attrs(prod_class=prod_class, name=name)
    years_available = helpers.get_years_available(prod_class=prod_class)
    magic_numbers = helpers.get_inflation_adjustment(country1,
                                                     years_available[0],
                                                     years_available[-1])

    if prod_class == "sitc4":
        items = Sitc4_cpy.objects
    else:
        items = Hs4_cpy.objects

    items = calculate_export_value_rca(items, trade_flow=trade_flow)
    items = items.extra(select={'name': name})
    items = items.values_list('year', 'product__id', 'product__code',
                              'product__name', 'product__community_id',
                              'product__community__color',
                              'product__community__name', 'val', 'rca',
                              'distance', 'opp_gain', 'product_year__pci',)

    if single_year:
        items = items.filter(year=year)

    items = items.filter(country_id=country1.id)
    items = items.extra(where=["export_value > 0"])


    json_response = {}

    # Generate cache key
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "all", "show",
                              prod_class, trade_flow)
    if single_year:
        key += ":%d" % int(year)

    # Check cache
    cached_data = cache.get(key)
    if cached_data is not None:
        json_response["data"] = msgpack.loads(cached_data)
    else:
        rows = list(items)
        total_val = sum([r[7] for r in rows])
        rows = [{"year": r[0], "item_id": r[1], "abbrv": r[2], "name": r[3],
                 "value": r[7], "rca": r[8], "distance": r[9], "opp_gain":
                 r[10], "pci": r[11], "share": (r[7] / total_val) * 100,
                 "community_id": r[4], "color": r[5], "community_name": r[6],
                 "code": r[2], "id": r[2]} for r in rows]

        # Save in cache
        cache.set(key, msgpack.dumps(rows), settings.CACHE_LONG)
        json_response["data"] = rows

    # Add in remaining metadata
    json_response["attr"] = attr
    json_response["attr_data"] = Sitc4.objects.get_all(
        lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
    json_response["country1"] = country1.to_json()
    json_response["title"] = "What does %s %s?" % (
        country1.name, trade_flow.replace("_", " "))
    json_response["year"] = year
    json_response["item_type"] = "product"
    json_response["app_type"] = "casy"
    json_response["magic_numbers"] = magic_numbers
    json_response["world_trade"] = world_trade
    json_response["prod_class"] = prod_class
    json_response["other"] = query_params

    # Check the request data type
    if (request.GET.get('data_type', None) is None):
        return HttpResponse("")
    elif (request.GET.get('data_type', '') == 'json'):
        return HttpResponse(json.dumps(json_response))


def api_sapy(request, trade_flow, product, year):
    """show / all / <product> / <year>"""

    # Get session / request vars
    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))
    lang = helpers.get_language(request)['code']
    name = "name_%s" % lang
    single_year = 'single_year' in request.GET
    product = helpers.get_product_by_code(product, prod_class)

    query_params = request.GET.copy()
    query_params["lang"] = lang
    query_params["product_classification"] = prod_class

    region = helpers.get_region_list()
    continents = helpers.get_continent_list()
    attr = helpers.get_attrs(prod_class=prod_class, name=name)

    if prod_class == "sitc4":
        items = Sitc4_cpy.objects
    else:
        items = Hs4_cpy.objects

    items = calculate_export_value_rca(items, trade_flow=trade_flow)
    items = items.extra(select={'name': name})
    items = items.values_list('year', 'country__id', 'country__name_3char',
                              'name', 'country__region_id',
                              'country__continent', 'val', 'rca')

    if single_year:
        items = items.filter(year=year)

    items = items.filter(product_id=product.id)

    json_response = {}

    # Generate cache key
    key = "%s:%s:%s:%s:%s" % ("show", "all", product.id, prod_class,
                              trade_flow)
    if single_year:
        key += ":%d" % int(year)

    # Check cache
    cached_data = cache.get(key)
    if cached_data is not None:
        json_response["data"] = msgpack.loads(cached_data)
    else:
        rows = list(items)
        total_val = sum([r[6] for r in rows])
        rows = [{"year": r[0], "item_id": r[1], "abbrv": r[2], "name": r[3],
                 "value": r[6], "rca": r[7], "share": (r[6] / total_val) * 100,
                 "id": r[1], "region_id": r[4], "continent": r[5]}
                for r in rows]

        # Save in cache
        cache.set(key, msgpack.dumps(rows), settings.CACHE_LONG)
        json_response["data"] = rows

    json_response["attr_data"] = Country.objects.get_all(lang)
    json_response["product"] = product.to_json()
    json_response["title"] = "Who %sed %s?" % (
        trade_flow.replace("_", " "), product.name_en)
    json_response["year"] = year
    json_response["item_type"] = "country"
    json_response["app_type"] = "sapy"
    json_response["attr"] = attr
    json_response["region"] = region
    json_response["continents"] = continents
    json_response["other"] = query_params

    if (request.GET.get('data_type', None) is None):
        return HttpResponse("")
    elif (request.GET.get('data_type', '') == 'json'):
        """Return to browser as JSON for AJAX request"""
        return HttpResponse(json.dumps(json_response))


def api_csay(request, trade_flow, country1, year):
    """<COUNTRY> / show / all / <YEAR>"""

    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))
    lang = helpers.get_language(request)['code']
    name = "name_%s" % lang
    country1 = Country.objects.get(name_3char=country1)

    region = helpers.get_region_list()
    continents = helpers.get_continent_list()

    if prod_class == "sitc4":
        items = Sitc4_ccpy.objects
    else:
        items = Hs4_ccpy.objects

    items = calculate_export_value_rca(items, trade_flow=trade_flow,
                                       sum_val=True)
    items = items.extra(select={'name': name})
    items = items.values_list('year', 'destination__id',
                              'destination__name_3char', 'name',
                              'destination__region_id',
                              'destination__continent', 'val', 'rca')

    items = items.filter(origin_id=country1.id)

    json_response = {}

    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", "all", prod_class,
                              trade_flow)

    cached_data = cache.get(key)
    if cached_data is not None:
        json_response["data"] = msgpack.loads(cached_data)
    else:
        # This might possibly be the most disgusting hack ever made, simply
        # because when doing an aggregate (like SUM()) in extra, django does
        # not add that stuff correctly into the group by. It's also not
        # possible to use annotate() here because it's a complex aggregate that
        # uses addition / subtraction. C'est la vie :(
        cursor = connection.cursor()
        cursor.execute(str(items.query) + "group by `year`, `destination_id`")
        rows = cursor.fetchall()
        total_val = sum([r[1] for r in rows])

        """Add percentage value to return vals"""
        # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
        rows = [
            {"year": r[3], "item_id": r[4], "abbrv": r[5], "name": r[2],
             "value": r[1], "rca": r[0], "share": (r[1] / total_val) * 100,
             "id": r[4], "region_id": r[6], "continent": r[7]}
            for r in rows]

        cache.set(key, msgpack.dumps(rows), settings.CACHE_LONG)
        json_response["data"] = rows

    years_available = helpers.get_years_available()
    magic_numbers = helpers.get_inflation_adjustment(country1,
                                                     years_available[0],
                                                     years_available[-1])

    query_params = request.GET.copy()
    query_params["lang"] = lang
    query_params["product_classification"] = prod_class

    json_response["attr_data"] = Country.objects.get_all(lang)
    json_response["country1"] = country1.to_json()
    article = "to" if trade_flow == "export" else "from"
    json_response["title"] = "Where does %s %s %s?" % (
        country1.name, trade_flow, article)
    json_response["year"] = year
    json_response["item_type"] = "country"
    json_response["app_type"] = "csay"
    json_response["region"] = region
    json_response["continents"] = continents
    json_response["prod_class"] = prod_class
    json_response["magic_numbers"] = magic_numbers
    json_response["other"] = query_params

    # raise Exception(time.time() - start)
    # Check the request data type
    if (request.GET.get('data_type', None) is None):
        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse("")
    elif (request.GET.get('data_type', '') == 'json'):
        """Return to browser as JSON for AJAX request"""
        return HttpResponse(json.dumps(json_response))


def api_ccsy(request, trade_flow, country1, country2, year):

    # Get session / request vars
    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))
    lang = helpers.get_language(request)['code']
    name = "name_%s" % lang
    single_year = 'single_year' in request.GET
    country1 = Country.objects.get(name_3char=country1)
    country2 = Country.objects.get(name_3char=country2)

    article = "to" if trade_flow == "export" else "from"

    query_params = request.GET.copy()
    query_params["lang"] = lang
    query_params["product_classification"] = prod_class

    attr = helpers.get_attrs(prod_class=prod_class, name=name)

    if prod_class == "sitc4":
        items = Sitc4_ccpy.objects
    else:
        items = Hs4_ccpy.objects

    items = calculate_export_value_rca(items, trade_flow=trade_flow)
    items = items.extra(select={'name': name})
    items = items.values_list('year', 'product__id', 'product__code',
                              'name', 'product__community_id',
                              'product__community__name',
                              'product__community__color', 'val')

    if single_year:
        items = items.filter(year=year)

    items = items.filter(origin_id=country1.id, destination_id=country2.id)

    json_response = {}

    key = "%s:%s:%s:%s:%s" % (country1.name_3char, country2.name_3char, "show",
                              prod_class, trade_flow)

    cached_data = cache.get(key)
    if cached_data is not None:
        json_response["data"] = msgpack.loads(cached_data)
    else:
        rows = list(items)
        total_val = sum([r[7] for r in rows])

        """Add percentage value to return vals"""
        rows = [{"year": r[0],
                 "item_id":r[1],
                 "abbrv":r[2],
                 "name":r[3],
                 "value":r[7],
                 "share": (r[7] / total_val)*100,
                 "community_id":r[4],
                 "community_name":r[5],
                 "color":r[6],
                 "code":r[2],
                 "id": r[2]} for r in rows]

        json_response["data"] = rows
        cache.set(key, msgpack.dumps(rows), settings.CACHE_LONG)

    years_available = helpers.get_years_available(prod_class=prod_class)
    magic_numbers = helpers.get_inflation_adjustment(country1,
                                                     years_available[0],
                                                     years_available[-1])

    json_response["magic_numbers"] = magic_numbers
    json_response["attr_data"] = Sitc4.objects.get_all(
        lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
    json_response["country1"] = country1.to_json()
    json_response["country2"] = country2.to_json()
    json_response["title"] = "What does %s %s %s %s?" % (
        country1.name, trade_flow, article, country2.name)
    json_response["year"] = year
    json_response["item_type"] = "product"
    json_response["app_type"] = "ccsy"
    json_response["prod_class"] = prod_class
    json_response["attr"] = attr
    json_response["class"] = prod_class
    json_response["other"] = query_params

    # Check the request data type
    if (request.GET.get('data_type', None) is None):
        return HttpResponse("")
    elif (request.GET.get('data_type', '') == 'json'):
        """Return to browser as JSON for AJAX request"""
        return HttpResponse(json.dumps(json_response))


def api_cspy(request, trade_flow, country1, product, year):
    """ country / show / product / year """

    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))
    lang = helpers.get_language(request)['code']
    name = "name_%s" % lang

    product = helpers.get_product_by_code(product, prod_class)
    country1 = Country.objects.get(name_3char=country1)
    single_year = "single_year" in request.GET

    query_params = request.GET.copy()
    query_params["lang"] = lang
    query_params["product_classification"] = prod_class

    region = helpers.get_region_list()
    continents = helpers.get_continent_list()

    if prod_class == "sitc4":
        items = Sitc4_ccpy.objects
    else:
        items = Hs4_ccpy.objects

    items = calculate_export_value_rca(items, trade_flow)
    items = items.extra(select={'name': name})
    items = items.values_list('year', 'destination__id',
                              'destination__name_3char', 'name',
                              'destination__region_id',
                              'destination__continent', 'val')
    items = items.filter(origin_id=country1.id, product_id=product.id)

    if single_year:
        items = items.filter(year=year)

    json_response = {}

    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", product.id,
                              prod_class, trade_flow)

    cached_data = cache.get(key)
    if cached_data is not None:
        json_response['data'] = msgpack.loads(cached_data)
    else:
        rows = list(items)
        total_val = sum([r[6] for r in rows])

        rows = [
            {"year": r[0], "item_id": r[1], "abbrv": r[2], "name": r[3],
             "value": r[6], "share": (r[6] / total_val) * 100,
             "region_id": r[4], "continent": r[5], "id": r[1]}
            for r in rows]

        json_response["data"] = rows
        cache.set(key, msgpack.dumps(rows), settings.CACHE_LONG)

    years_available = helpers.get_years_available(prod_class=prod_class)
    inflation_adjustment = helpers.get_inflation_adjustment(
        country1, years_available[0], years_available[-1])

    json_response["magic_numbers"] = inflation_adjustment
    json_response["attr_data"] = Country.objects.get_all(lang)
    article = "to" if trade_flow == "export" else "from"
    json_response["title"] = "Where does %s %s %s %s?" % (
        country1.name, trade_flow, product.name_en, article)
    json_response["country1"] = country1.to_json()
    json_response["product"] = product.to_json()
    json_response["year"] = year
    json_response["item_type"] = "country"
    json_response["continents"] = continents
    json_response["region"] = region
    json_response["app_type"] = "cspy"
    json_response["class"] = prod_class
    json_response["other"] = query_params

    if (request.GET.get('data_type', None) is None):
        return HttpResponse("")
    elif (request.GET.get('data_type', '') == 'json'):
        return HttpResponse(json.dumps(json_response))
