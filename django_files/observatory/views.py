# -*- coding: utf-8 -*-

# Standard Library
import os
import collections
import json
import time
from urlparse import urlparse


# Django
from django.shortcuts import render_to_response, redirect
from django.http import (HttpResponse, Http404, HttpResponsePermanentRedirect,
                         HttpResponseRedirect)
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import gettext as _

# Local
from observatory.models import (Country, Country_region, Cy, Hs4, Hs4_py,
                                Hs4_cpy, Sitc4, Sitc4_py, Sitc4_cpy)
from observatory.models import raw_q
from observatory import helpers

# Conditional things
if settings.REDIS:
  import redis
  import msgpack

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


#Static Images

def url_to_filename(request,Url):
  # set language (if session data available use that as default)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  # set product classification (if session data available use that as default)
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  #Get session parameters
  language=lang
  try:
      view, args, kwargs = resolve(urlparse(Url)[2])
      app_name = kwargs["app_name"]
      trade_flow = kwargs["trade_flow"]
      country1 = kwargs["country1"]
      product = kwargs["product"]
      country2 = kwargs["country2"]
      year = kwargs["year"]
      url = reverse(view, kwargs=kwargs)
      product_file_bit = country2 + "_" + product
      file_name = app_name + "_" + language + "_" + prod_class + "_" + trade_flow + "_" + country1 + "_" + product_file_bit + "_" + str(year)
      response = file_name
      return response
  except Http404:
      print "Invalid Url"

def filename_to_url(request, fileName,):
  # set language (if session data available use that as default)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  # set product classification (if session data available use that as default)
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  #Get session parameters
  language=lang
  # Split the array to get the parts we want
  data=fileName.split('_')
  app_name1=data[0]
  app_name2=data[1]
  if app_name1 == "stacked":
     app_name= data[0]
     lanuage = data[1]
     prod_class = data[2]
     trade_flow = data[3]
     country1 = data[4]
     country2 = data[5]
     product = data[6]
     year= data[7]
     # Build the url
     #url = app_name + "/" + trade_flow + "/" + country1 + "/" + country2 + "/" + product + "/" + year
     url = reverse('observatory.views.explore', kwargs={'app_name': app_name,'trade_flow':trade_flow,'country1':country1,'country2':country2,'product':product,'year':year})
     full_url = request.META['HTTP_HOST'] + '/explore/' + url
     response = full_url
     return response
  if app_name1 == "map":
     app_name= data[0]
     lanuage = data[1]
     prod_class = data[2]
     trade_flow = data[3]
     country1 = data[4]
     country2 = data[5]
     product = data[6]
     year= data[7]
     # Build the url
     #url = app_name + "/" + trade_flow + "/" + country1 + "/" + country2 + "/" + product + "/" + year
     url = reverse('observatory.views.explore', kwargs={'app_name': app_name,'trade_flow':trade_flow,'country1':country1,'country2':country2,'product':product,'year':year})
     full_url = request.META['HTTP_HOST'] + '/explore/' + url
     response = full_url
     return response
  if app_name1 == "tree" or "pie" or "product":
     app_name = data[0] + "_" + data[1]
     language = data[2]
     prod_class = data[3]
     trade_flow = data[4]
     country1 = data[5]
     country2 = data[6]
     product = data[7]
     year= data[8]
     # Build the url
     #url = app_name + "/" + trade_flow + "/" + country1 + "/" + country2 + "/" + product + "/" + year
     url = reverse('observatory.views.explore', kwargs={'app_name': app_name,'trade_flow':trade_flow,'country1':country1,'country2':country2,'product':product,'year':year})
     print url
     full_url = request.META['HTTP_HOST'] + '/explore/' + url
     response = full_url
     return response


def home(request):
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  try:
    ip = request.META["HTTP_X_FORWARDED_FOR"]
  except KeyError:
    ip = request.META["REMOTE_ADDR"]
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
  import cairo, rsvg, xml.dom.minidom
  import csv
  #raise Exception(request.POST)
  content = request.POST.get("content")

  title = request.POST.get("title")

  format = request.POST.get("format")

  if format == "svg" or format == "pdf" or format == "png":
    svg = rsvg.Handle(data=content.encode("utf-8"))
    x = settings.EXPORT_IMAGE_WIDTH
    y = settings.EXPORT_IMAGE_HEIGHT

  if format == "svg":
    response = HttpResponse(content.encode("utf-8"), mimetype="application/octet-stream")

  elif format == "pdf":
    response = HttpResponse(mimetype='application/pdf')
    surf = cairo.PDFSurface(response, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.finish()

  elif format == "png":
    response = HttpResponse(mimetype='image/png')
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.write_to_png(response)

  else:
    response = HttpResponse(mimetype="text/csv;charset=UTF-8")
    csv_writer = csv.writer(response, delimiter=',', quotechar='"')#, quoting=csv.QUOTE_MINIMAL)
    item_list = json.loads(content,encoding='utf-8')
    # raise Exception(content)
    for item in item_list:
      csv_writer.writerow([i.encode("utf-8") for i in item])

  # Need to change with actual title
  response["Content-Disposition"]= "attachment; filename=%s.%s" % (title, format)

  return response


def app_redirect(request, app_name, trade_flow, filter, year):
  # Corrent for old spelling of tree map as one word
  if app_name == "treemap":
    app_name = "tree_map"

  # Bilateral
  if "." in filter:
    bilateral_filters = filter.split(".")

    # Country x Product
    if len(bilateral_filters[1]) > 3:
      country1, country2, product = bilateral_filters[0], "show", bilateral_filters[1]

    # Country x Country
    else:
      country1, country2, product = bilateral_filters[0], bilateral_filters[1], "show"

  # Product
  elif len(filter) > 3:
    country1, country2, product = "show", "all", filter

  # Country
  else:
    country1, country2, product = filter, "all", "show"
  # raise Exception("/explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))
  return HttpResponsePermanentRedirect(HTTP_HOST+"explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))


def explore(request, app_name, trade_flow, country1, country2, product, year="2011"):
  iscreatemode=False
  iscreatemode = request.session['create'] if 'create' in request.session else False
  isbrowsemode=False
  isbrowsemode = request.session['retrieve'] if 'retrieve' in request.session else False
  NoOfChapter=request.session['BrowseStoryChapNos'] if 'BrowseStoryChapNos' in request.session else ""
  browseStoryName=request.session['browseStoryName'] if 'browseStoryName' in request.session else ""
  browseStoryDesc=request.session['browseStoryDesc'] if 'browseStoryDesc' in request.session else ""
  browseChapterName=request.session['browseStoryChapName'] if 'browseStoryChapName' in request.session else ""
  browseChapterDesc=request.session['browseStoryChapterDesc'] if 'browseStoryChapterDesc'in request.session else ""
  browseModeJScript=request.session['browseStoryJScript'] if 'browseStoryJScript' in request.session else ""
  NoOfChpt=request.session['NoOfchap'] if 'NoOfchap' in request.session else ""
  userName=request.session['username'] if 'username' in request.session else ""
  userId=request.session['userid'] if 'userid' in request.session else 0
  likeBtnEnable=request.session['likeBtnEnable'] if 'likeBtnEnable' in request.session else False
  likeCount=request.session['likeCount'] if 'likeCount' in request.session else ""
  #Set app_name to session
  request.session['app_name']=app_name
  # raise Exception(country1, country2, product, year)
  # Get URL query parameters
  was_redirected = request.GET.get("redirect", False)
  crawler = request.GET.get("_escaped_fragment_", False)
  options = request.GET.copy()
  # set language (if session data available use that as default)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  options["lang"] = lang
  # set product classification (if session data available use that as default)
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  options["product_classification"] = prod_class
  options = options.urlencode()
  #Get session parameters
  language=lang
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
  request_hash_string = "_".join( request_hash_dictionary.values() )

  # Check staic image mode
  if( settings.STATIC_IMAGE_MODE == "SVG" ):
    # Check if we have a valid PNG image to display for this
    if os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".png"):
        # display the  static images
        displayviz = True
        displayImage = settings.STATIC_URL + "data/" + request_hash_string + ".png"
    else:
        displayviz=False
        displayImage = settings.STATIC_URL + "img/all/loader.gif"
  else:
    displayviz=False
    displayImage = settings.STATIC_URL + "img/all/loader.gif"

  # Verify countries from DB
  countries = [None, None]
  alert = None
  for i, country in enumerate([country1, country2]):
    if country != "show" and country != "all":
      try:
        countries[i] = Country.objects.get(name_3char=country)
      except Country.DoesNotExist:
        alert = {"title": "Country could not be found",
          "text": "There was no country with the 3 letter abbreviation <strong>%s</strong>. Please double check the <a href='about/data/country/'>list of countries</a>."%(country)}

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

  country1_list, product_list, year1_list, year2_list, year_interval_list, year_interval = None, None, None, None, None, None
  warning, title = None, None
  data_as_text = {}
  # What is actually being shown on the page
  item_type = "product"
  prod_or_partner = "partner"

  # To make sure it cannot be another product class
  if prod_class != "hs4" and prod_class != "sitc4":
    prod_class = "sitc4"

  # Test for country exceptions
  if prod_class == "hs4":
    # redirect if and exception country
    if country1 == "bel" or country1 == "lux":
      return redirect(HTTP_HOST+'explore/%s/%s/blx/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
    if country1 == "bwa" or country1 == "lso" or country1 == "nam" or country1 == "swz":
      return redirect(HTTP_HOST+'explore/%s/%s/zaf/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
  if was_redirected:
    # display warning is redirected from exception
    if country1 == "blx":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Belgium and Luxembourg is reported as 'Belgium-Luxembourg'."}
    if country1 == "zaf":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Namibia, Republic of South Africa, Botswana, Lesotho and Swaziland is reported under 'South African Customs Union'."}

  trade_flow_list = [("export", _("Export")), ("import", _("Import")), ("net_export", _("Net Export")), ("net_import", _("Net Import"))]
  if (app_name == "product_space" or app_name == "rings"):
    trade_flow_list = [trade_flow_list[0]]

  year1_list = range(years_available[0], years_available[len(years_available)-1]+1, 1)

  if app_name == "stacked" and year == "2009":
    year = "1969.2011.10"

  if "." in year:
    y = [int(x) for x in year.split(".")]
    year_start = y[0]
    year_end = y[1]
    year2_list = year1_list
    year_interval_list = range(1, 11)
  else:
    year_start, year_end = None, None
    year = int(year)
    # Check that year is within bounds
    if year > years_available[len(years_available)-1]:
      year = years_available[len(years_available)-1]
    elif year < years_available[0]:
      year = years_available[0]

  api_uri = "api/%s/%s/%s/%s/%s/?%s" % (trade_flow, country1, country2, product, year, options)

  redesign_api_uri = "redesign/api/%s/%s/%s/%s/%s/%s" % (prod_class, trade_flow, country1, country2, product, year)

  country_code = None
  if country1 != "show" and country1 != "all": country_code = country1

  if crawler == "":
    view, args, kwargs = resolve("api/%s/%s/%s/%s/%s/" % (trade_flow, country1, country2, product, year))
    kwargs['request'] = request
    view_response = view(*args, **kwargs)
    raise Exception(view_response)
    data_as_text["data"] = view_response[0]
    data_as_text["total_value"] = view_response[1]
    data_as_text["columns"] = view_response[2]


  app_type = helpers.get_app_type(country1, country2, product, year)

  # Some countries need "the" before their names
  list_countries_the = set(("Cayman Islands", "Central African Republic",
                            "Channel Islands", "Congo, Dem. Rep.",
                            "Czech Republic", "Dominican Republic",
                            "Faeroe Islands", "Falkland Islands", "Fm Yemen Dm",
                            "Lao PDR", "Marshall Islands", "Philippines",
                            "Seychelles", "Slovak Republic",
                            "Syrian Arab Republic", "Turks and Caicos Islands",
                            "United Arab Emirates", "United Kingdom",
                            "Virgin Islands, U.S.", "United States"))
  if countries[0] and countries[0].name in list_countries_the:
    countries[0].name = "the "+countries[0].name

  #p_code, product = None, None
  if product not in ("show", "all"):
    p_code = product
    product = clean_product(p_code, prod_class)

  if not alert:

    # Generate page title depending on visualization being used
    trade_flow = trade_flow.replace('_', ' ')
    years = [year_start, year_end] if year_start is not None else [year]
    product_name = product.name_en if not isinstance(product, basestring) else product
    country_names = [getattr(x, "name", None) for x in countries]
    title = helpers.get_title(app_type, app_name,
                              country_names=country_names,
                              trade_flow=trade_flow,
                              years=years,
                              product_name=product_name
                              )

    if app_type in ("ccsy", "cspy"):
      if _("net_export") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_export"))]
      if _("net_import") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_import"))]
      #trade_flow_list.pop(_("net_export"), None)

    # Should we show the product or partner tab pane?
    # quick fix should be merged with item_type
    if app_type in ["cspy", "sapy"]:
      prod_or_partner = "product"
    elif app_type == "casy":
      if app_name in ("stacked", "map", "tree_map","pie_scatter", "product_space"):
        prod_or_partner = "product"


  # Return page without visualization data

  # Record views in redis for "newest viewed pages" visualization
  if settings.REDIS:
    views_image_path = settings.STATIC_URL + "data/" + request_hash_string + ".png"
    view_data = {
      "timestamp": time.time(),
      "image": views_image_path,
      "title": title,
      "url": request.build_absolute_uri()
    }
    raw = redis.Redis("localhost", db=1)
    raw.rpush("views", json.dumps(view_data))


  return render_to_response("explore/index.html", {
    "displayviz":displayviz,
    "displayImage":displayImage,
    "likeBtnEnable":likeBtnEnable,
    "browseModeJScript": browseModeJScript,
    "browseChapterDesc" : browseChapterDesc,
    "likeCount":likeCount,
    "browseChapterName": browseChapterName,
    "NoOfChapter" : NoOfChapter,
    "browseStoryName": browseStoryName,
    "browseStoryDesc" : browseStoryDesc,
    "isbrowsemode": isbrowsemode,
    "iscreatemode": iscreatemode,
    "userName":userName,
    "userId":userId,
    "language":language,
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
    "year_interval_list": year_interval_list,
    "trade_flow_list": trade_flow_list,
    "api_uri": api_uri,
    "app_type": app_type,
    "redesign_api_uri": redesign_api_uri,
    "country_code": country_code,
    "prod_or_partner": prod_or_partner,
    "version": VERSION,
    "previous_page": request.META.get('HTTP_REFERER', None),
    "item_type": item_type}, context_instance=RequestContext(request))

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


'''<COUNTRY> / all / show / <YEAR>'''
def api_casy(request, trade_flow, country1, year):
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()

  # Store the country code
  country_code = country1
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  single_year = 'single_year' in request.GET

  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  #Get app_name  from session
  app_name = request.session.get( "app_name", "tree_map" ) #request.session['app_name'] if 'app_name' in request.session else "tree_map"
  # See if we have an app name passed as part of the request URL
  forced_app_name = request.GET.get( "use_app_name", None )
  # If we have an app name passed, override and use that
  if ( forced_app_name is not None ):
      # override the app_name in this case, since generate_svg will pass app names specifically
      app_name = forced_app_name
  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class

  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country'] = country_code

  #refererUrl = request.META['HTTP_REFERER']
  #view, args, kwargs = resolve(urlparse(refererUrl)[2])
  #request_hash_string = kwargs['app_name'] + '_' + lang + '_' + prod_class + '_' + kwargs['trade_flow'] + '_' + kwargs['country1'] + '_' + kwargs['country2'] + '_' + kwargs['product'] + '_' + year

  # Set the product stuff based on the app
  if ( app_name in [ "product_space", "pie_scatter" ] ):
      request_hash_dictionary['product_type'] = 'all'
      request_hash_dictionary['product_display'] = 'show'
  else:
      request_hash_dictionary['product_type'] = 'all'
      request_hash_dictionary['product_display'] = 'show'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join( request_hash_dictionary.values() ) #base64.b64encode( request_unique_hash )
  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  # Set proper permissions since we want the cron to remove the file as well
  os.chmod( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", 0777 )

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  # Get attribute information
  if prod_class == "sitc4":
    world_trade = list(Sitc4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])

  elif prod_class == "hs4":
    world_trade = list(Hs4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  # Inflation adjustment
  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                    'pc_constant',
                                                                    'pc_current',
                                                                    'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                "pc_current":i['pc_current'],
                                "notpc_constant":i["notpc_constant"]}


  '''Define parameters for query'''
  if crawler == True or single_year == True:
    year_where = "AND cpy.year = %s" % (year,)
  else:
    year_where = " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"

  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT cpy.year, p.id, p.code, p.name_%s, p.community_id, c.color,c.name, %s, %s, distance, opp_gain, py.pci
    FROM %sobservatory_%s_cpy as cpy, %sobservatory_%s as p, %sobservatory_%s_community as c, %sobservatory_%s_py as py
    WHERE country_id=%s and cpy.product_id = p.id %s and p.community_id = c.id and py.product_id=p.id and cpy.year=py.year
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, country1.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "all", "show", prod_class, trade_flow)
    if single_year:
        key += ":%d" % int(year)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):

      rows = raw_q(query=q, params=None)
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[8],
             "distance":r[9],"opp_gain":r[10], "pci": r[11], "share": (r[7] / total_val)*100,
             "community_id": r[4], "color": r[5], "community_name":r[6], "code":r[2], "id": r[2]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))#, 'data', json.dumps(rows))
      json_response["data"] = rows

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])
    """Add percentage value to return vals"""
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[8],
             "distance":r[9],"opp_gain":r[10], "pci": r[11], "share": (r[7] / total_val)*100,
             "community_id": r[4], "color": r[5], "community_name":r[6], "code":r[2], "id": r[2]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  json_response["attr"] = attr
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "What does %s %s?" % (country1.name, trade_flow.replace("_", " "))
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "casy"
  json_response["magic_numbers"] = magic_numbers
  json_response["world_trade"] = world_trade
  json_response["prod_class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    return HttpResponse(json.dumps(json_response))

def api_sapy(request, trade_flow, product, year):
  # Setup the hash dictionary
  #request_hash_dictionary = { 'trade_flow': trade_flow, 'product': product, 'year': year }
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  product = clean_product(product, prod_class)
  #Set product code to product
  product_code = product.code
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] =  'show'
  request_hash_dictionary['country2'] = 'all'
  request_hash_dictionary['product_dispaly'] = product_code
  request_hash_dictionary['year'] = year
  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()


  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang

  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}


  # Create dictionary of region codes
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  # Create dictinoary for continent groupings
  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"

  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_cpy as cpy, %sobservatory_country as c
    WHERE product_id=%s and cpy.country_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, product.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    # raw = get_redis_connection('default')
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % ("show", "all", product.id, prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])
       # raise Exception(total_val)
      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "id": r[1], "region_id":r[4],"continent":r[5]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])
    # raise Exception(total_val)
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id": r[1], "region_id":r[4],"continent":r[5]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["product"] = product.to_json()
  json_response["title"] = "Who %sed %s?" % (trade_flow.replace("_", " "), product.name_en)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "sapy"
  json_response["attr"] = attr
  json_response["region"]= region
  json_response["continents"] = continents
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))


'''<COUNTRY> / show / product / <YEAR>'''
def api_csay(request, trade_flow, country1, year):
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] =  country1.name_3char.lower()
  request_hash_dictionary['product_dispaly'] = 'show'
  request_hash_dictionary['country2'] = 'all'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )
  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "SUM(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "SUM(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "SUM(export_value) as val"
  else:
    val_col = "SUM(import_value) as val"

  '''Create query [year, id, abbrv, name_lang, val, rca]'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_country as c
    WHERE origin_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, country1.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", "all", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "id":r[1], "region_id":r[4], "continent":r[5]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id":r[1], "region_id":r[4], "continent":r[5]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  """Set article variable for question """
  article = "to" if trade_flow == "export" else "from"

  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "Where does %s %s %s?" % (country1.name, trade_flow, article)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "csay"
  json_response["region"]= region
  json_response["continents"]= continents
  json_response["prod_class"] =  prod_class
  json_response["magic_numbers"] = magic_numbers
  json_response["other"] = query_params

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))


def api_ccsy(request, trade_flow, country1, country2, year):
  # import time
  # start = time.time()
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  country2 = Country.objects.get(name_3char=country2)
  article = "to" if trade_flow == "export" else "from"
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  country_code1=Country.objects.filter(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Get Name in proper lang
  name = "name_%s" % lang
  # Setup the hash dictionary
  request_hash_dictionary1 = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class

  #Set country_code to Country
  country_code1=Country.objects.get(name=country1)
  country_code2=Country.objects.get(name=country2)
  country_code_one=country_code1.name_3char.lower()
  country_code_two=country_code2.name_3char.lower()
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] = country_code_one
  request_hash_dictionary['country2'] = country_code_two
  request_hash_dictionary['product_dispaly'] = 'show'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )
  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}



  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"

  '''Create query'''
  q = """
    SELECT year, p.id, p.code, p.name_%s, p.community_id, c.name, c.color, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_%s as p, %sobservatory_%s_community as c
    WHERE origin_id=%s and destination_id=%s and ccpy.product_id = p.id and p.community_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, country1.id, country2.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    #raw = get_redis_connection('default')
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, country2.name_3char, "show", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if(cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[7] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[5],
               "share": (r[7] / total_val)*100,
               "community_id":r[4],"community_name":r[5],"color":r[6], "code":r[2], "id": r[2]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[5],
             "share": (r[7] / total_val)*100,
             "community_id":r[4],"community_name":r[5],"color":r[6], "code":r[2], "id": r[2]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  json_response["magic_numbers"] = magic_numbers
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["country2"] = country2.to_json()
  json_response["title"] = "What does %s %s %s %s?" % (country1.name, trade_flow, article, country2.name)
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "ccsy"
  json_response["prod_class"] =  prod_class
  json_response["attr"] = attr
  json_response["class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))

def api_cspy(request, trade_flow, country1, product, year):
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  product = clean_product(product, prod_class)
  article = "to" if trade_flow == "export" else "from"

  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  #Set product code to particular product
  product_display = product.code
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] = country1
  request_hash_dictionary['country1'] = 'show'
  request_hash_dictionary['product_display'] = product_display
  request_hash_dictionary['year'] = year
  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values()) #base64.b64encode( request_unique_hash )

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"

  '''Create query'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_country as c
    WHERE origin_id=%s and ccpy.product_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, country1.id, product.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", product.id,  prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)

    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows


  article = "to" if trade_flow == "export" else "from"

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  json_response["magic_numbers"] = magic_numbers
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["title"] = "Where does %s %s %s %s?" % (country1.name, trade_flow, product.name_en, article)
  json_response["country1"] = country1.to_json()
  json_response["product"] = product.to_json()
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["continents"]= continents
  json_response["region"]= region
  json_response["app_type"] = "cspy"
  json_response["class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))

# Embed for iframe
def embed(request, app_name, trade_flow, country1, country2, product, year):
  lang = request.GET.get("lang", "en")
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  query_string = request.GET.copy()
  query_string["product_classification"] = prod_class
  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  return render_to_response("explore/embed.html", {"app":app_name, "trade_flow": trade_flow, "country1":country1, "country2":country2, "product":product, "year":year, "other":json.dumps(query_string),"years_available":json.dumps(years_available), "lang":lang})


def api_views(request):
  r = redis.Redis(db=1)
  recent_views = r.lrange("views", -15, -1)
  return HttpResponse("[%s]" % ",".join(recent_views))


###############################################################################
## Helpers
###############################################################################
def clean_country(country):
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

def clean_product(product, prod_class):
  # first try looking up based on 3 character code
  if prod_class == "hs4":
    try:
      p = Hs4.objects.get(code=product)
    except Hs4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Sitc4.objects.get(code=product).conversion_code
        p = Hs4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  else:
    try:
      p = Sitc4.objects.get(code=product)
    except Sitc4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Hs4.objects.get(code=product).conversion_code
        p = Sitc4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  return p

def get_country_lookup():
  lookup = {}
  for c in Country.objects.all():
    lookup[c.id] = [c.name_en, c.name_3char]
  return lookup

