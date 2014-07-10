import os
import collections
import json

from django.conf import settings
from django.http import HttpResponse

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


def api_casy(request, trade_flow, country1, year):
  '''<COUNTRY> / all / show / <YEAR>'''
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
  product = helpers.get_product_by_code(product, prod_class)
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
  product = helpers.get_product_by_code(product, prod_class)
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
