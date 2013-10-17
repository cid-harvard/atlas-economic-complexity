#from django.conf.urls import patterns, include, url
#from django.conf.urls import patterns, url
from django.conf.urls.defaults import *
#from django.views.generic.simple import redirect_to
from django.conf.urls import patterns, include
from django.views.generic import TemplateView, RedirectView

# sitemap
from django.conf.urls.defaults import *
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.conf import settings


sitemaps = {
    'flatpages': FlatPageSitemap,
}


if not settings.HTTP_HOST:
  HTTP_HOST = '/'
else:
  HTTP_HOST = settings.HTTP_HOST

class TextPlainView(TemplateView):
  def render_to_response(self, context, **kwargs):
    return super(TextPlainView, self).render_to_response(
      context, content_type='text/plain', **kwargs)


urlpatterns = patterns('',
  
  ## Exploring new patterns
  #(r'^redesign/', include('redesign.urls')),
#  (r'^usa/', include('usa.urls')),
#  (r'^redesign/', include('redesign.urls')), 
  ####                       
  ## Revisiting old patterns 
  ####                    
  
#  (r'^new_ps/', 'observatory.views.new_ps'),
  # internationalization ######################################################
  (r'^i18n/', include('django.conf.urls.i18n')),
  (r'^set_language/(?P<lang>[a-z-]{2,5})/$', 'observatory.views.set_language'),
  
  # product classification ####################################################
  (r'^set_product_classification/(?P<prod_class>[a-z0-9]{3,5})/$', 'observatory.views.set_product_classification'),
  
  # general site ############################################################
  (r'^$', 'observatory.views.home'),
  (r'^download/$', 'observatory.views.download'),
  
  # about section ###########################################################
  (r'^about/$', 'observatory.views.about'),
  (r'^about/data/$', RedirectView.as_view(url='/about/data/sitc4/')), 
  (r'^about/data/(?P<data_type>\w+)/$', "observatory.views.about_data"),
  (r'^about/permissions/$', "observatory.views.permissions"),
  (r'^about/support/$', "observatory.views.support"),  
  (r'^about/research/$', "observatory.views.research"),  
  (r'^about/glossary/$', "observatory.views.glossary"),  
  (r'^about/team/$', "observatory.views.team"), 
  (r'^about/data/$', "observatory.views.data"), 
  (r'^about/permissions/$', "observatory.views.permissions"), 
  (r'^about/privacy/$', "observatory.views.privacy"), 
  # blog
  (r'^about/blog/$', "blog.views.blog_index"),
  url(r'^about/blog/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', "blog.views.blog_post_detail", name="blog_post"),
  
  # book ###################################################################
  (r'^book/$', 'observatory.views.book'),
  
  # API #######################################################################
  (r'^api/$', 'observatory.views.api'),
  (r'^api/apps/$', 'observatory.views.api_apps'),
  (r'^api/data/$', 'observatory.views.api_data'),

  # Story #####
  (r'^mystories/$','observatory.views.minestory'),
  (r'^featured/$','observatory.views.featurestory'),
  (r'^popular/$','observatory.views.popularstory'),
  (r'^published/$','observatory.views.publishstory'),
  (r'^endbrowse/$','observatory.views.endbrowse'),
  (r'^deleteStory/$','observatory.views.deleteStory'),
  (r'^logout/$','observatory.views.logout'),
  (r'^updateEditForm/$','observatory.views.updateEditForm'),
  (r'^stories/view/(?P<browseStoryId>[a-z0-9A-Z=_]+)/$','observatory.views.viewStory'),
  (r'^stories/edit/(?P<editStoryId>[a-z0-9A-Z=_]+)/$','observatory.views.editStoryForm'),
  (r'^cancelstory/$','observatory.views.cancelstory'),
  (r'^endSaveStory/$','observatory.views.endSaveStory'),
  (r'^publishstory/$','observatory.views.published'),
  (r'^likeCount/$','observatory.views.likeCount'),
  (r'^featurestory/$','observatory.views.featured'),
  (r'^endbrowsestory/$','observatory.views.endbrowsestory'),  
  (r'^browsestories/(?P<browseStoryId>\d+)/$','observatory.views.browsestories'),
  (r'^stories/$','observatory.views.browseStoryForm'),
  (r'^endSaveStory/$','observatory.views.endSaveStory'),
  (r'^browseStoryNext/$','observatory.views.browseStoryNext'),
  (r'^browseStoryPrev/$','observatory.views.browseStoryPrev'),
  (r'^createStory/$','observatory.views.createStory'),

  # Explore (App) #############################################################
  # Legacy app redirect
  (r'^app/(?P<app_name>[a-z0-9_]+)/(?P<trade_flow>\w{6,10})/(?P<filter>[a-z0-9\.]+)/(?P<year>[0-9\.]+)/$', 'observatory.views.app_redirect'),
  
  # New app URL structure
  (r'^explore/$', RedirectView.as_view(url=HTTP_HOST+'explore/tree_map/export/usa/all/show/2011/')), 
  (r'^explore/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/(?P<year>[0-9\.]+)/$', 'observatory.views.explore'),
  (r'^explore/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/$', 'observatory.views.explore'),
  
  # Find similar countries
  # (r'^similar/(?P<country>\w{2,3})/(?P<year>[0-9\.]+)/$', 'observatory.views.similar'),
  (r'^similar_wdi/(?P<country>\w{2,3})/(?P<indicator>\d+)/(?P<year>[0-9\.]+)/$', 'observatory.views.similar_wdi'),
    
  # Embed URL
  (r'^embed/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/(?P<year>[0-9\.]+)/$', 'observatory.views.embed'),

  # API #######################################################################
  (r'^api/(?P<trade_flow>[a-z_]{6,10})/(?P<country1>\w{3})/all/show/(?P<year>[0-9\.]+)/$', 'observatory.views.api_casy'),
  (r'^api/(?P<trade_flow>[a-z_]{6,10})/(?P<country1>\w{3})/show/all/(?P<year>[0-9\.]+)/$', 'observatory.views.api_csay'),
  (r'^api/(?P<trade_flow>[a-z_]{6,10})/(?P<country1>\w{3})/(?P<country2>\w{3})/show/(?P<year>[0-9\.]+)/$', 'observatory.views.api_ccsy'),
  (r'^api/(?P<trade_flow>[a-z_]{6,10})/(?P<country1>\w{3})/show/(?P<product>\w{4})/(?P<year>[0-9\.]+)/$', 'observatory.views.api_cspy'),
  (r'^api/(?P<trade_flow>[a-z_]{6,10})/show/all/(?P<product>\w{4})/(?P<year>[0-9\.]+)/$', 'observatory.views.api_sapy'),
  
  (r'^api/near/(?P<country>\w{3})/(?P<year>[0-9\.]+)/(?P<num_prods>\d+)/$', 'observatory.views_exhibit.api_near'),
  
  # Overview (Countries) ######################################################
  (r'^country/(?P<country>\w{2,3})/$', 'observatory.views_overview.country2'),
  (r'^hs4/(?P<product>\d{4})/$', 'observatory.views_overview.product'),
  (r'^sitc4/(?P<product>\d{4})/$', 'observatory.views_overview.product'),
  # (r'^profile/(?P<country>\w{2,3})/(?P<trade_flow>[a-z_]{6})/$', 'observatory.views_overview.country'),
  
  # Overview (Products) ######################################################
  (r'^overview/(?P<product>\d{4})/$', 'observatory.views_overview.product'),
  (r'^overview/(?P<product>\d{4})/(?P<trade_flow>[a-z_]{6})/$', 'observatory.views_overview.product'),

  # Rankings ##################################################################
  (r'^rankings/$', 'observatory.views_rankings.index'),
  (r'^rankings/(?P<category>\w{7})/$', 'observatory.views_rankings.index'),
  (r'^rankings/(?P<category>\w{7})/(?P<year>[0-9\.]+)/$', 'observatory.views_rankings.index'),
  (r'^rankings/(?P<category>\w{7})/download/$', 'observatory.views_rankings.download'),
  (r'^rankings/(?P<category>\w{7})/(?P<year>[0-9\.]+)/download/$', 'observatory.views_rankings.download'),
  
  # Exhibit ###################################################################
  (r'^exhibit/$', 'observatory.views_exhibit.index'),
  (r'^exhibit/country_selection/$', 'observatory.views_exhibit.country_selection'),
  (r'^exhibit/product_selection/$', 'observatory.views_exhibit.product_selection'),
  (r'^exhibit/year_selection/$', 'observatory.views_exhibit.year_selection'),

  # ROBOTS.TXT AND FAVICO ########################################
  url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
  url(r'^favicon\.ico$', RedirectView.as_view(url='/media/img/favicon.ico')),

  url(r'^sitemap\.xml$', RedirectView.as_view(url='/media/sitemaps/sitemap_index.xml')),
  #(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

)
