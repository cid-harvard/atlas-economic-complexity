# -*- coding: utf-8 -*-

# Standard Library
import os
import collections
import json
import string
import time
from urlparse import urlparse

# Django
from django.shortcuts import render_to_response, redirect
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import RequestContext
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve
from django.utils import translation
from django.utils.translation import gettext as _

import cairosvg
from redis_cache.cache import RedisCache

# Local
from observatory.models import (Country, Hs4_cpy, Sitc4_cpy)
from observatory import helpers

if not settings.DB_PREFIX:
    DB_PREFIX = ''
else:
    DB_PREFIX = settings.DB_PREFIX

if not settings.VERSION:
    VERSION = '1.0.0'
else:
    VERSION = settings.VERSION

if not settings.HTTP_HOST:
    HTTP_HOST = '/'
else:
    HTTP_HOST = settings.HTTP_HOST


def home(request):
    c = Country.objects.get(name_2char="us")
    return render_to_response("home.html",
                              {"default_country": c},
                              context_instance=RequestContext(request))


def set_language(request, lang):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    # if request.method == 'GET':
    #   lang_code = request.GET.get('language', None)
    lang_code = lang
    if lang_code:
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
    return response


def set_product_classification(request, prod_class):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if prod_class:
        if hasattr(request, 'session'):
            request.session['product_classification'] = prod_class
            request.session['classification'] = prod_class
    return response


def download(request):

    content = request.POST.get("file_content")
    title = request.POST.get("file_name").replace(" ", "_")
    file_format = request.POST.get("file_format").lower()

    valid_chars = string.ascii_letters + string.digits + "?_"
    title_clean = ''.join(ch for ch in title if ch in valid_chars)

    if len(content) == 0 or "</svg>" not in content:
        return HttpResponse(status=500,
                            content="Invalid svg image.")

    if file_format == "svg":
        response = HttpResponse(content.encode("utf-8"),
                                mimetype="application/octet-stream")

    elif file_format == "pdf":
        response = HttpResponse(cairosvg.svg2pdf(bytestring=content),
                                mimetype="application/pdf")

    elif file_format == "png":
        response = HttpResponse(cairosvg.svg2png(bytestring=content),
                                mimetype="image/png")

    else:
        return HttpResponse(status=500, content="Wrong image format.")

    response[
        "Content-Disposition"] = "attachment; filename=%s.%s" % (title_clean,
                                                                 file_format)

    return response


def explore(
        request,
        app_name,
        trade_flow,
        country1,
        country2,
        product,
        year="2013"):

    request.session['app_name'] = app_name

    was_redirected = request.GET.get("redirect", False)
    lang = helpers.get_language(request)['code']
    crawler = request.GET.get("_escaped_fragment_", False)

    # Get session / request vars
    prod_class = request.GET.get("prod_class",
                                 request.session.get('product_classification',
                                                     'hs4'))

    options = request.GET.copy()
    options["lang"] = lang
    options["product_classification"] = prod_class
    options = options.urlencode()

    # Setup the hash dictionary
    request_hash_dictionary = collections.OrderedDict()

    # Add prod class to request hash dictionary
    request_hash_dictionary['app_name'] = app_name
    request_hash_dictionary['lang'] = lang
    request_hash_dictionary['prod_class'] = prod_class

    # Add the arguments to the request hash dictionary
    request_hash_dictionary['trade_flow'] = trade_flow
    request_hash_dictionary['country1'] = country1
    request_hash_dictionary['country2'] = country2
    request_hash_dictionary['product_type'] = product
    request_hash_dictionary['year'] = year

    # We are here, so let us store this data somewhere
    request_hash_string = "_".join(request_hash_dictionary.values())

    # Code for showing a static image or not
    static_image_name = helpers.url_to_hash(request.path, request.GET)
    if settings.STATIC_IMAGE and os.path.exists(
        os.path.join(settings.STATIC_IMAGE_PATH,
                     static_image_name + ".png")):
        displayviz = True
        displayImage = static_image_name + ".png"
    else:
        displayviz = False
        displayImage = settings.STATIC_URL + "img/all/loader.gif"

    # Verify countries from DB
    countries = [None, None]
    alert = None
    for i, country in enumerate([country1, country2]):
        if country != "show" and country != "all":
            try:
                countries[i] = Country.objects.get(name_3char=country)
            except Country.DoesNotExist:
                alert = {
                    "title": "Country could not be found",
                    "text": """There was no country with the 3 letter
                    abbreviation <strong>%s</strong>. Please double check the
                    <a href='about/data/country/'>list of countries</a>.""" %
                    (country)}

    # The years of data available tends to vary based on the dataset used (Hs4
    # vs Sitc4) and the specific country.
    years_available_model = Sitc4_cpy if prod_class == "sitc4" else Hs4_cpy
    years_available = years_available_model.objects\
        .values_list("year", flat=True)\
        .order_by("year")\
        .distinct()
    # Sometimes the query is not about a specific country (e.g. "all countries"
    # queries) in which case filtering by country is not necessary
    if countries[0]:
        years_available = years_available.filter(country=countries[0].id)
    # Force lazy queryset to hit the DB to reduce number of DB queries later
    years_available = list(years_available)

    if len(years_available) == 0:
        alert = {"title": """The product classification you're using (%s) does
               not seem to include data for the country code (%s) you selected.
               Please try a different product classification or country.""" %
                 (prod_class, countries[0].name)}
        years_available = range(1995, 2012)  # Dummy

    year1_list, year2_list = None, None
    warning, title = None, None
    data_as_text = {}

    prod_or_partner = "partner"

    # To make sure it cannot be another product class
    if prod_class != "hs4" and prod_class != "sitc4":
        prod_class = "sitc4"

    # Test for country exceptions
    if prod_class == "hs4":
        # redirect if and exception country
        if country1 == "blx" or country1 == "lux":
            return redirect(
                HTTP_HOST+'explore/%s/%s/bel/%s/%s/%s/?redirect=true' %
                (app_name, trade_flow, country2, product, year))
        if country1 == "bwa" or country1 == "lso" or country1 == "nam" or country1 == "swz":
            return redirect(
                HTTP_HOST+'explore/%s/%s/zaf/%s/%s/%s/?redirect=true' %
                (app_name, trade_flow, country2, product, year))
    if was_redirected:
        # display warning is redirected from exception
        if country1 == "bel":
            warning = {
                "title": "Country Substitution", "text":
                "In the Harmonized System (HS) classification, trade for Belgium and Luxembourg is reported under 'BEL' ."}
        if country1 == "zaf":
            warning = {
                "title": "Country Substitution", "text":
                "In the Harmonized System (HS) classification, trade for Namibia, Republic of South Africa, Botswana, Lesotho and Swaziland is reported under 'South African Customs Union'."}

    trade_flow_list = [
        ("export", _("Export")), ("import", _("Import")),
        ("net_export", _("Net Export")), ("net_import", _("Net Import"))]
    if (app_name == "product_space" or app_name == "country_space" or app_name == "rings"):
        trade_flow_list = [trade_flow_list[0]]

    year1_list = range(
        years_available[0],
        years_available[
            len(years_available) -
            1] +
        1,
        1)

    if app_name == "stacked" and year == "2009":
        year = "1969.2013.10"

    if "." in year:
        y = [int(x) for x in year.split(".")]
        year_start = y[0]
        year_end = y[1]
        year2_list = year1_list
    else:
        year_start, year_end = None, None
        year = int(year)
        # Check that year is within bounds
        if year > years_available[len(years_available)-1]:
            year = years_available[len(years_available)-1]
        elif year < years_available[0]:
            year = years_available[0]

    api_uri = "api/%s/%s/%s/%s/%s/?%s" % (trade_flow,
                                          country1,
                                          country2,
                                          product,
                                          year,
                                          options)

    redesign_api_uri = "redesign/api/%s/%s/%s/%s/%s/%s" % (prod_class,
                                                           trade_flow,
                                                           country1,
                                                           country2,
                                                           product,
                                                           year)

    country_code = None
    if country1 != "show" and country1 != "all":
        country_code = country1

    if crawler == "":
        view, args, kwargs = resolve(
            "api/%s/%s/%s/%s/%s/" %
            (trade_flow, country1, country2, product, year))
        kwargs['request'] = request
        view_response = view(*args, **kwargs)
        raise Exception(view_response)
        data_as_text["data"] = view_response[0]
        data_as_text["total_value"] = view_response[1]
        data_as_text["columns"] = view_response[2]

    app_type = helpers.get_app_type(country1, country2, product, year)

    # What is actually being shown on the page
    if app_type == "csay" or app_type == "sapy":
      item_type = "country"
    else:
      item_type = "product"


    # Some countries need "the" before their names
    list_countries_the = set(
        ("Cayman Islands",
         "Central African Republic",
         "Channel Islands",
         "Congo, Dem. Rep.",
         "Czech Republic",
         "Dominican Republic",
         "Faeroe Islands",
         "Falkland Islands",
         "Fm Yemen Dm",
         "Lao PDR",
         "Marshall Islands",
         "Philippines",
         "Seychelles",
         "Slovak Republic",
         "Syrian Arab Republic",
         "Turks and Caicos Islands",
         "United Arab Emirates",
         "United Kingdom",
         "Virgin Islands, U.S.",
         "United States"))
    if countries[0] and countries[0].name in list_countries_the:
        countries[0].name = "the "+countries[0].name

    if product not in ("show", "all"):
        p_code = product
        product = helpers.get_product_by_code(p_code, prod_class)

    if not alert:

        # Generate page title depending on visualization being used
        years = [year_start, year_end] if year_start is not None else [year]
        product_name = product.name_en if not isinstance(
            product,
            basestring) else product
        country_names = [getattr(x, "name", None) for x in countries]
        title = helpers.get_title(app_type, app_name,
                                  country_names=country_names,
                                  trade_flow=trade_flow.replace('_', ' '),
                                  years=years,
                                  product_name=product_name
                                  )

        if app_type in ("ccsy", "cspy"):
            if _("net_export") in trade_flow_list:
                del trade_flow_list[trade_flow_list.index(_("net_export"))]
            if _("net_import") in trade_flow_list:
                del trade_flow_list[trade_flow_list.index(_("net_import"))]

        # Should we show the product or partner tab pane?
        # quick fix should be merged with item_type
        if app_type in ["cspy", "sapy"]:
            prod_or_partner = "product"
        elif app_type == "casy":
            if app_name in ("stacked", "map", "tree_map", "pie_scatter", "product_space", "country_space", "rankings", "scatterplot"):
                prod_or_partner = "product"

    # Record views in redis for "newest viewed pages" visualization
    if isinstance(cache, RedisCache):
        views_image_path = settings.STATIC_URL + \
            "data/" + request_hash_string + ".png"
        view_data = {
            "timestamp": time.time(),
            "image": views_image_path,
            "title": title,
            "url": request.build_absolute_uri()
        }
        r = cache.raw_client
        r.rpush("views", json.dumps(view_data))

    previous_page = request.META.get('HTTP_REFERER',
                                           None),

    if previous_page[0] is not None:

      previous_page = previous_page[0]
      previous_image = helpers.url_to_hash(urlparse(previous_page).path, {})

      if os.path.exists(os.path.join(settings.STATIC_IMAGE_PATH,
                                     previous_image + ".png")):
        previous_image = previous_image + ".png"
      else:
        previous_image = settings.STATIC_URL + "img/all/loader.gif"

    else:
      previous_image = settings.STATIC_URL + "img/all/loader.gif"
      previous_page = None

    return render_to_response(
        "explore/index.html",
        {"lang": lang,
         "warning": warning,
         "alert": alert,
         "prod_class": prod_class,
         "data_as_text": data_as_text,
         "app_name": app_name,
         "title": title,
         "trade_flow": trade_flow,
         "country1": countries[0] or country1,
         "country2": countries[1] or country2,
         "country1_3char": countries[0].name_3char if countries[0] else "",
         "country2_3char": countries[1].name_3char if countries[1] else "",
         "product": product,
         "product_code": product.code if not isinstance(product, basestring) else product,
         "years_available": years_available,
         "year": year,
         "year_start": year_start,
         "year_end": year_end,
         "year1_list": year1_list,
         "year2_list": year2_list,
         "trade_flow_list": trade_flow_list,
         "api_uri": api_uri,
         "app_type": app_type,
         "redesign_api_uri": redesign_api_uri,
         "country_code": country_code,
         "prod_or_partner": prod_or_partner,
         "version": VERSION,
         "previous_page": previous_page,
         "previous_image": previous_image,
         "item_type": item_type,
         "displayviz": displayviz,
         "displayImage": displayImage,
         "display_iframe": request.GET.get("display_iframe", False),
         "static_image": request.GET.get("static_image", "loading"),
         },
        context_instance=RequestContext(request))


def explore_random(request):
    """Pick a random country and explore that, for the /explore link on the top
    of the main template."""
    random_country = Country.objects.get_random().name_3char.lower()
    return HttpResponseRedirect(reverse('observatory.views.explore',
                                        args=('tree_map',
                                              'export',
                                              random_country,
                                              'all',
                                              'show',
                                              2012
                                              )))


def api_views(request):
    """Return metadata of the last 15 visits to the site, in JSON."""

    if not isinstance(cache, RedisCache):
        return HttpResponse("")

    r = cache.raw_client
    recent_views = r.lrange("views", -15, -1)
    return HttpResponse("[%s]" % ",".join(recent_views))
