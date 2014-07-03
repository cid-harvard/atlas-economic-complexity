from observatory.models import (Country, Hs4, Sitc4)
from django.template import RequestContext
from django.shortcuts import render_to_response


def about(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("about/index.html", context_instance=RequestContext(request))


def support(request):
  return render_to_response("about/support.html", context_instance=RequestContext(request))


def research(request):
  return render_to_response("about/research.html", context_instance=RequestContext(request))


def glossary(request):
  return render_to_response("about/glossary.html", context_instance=RequestContext(request))


def team(request):
  return render_to_response("about/team.html", context_instance=RequestContext(request))


def data(request):
  return render_to_response("about/data.html", context_instance=RequestContext(request))


def permissions(request):
  return render_to_response("about/permissions.html", context_instance=RequestContext(request))


def privacy(request):
  return render_to_response("about/privacy.html", context_instance=RequestContext(request))


def about_data(request, data_type):
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  if data_type == "sitc4":
    items = [[getattr(x, "name_%s"% (lang,)), x.code] for x in Sitc4.objects.filter(community__isnull=False)]
    headers = ["Name", "SITC4 Code"]
    title = "SITC4 product names and codes"
  elif data_type == "hs4":
    items = [[x.name, x.code] for x in Hs4.objects.filter(community__isnull=False)]
    headers = ["Name", "HS4 Code"]
    title = "HS4 (harmonized system) product names and codes"
  elif data_type == "country":
    items = [[getattr(x, "name_%s"% (lang,)), x.name_3char] for x in Country.objects.filter(name_3char__isnull=False, name_2char__isnull=False, region__isnull=False)]
    headers = ["Name", "Alpha 3 Abbreviation"]
    title = "Country names and abbreviations"
  items.sort()
  return render_to_response("about/data.html",
    {"items":items, "headers":headers, "title": title},
    context_instance=RequestContext(request))


def api(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("api/index.html", context_instance=RequestContext(request))


def api_apps(request):
  return render_to_response("api/apps.html", context_instance=RequestContext(request))


def api_data(request):
  return render_to_response("api/data.html", context_instance=RequestContext(request))


def book(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("book/index.html", context_instance=RequestContext(request))
