# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ModelForm
from django.conf import settings


if not settings.DB_PREFIX:
  DB_PREFIX = ''
else:
  DB_PREFIX = settings.DB_PREFIX


###############################################################################
#Observa-Story Table
###############################################################################
class observastory(models.Model):
	story_id=models.AutoField(max_length=11,primary_key=True)
	story_name=models.CharField(max_length=200)
	story_desc=models.CharField(max_length=2000,blank=True, null=True)
	published=models.BooleanField(default=0)
        featured=models.BooleanField(default=0)
	likecount=models.IntegerField(default=0)
        user_id=models.IntegerField(max_length=11,default=1)
        number_of_chapters=models.IntegerField(max_length=11,default=0)
	class Meta:
		db_table = "observatory_story"


	def __unicode__(self):
        	return u"%s" % self.story_id

class storyform(ModelForm):

        class Meta:
		model = observastory
        	fields = ('story_name','story_desc')
###############################################################################
# Observa-Story-Chapter-Table
###############################################################################

class storychapter(models.Model):
	chapter_id=models.IntegerField(max_length=11,primary_key=True)
	story_id=models.IntegerField(max_length=11)
	chapter_details=models.CharField(max_length=2000,null=True)
	chapter_url=models.CharField(max_length=500)
        chapter_desc=models.CharField(max_length=500,blank=True, null=True)
        chapter_title=models.CharField(max_length=300)
	chapter_js_details = models.CharField(max_length=2000)
        serial_number=models.IntegerField(max_length=11)

	class Meta:
		db_table = "observatory_story_chapter"

  	def __unicode__(self):
        	return u"%s %s" % (self.chapter_details, self.chapter_url)

class patronform(ModelForm):

	class Meta:
		model = storychapter


###############################################################################
# Observa-Story-User-Table
###############################################################################

class observatoryuser(models.Model):
	user_id=models.AutoField(max_length=11,primary_key=True)
        user_name=models.CharField(max_length=200)
        user_email=models.EmailField(max_length=50,null=True)
	user_auth_type=models.CharField(max_length=100,null=True)
	isadmin =models.BooleanField(default=0)
	class Meta:
		db_table = "observatory_user"

	def __unicode__(self):
		return u"%s" % (self.user_id)



##############################################################################
# Observa-Story-Likemode deatils
#############################################################################

class observatory_like(models.Model):
	user_id=models.IntegerField(max_length=11)
        story_id=models.IntegerField(max_length=11)
	class Meta:
		db_table = "observatory_likemode"

	def __unicode__(self):
		return u"%s" % (self.user_id)


###############################################################################
# country tables
###############################################################################
class Country_region(models.Model):
	name = models.CharField(max_length=50, null=True)
	color = models.CharField(max_length=7, null=True)
	text_color = models.CharField(max_length=7, null=True)

	class Meta:
		db_table = DB_PREFIX+"observatory_country_region"

	def __unicode__(self):
		return self.name

class Country_manager(models.Manager):

	def filter_lang(self, lang):
		return self.extra(select={"name": "name_"+lang})

	def get_all(self, lang):

		if type(lang) == bool:
			lang = "en"
		lang = lang.replace("-", "_")

		countries = self.filter_lang(lang)
		countries = countries.filter(region__isnull=False, name_3char__isnull=False, name_2char__isnull=False).order_by("name_"+lang)
		return list(countries.values(
			"id",
			"name",
			"name_3char",
			"name_2char",
      "continent",
			"region_id",
			"region__color",
			"region__name",
			"region__text_color",
    ))

	def get_valid(self):
	    return self.filter(
			name_3char__isnull=False,
			name_2char__isnull=False,
			region__isnull=False
		)

	def get_random(self):
		"""Grab a random country. This uses the 'ORDER BY RAND()' method which
		is fine for this purpose but slow in mysql for larger tables so
		beware."""
		return self.get_valid().order_by('?')[1]

class Country(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_country"

	name = models.CharField(max_length=200)
	name_numeric = models.PositiveSmallIntegerField(max_length=4, null=True)
	name_2char = models.CharField(max_length=2, null=True)
	name_3char = models.CharField(max_length=3, null=True)
	continent = models.CharField(max_length=50, null=True)
	region = models.ForeignKey(Country_region, null=True)
	capital_city = models.CharField(max_length=100, null=True)
	longitude = models.FloatField(null=True)
	latitude = models.FloatField(null=True)
	coordinates = models.TextField(null=True)
	name_ar = models.TextField(null=True)
	name_de = models.TextField(null=True)
	name_el = models.TextField(null=True)
	name_en = models.TextField(null=True)
	name_es = models.TextField(null=True)
	name_fr = models.TextField(null=True)
	name_he = models.TextField(null=True)
	name_hi = models.TextField(null=True)
	name_it = models.TextField(null=True)
	name_ja = models.TextField(null=True)
	name_ko = models.TextField(null=True)
	name_nl = models.TextField(null=True)
	name_ru = models.TextField(null=True)
	name_pt = models.TextField(null=True)
	name_tr = models.TextField(null=True)
	name_zh_cn = models.TextField(null=True)

	def __unicode__(self):
		return self.name

	def to_json(self):
		return {
			"name": self.name_en,
			"name_3char": self.name_3char}

	objects = Country_manager()

class Cy(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_cy"

	country = models.ForeignKey(Country)
	year = models.PositiveSmallIntegerField(max_length=4)
	eci = models.FloatField(null=True)
	eci_rank = models.PositiveSmallIntegerField(max_length=4)
	oppvalue = models.FloatField(null=True)
	leader = "" #models.CharField(max_length=100, null=True)
	magic = models.FloatField(null=True)
	pc_constant = models.FloatField(null=True)
	pc_current = models.FloatField(null=True)
	notpc_constant = models.FloatField(null=True)

	def __unicode__(self):
		return "%s rank: %d" % (self.country.name, self.eci_rank)

###############################################################################
# product tables
###############################################################################
# Colors for leamer classification of products
class Sitc4_leamer(models.Model):
	name = models.CharField(max_length=30)
	color = models.CharField(max_length=7)
	img = models.FilePathField(null=True)

	def __unicode__(self):
		return self.name + " color: " + self.color

# Colors for Michele Coscia community clustering algorithm
class Sitc4_community(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_sitc4_community"

	code = models.CharField(max_length=4)
	name = models.CharField(max_length=100, null=True)
	color = models.CharField(max_length=7, null=True)
	text_color = models.CharField(max_length=7, null=True)
	img = models.FilePathField(null=True)

	def __unicode__(self):
		return self.code

# SITC4 products
class Sitc4_manager(models.Manager):

	def filter_lang(self, lang):
		if type(lang) is bool:
			lang = "en"
		else:
			lang = lang.replace("-", "_")
		return self.extra(select={"name": "name_"+lang})

	def get_all(self, lang):

		products = self.filter_lang(lang)
		products = products.filter(community__isnull=False)#, ps_size__isnull=False)
		return list(products.values(
			"id",
			"name",
			"code",
			"community_id",
			"community__color",
			"community__name",
			"community__text_color",
			"ps_x",
			"ps_y",
			"ps_size"
		))

class Sitc4(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_sitc4"

	name = models.CharField(max_length=255)
	code = models.CharField(max_length=4)
	conversion_code = models.CharField(max_length=4)
	leamer = models.ForeignKey(Sitc4_leamer, null=True)
	community = models.ForeignKey(Sitc4_community, null=True)
	ps_x = models.FloatField(null=True)
	ps_y = models.FloatField(null=True)
	ps_size = models.FloatField(null=True)
	ps_x_classic = models.FloatField(null=True)
	ps_y_classic = models.FloatField(null=True)
	ps_size_classic = models.FloatField(null=True)
	name_ar = models.TextField(null=True) # Arabic
	name_de = models.TextField(null=True) # German
	name_el = models.TextField(null=True) # Greek
	name_en = models.TextField(null=True) # English
	name_es = models.TextField(null=True) # Spanish
	name_fr = models.TextField(null=True) # France
	name_he = models.TextField(null=True) # Hebrew
	name_hi = models.TextField(null=True) # Hindi
	name_it = models.TextField(null=True) # Italy
	name_ja = models.TextField(null=True) # Japanese
	name_ko = models.TextField(null=True) # Korean
	name_nl = models.TextField(null=True) # Dutch
	name_ru = models.TextField(null=True) # Russian
	name_pt = models.TextField(null=True) # Portuguese
	name_tr = models.TextField(null=True) # Turkish
	name_zh_cn = models.TextField(null=True) # Simplified Chinese
	color = models.TextField(null=True)

	def __unicode__(self):
		return self.code + self.name_en

	def to_json(self):
		return {
			"name": self.name_en,
			"community_id": self.community.id}

	objects = Sitc4_manager()

class Sitc4_py(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_sitc4_py"

	product = models.ForeignKey(Sitc4)
	year = models.PositiveSmallIntegerField(max_length=4)
	pci = models.FloatField(null=True)
	pci_rank = models.PositiveSmallIntegerField(max_length=4)
	world_trade = models.FloatField(null=True)

	def __unicode__(self):
		return "%s rank: %d" % (self.product.name, self.pci_rank)

class Hs4_py(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_hs4_py"

	product = models.ForeignKey('Hs4')
	year = models.PositiveSmallIntegerField(max_length=4)
	pci = models.FloatField(null=True)
	pci_rank = models.PositiveSmallIntegerField(max_length=4)
	world_trade = models.FloatField(null=True)


	def __unicode__(self):
		return "%s rank: %d" % (self.product.name, self.pci_rank)


# Colors for HS4 clusters
# http://www.foreign-trade.com/reference/hscode.htm
class Hs4_community(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_hs4_community"

	code = models.CharField(max_length=4)
	name = models.CharField(max_length=100, null=True)
	color = models.CharField(max_length=7, null=True)
	text_color = models.CharField(max_length=7, null=True)

	def __unicode__(self):
		return self.code

# SITC4 products
class Hs4_manager(models.Manager):

	def filter_lang(self, lang):
		if type(lang) is bool:
			lang = "en"
		else:
			lang = lang.replace("-", "_")
		return self.extra(select={"name": "name_"+lang})

	def get_all(self, lang):
		products = self.filter_lang(lang)
		products = products.filter(community__isnull=False)#, ps_size__isnull=False)
		return list(products.values(
			"id",
			"name",
			"code",
			"community_id",
			"community__color",
			"community__name",
			"community__text_color",
			"ps_x",
			"ps_y",
			"ps_size"
		))

	def get_low_level(self):
		"""Only get low level, detailed products, and don't get the high level
		aggregate categories like: Foodstuffs or Beverages, Spirits &
		Vinegar."""
		return self.filter(id__lte=1241)

# HS4 Products
class Hs4(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_hs4"

	name = models.CharField(max_length=255)
	code = models.CharField(max_length=4)
	conversion_code = models.CharField(max_length=4)
	community = models.ForeignKey(Hs4_community, null=True)
	ps_x = models.FloatField(null=True)
	ps_y = models.FloatField(null=True)
	ps_size = models.FloatField(null=True)
	name_ar = models.TextField(null=True) # Arabic
	name_de = models.TextField(null=True) # German
	name_el = models.TextField(null=True) # Greek
	name_en = models.TextField(null=True) # English
	name_es = models.TextField(null=True) # Spanish
	name_fr = models.TextField(null=True) # France
	name_he = models.TextField(null=True) # Hebrew
	name_hi = models.TextField(null=True) # Hindi
	name_it = models.TextField(null=True) # Italy
	name_ja = models.TextField(null=True) # Japanese
	name_ko = models.TextField(null=True) # Korean
	name_nl = models.TextField(null=True) # Dutch
	name_ru = models.TextField(null=True) # Russian
	name_pt = models.TextField(null=True) # Portuguese
	name_tr = models.TextField(null=True) # Turkish
	name_zh_cn = models.TextField(null=True) # Simplified Chinese

	def __unicode__(self):
		return self.code + self.name

	def to_json(self):
		return {
			"name": self.name_en,
			"community_id": self.community_id}

	objects = Hs4_manager()

###############################################################################
# country - product - year tables
###############################################################################

class Sitc4_cpy(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_sitc4_cpy"

	country = models.ForeignKey(Country)
	product = models.ForeignKey(Sitc4)
	year = models.PositiveSmallIntegerField(max_length=4)
	export_value = models.FloatField(null=True)
	import_value = models.FloatField(null=True)
	export_rca = models.FloatField(null=True)
	distance = models.FloatField(null=True)
	opp_gain = models.FloatField(null=True)

	def __unicode__(self):
		return "CPY: %s.%s.%d" % (self.country.name, self.product.code, self.year)

	# def prod(self, lang):
		# return "%s" % (getattr(self.product, "name_%s" % (lang,)))


class Hs4_cpy(models.Model):

	class Meta:
		db_table = DB_PREFIX+"observatory_hs4_cpy"

	country = models.ForeignKey(Country)
	product = models.ForeignKey(Hs4)
	year = models.PositiveSmallIntegerField(max_length=4)
	export_value = models.FloatField(null=True)
	import_value = models.FloatField(null=True)
	export_rca = models.FloatField(null=True)
	distance = models.FloatField(null=True)
	opp_gain = models.FloatField(null=True)

	def __unicode__(self):
		return "CPY: %s.%s.%d" % (self.country.name, self.product.code, self.year)

###############################################################################
# country - country - product - year tables
###############################################################################
class Sitc4_ccpy(models.Model):

  class Meta:
    db_table = DB_PREFIX+"observatory_sitc4_ccpy"

  year = models.PositiveSmallIntegerField(max_length=4)
  origin = models.ForeignKey(Country, related_name="sitc4_ccpys_origin")
  destination = models.ForeignKey(Country, related_name="sitc4_ccpys_destination")
  product = models.ForeignKey(Sitc4)
  export_value = models.FloatField(null=True)
  import_value = models.FloatField(null=True)

  def __unicode__(self):
    return "%s -> %s" % (self.origin.name, self.destination.name)


class Hs4_ccpy(models.Model):


	class Meta:
		db_table = DB_PREFIX+"observatory_hs4_ccpy"

	year = models.PositiveSmallIntegerField(max_length=4)
	origin = models.ForeignKey(Country, related_name="hs4_ccpys_origin")
	destination = models.ForeignKey(Country, related_name="hs4_ccpys_destination")
	product = models.ForeignKey(Hs4)
	export_value = models.FloatField(null=True)
	import_value = models.FloatField(null=True)

	def __unicode__(self):
		return "%s -> %s" % (self.origin.name, self.destination.name)

class Wdi(models.Model):
  code = models.CharField(max_length=200)
  name = models.CharField(max_length=200)
  desc_short = models.CharField(max_length=255, null=True)
  desc_long = models.TextField(max_length=255, null=True)
  source = models.CharField(max_length=50, null=True)
  topic = models.CharField(max_length=50, null=True)
  aggregation = models.CharField(max_length=50, null=True)

  def __unicode__(self):
    return "%s: %s" % (self.code, self.name)

class Wdi_cwy(models.Model):
  country = models.ForeignKey(Country)
  wdi = models.ForeignKey(Wdi)
  year = models.PositiveSmallIntegerField(max_length=4)
  value = models.FloatField(null=True)

  def __unicode__(self):
    return "[%s] %s: %s" % (self.year, self.country.name_3char, self.wdi.name)

def raw_q(*args, **kwargs):
  '''Returns an array based on the keyword arguments'''
  from django.db import connection, transaction
  cursor = connection.cursor()
  cursor.execute(kwargs["query"])
  # raise Exception(cursor.description)
  # raise Exception(cursor.rowcount)
  return cursor.fetchall()
