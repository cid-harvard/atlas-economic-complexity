from django.conf import settings
from django.utils.translation import get_language_info

from cache_utils.decorators import cached

from observatory.models import (Hs4_cpy, Sitc4_cpy, Country, Hs4, Sitc4,
                                Sitc4_py, Hs4_py, Cy, Country_region)

import hashlib
from collections import OrderedDict
from django.utils.translation import ugettext as _


# make sure app name is in the list of possible apps
def get_app_name(app_name):
    possible_apps = ["tree_map", "stacked", "product_space", "map"]

    # if the app_name requested is not in the list of possibilities
    if app_name not in possible_apps:
        app_name = None

    return app_name


# make sure this is accepted trade_flow
def get_trade_flow(trade_flow):
    possible_yoga_flows = ["export", "import", "net_export", "net_import"]

    if trade_flow not in possible_yoga_flows:
        trade_flow = None

    return trade_flow


def get_years(classification):
    # get distince years from db, different for diff product classifications

    if classification == "sitc4":
        years_available = list(
            Sitc4_cpy.objects.values_list(
                "year",
                flat=True).distinct())
    elif classification == "hs4":
        years_available = list(
            Hs4_cpy.objects.values_list(
                "year",
                flat=True).distinct())

    return years_available


# Returns app type in CCPY format
def get_app_type(country1, country2, product, year):

    # country / all / show / year
    if country2 == "all" and product == "show":
        return "casy"

    # country / show / all / year
    elif country2 == "show" and product == "all":
        return "csay"

    # show / all / product / year
    elif country1 == "show" and country2 == "all":
        return "sapy"

    # country / country / show / year
    elif product == "show":
        return "ccsy"

    #  country / show / product / year
    else:
        return "cspy"


# Returns the Country object or None
def get_country(country):
    # first try looking up based on 3 character code
    try:
        c = Country.objects.get(name_3char=country)
    except Country.DoesNotExist:
        # next try 2 character code
        try:
            c = Country.objects.get(name_2char=country)
        except Country.DoesNotExist:
            c = None
    return c


def get_product_by_code(product_code, classification="hs4"):
    """Look up a product code in a given product code with fallback to
    another."""
    if classification == "hs4":
        try:
            p = Hs4.objects.get(code=product_code)
        except Hs4.DoesNotExist:
            try:
                conv_code = Sitc4.objects\
                    .get(code=product_code).conversion_code
                p = Hs4.objects.get(code=conv_code)
            except (Hs4.DoesNotExist, Sitc4.DoesNotExist):
                p = None
    else:
        try:
            p = Sitc4.objects.get(code=product_code)
        except Sitc4.DoesNotExist:
            try:
                conv_code = Hs4.objects\
                    .get(code=product_code).conversion_code
                p = Sitc4.objects.get(code=conv_code)
            except (Hs4.DoesNotExist, Sitc4.DoesNotExist):
                p = None
    return p


def get_time_clause(years):
    """Generate a string like 'between 2005 and 2007' or 'in 2011' from a list
    of years. Beginning space is included to allow for empty time clause."""
    if years is None or len(years) == 0:
        return ""
    elif len(years) == 1:
        return " in %d" % years[0]
    else:
        return " between %d and %d" % (years[0], years[1])


def get_title(api_name, app_name, country_names=None, trade_flow=None,
              years=None, product_name=None):
    """Fetch the natural-languageized title of a page based on the data being
    displayed.

    :param api_name: One of: casy, cspy, csay, ccsy, sapy
    :param app_name: E.g. pie_scatter, stacked, product_space, rings ...
    :param list country_names: List of country name strings. If multiple, first
    is "from" country and second is the "to" country.
    :param str trade_flow: import, export, net_import, net_export
    :param list years: List of years. If multiple, first is the start year and
    second is the end year.
    :param str product_name: Localized name of product
    """
    # e.g. What did Burundi export in 2013? Which products are feasible for
    # Latvia?
    if api_name == "casy":
        if app_name == "pie_scatter":
            pre_def_str = _("Which products are feasible for ")
            return "%s%s%s?" % (pre_def_str,
                                country_names[0],
                                get_time_clause(years))
        else:
            pre_def_str = _("What did")
            return "%s %s %s%s?" % (pre_def_str,
                                    country_names[0],
                                    trade_flow,
                                    get_time_clause(years))

    # e.g. Where did Albania export to in 2009?
    elif api_name == "csay":
        article = "to" if trade_flow == "export" else "from"
        pre_def_str = _("Where did")
        return "%s %s %s %s%s?" % (pre_def_str,
                                   country_names[0],
                                   trade_flow,
                                   article,
                                   get_time_clause(years))

    # e.g. Who exported Petroleum in 1990?
    elif api_name == "sapy":
        pre_def_str = _("Who")
        return "%s %sed %s%s?" % (trade_flow, product_name,
                                  get_time_clause(years))

    # e.g. What did Germany import from Turkey in 2011?
    elif api_name == "ccsy":
        article = "to" if trade_flow == "export" else "from"
        pre_def_str = _("What did")
        return "%s %s %s %s %s%s?" % (pre_def_str,
                                      country_names[0],
                                      trade_flow,
                                      article, country_names[1],
                                      get_time_clause(years))

    # e.g. Where did France export wine to in 2012?
    elif api_name == "cspy":
        article = "to" if trade_flow == "export" else "from"
        pre_def_str = _("Where did")
        return "%s %s %s %s %s%s?" % (pre_def_str,
                                      country_names[0], trade_flow,
                                      product_name, article,
                                      get_time_clause(years))

    else:
        raise ValueError("Unknown API name when trying to generate title: %s" %
                         api_name)


def params_to_url(api_name=None, app_name=None, country_codes=None,
                  trade_flow=None, years=None, product_code=None):
    """Generate explore/ urls from specific parameters. Same parameter syntax
    as get_title, but product code instead of product name and 3 letter country
    codees instead of country names."""

    if app_name is None:
        # Treemap is a safe default that works with almost all of our data
        app_name = 'tree_map'

    if api_name == 'casy':
        # What did Germany import in 2012?
        # Which products are feasible for Latvia?
        # Looks like explore/tree_map/import/deu/all/show/2012/
        country_codes.append('all')
        product_code = "show"

    elif api_name == 'cspy':
        # Where did Germany import Swine from in 2012?
        # Looks like explore/tree_map/import/deu/show/0103/2012/
        country_codes.append('show')

    elif api_name == 'csay':
        # Where does germany import from?
        # Looks like explore/tree_map/import/deu/show/all/2012/
        country_codes.append('show')
        product_code = 'all'

    elif api_name == 'ccsy':
        # What did Germany import from Congo in 2012?
        # Looks like explore/tree_map/import/deu/cog/show/2012/
        product_code = 'show'

    elif api_name == 'sapy':
        # Who exports potatoes?
        # Looks like explore/tree_map/export/show/all/0101/2012/
        country_codes = ("show", "all")

    else:
        raise ValueError("Unknown API name : %s" % api_name)

    url = "explore/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country_codes[0],
                                       country_codes[1], product_code)
    if years is not None:
        url += "%s/" % years_to_string(years)

    return url


@cached(settings.CACHE_VERY_LONG)
def get_world_trade(prod_class="hs4"):
    """Get world trade volume for every product in a classification."""
    if prod_class == "sitc4":
        return list(
            Sitc4_py.objects.all().values(
                'year',
                'product_id',
                'world_trade'))
    elif prod_class == "hs4":
        return list(
            Hs4_py.objects.all().values(
                'year',
                'product_id',
                'world_trade'))


@cached(settings.CACHE_VERY_LONG)
def get_attrs(prod_class="hs4", name="name_en"):
    """Get extraneous attributes (like color and code) for each product in a
    classification."""
    if prod_class == "sitc4":
        attr_list = list(
            Sitc4.objects.all().values(
                'code',
                name,
                'id',
                'color'))
        attr = {}
        for i in attr_list:
            attr[i['code']] = {
                'code': i['code'],
                'name': i[name],
                'color': i['color']}
    elif prod_class == "hs4":
        attr_list = list(
            Hs4.objects.all().values(
                'code',
                name,
                'id',
                'community_id__color'))
        attr = {}
        for i in attr_list:
            attr[
                i['code']] = {
                'code': i['code'],
                'name': i[name],
                'item_id': i['id'],
                'color': i['community_id__color']}
    return attr


@cached(settings.CACHE_VERY_LONG)
def get_years_available(prod_class="hs4"):
    """Get years available for a given classification."""
    if prod_class == "sitc4":
        years_available = Sitc4_cpy.objects\
            .values_list("year", flat=True).distinct()
    else:
        years_available = Hs4_cpy.objects\
            .values_list("year", flat=True).distinct()
    return sorted(list(years_available))


@cached(settings.CACHE_VERY_LONG)
def get_inflation_adjustment(country, first_year, last_year):
    """For a given country and year range, get inflation adjustment
    constants."""
    inflation_constants = Cy.objects\
        .filter(country=country.id,
                year__range=(first_year,
                             last_year))\
        .values('year',
                'pc_constant',
                'pc_current',
                'notpc_constant')
    magic_numbers = {}
    for year in inflation_constants:
        magic_numbers[year['year']] = {
            "pc_constant": year['pc_constant'],
            "pc_current": year['pc_current'],
            "notpc_constant": year["notpc_constant"]}
    return magic_numbers


@cached(settings.CACHE_VERY_LONG)
def get_region_list():
    region_list = list(Country_region.objects.all().values())
    region = {}
    for i in region_list:
        region[i['id']] = i
    return region


@cached(settings.CACHE_VERY_LONG)
def get_continent_list():
    continent_list = list(Country.objects.all().distinct().values('continent'))
    continents = {}
    for i, k in enumerate(continent_list):
        continents[k['continent']] = i*1000
    return continents


def get_language(request):
    """Given a request, check the GET params and then the session to find
    language info specified in 2 char ISO code form, and then make sure it's
    valid, and return a tuple in the format of django's get_language_info.
    Nonexistent languages raise KeyError."""
    lang = request.GET.get("lang",
                           request.session.get('django_language', 'en'))
    return get_language_info(lang)


def years_to_string(years):
    year_tuple = tuple(years)
    if len(year_tuple) == 1:
        return "%d" % year_tuple
    elif len(year_tuple) == 2:
        return "%d.%d" % year_tuple
    elif len(year_tuple) == 3:
        return "%d.%d..%d" % year_tuple
    else:
        raise ValueError("Invalid year tuple")


def url_to_hash(url, query_params_dict):
    """Turn a URL into a canonical base64 hash, useful for saving specific
    urls, e.g. when saving history or to a file. One caveat is that if you pass
    in a django request.GET, watch out if you have two GET parameters with the
    same key (HTTP spec allows for this). request.GET.iteritems() returns
    only the last value for that key but request.GET.iterlists() returns all
    values.

    :param url: URL relative to django root
    :param query_params_dict: dict of GET parameters, will be sorted and keys
    lowercased to remove duplicates.
    """

    string = str(url) + str(OrderedDict(sorted(query_params_dict.iteritems(),
                                               key=lambda x: x[0])))
    return hashlib.md5(string).hexdigest()
