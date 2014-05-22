# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext

from observatory.models import Cy, Hs4_py

from collections import defaultdict
import csv
import json

def index(request, category="country", year=2012):
    year = int(year)

    min_year = 1995
    max_year = 2012 if category == "country" else 2012
    if year < min_year:
        return redirect('/rankings/%s/%d/' % (category, max_year))
    elif year > max_year:
        return redirect('/rankings/%s/%d/' % (category, min_year))

    rankings = get_rankings(category, year)

    # get list of all years available for dropdown
    year_list = range(min_year, max_year+1)
    year_list.reverse()

    return render_to_response("rankings/index.html", {
        "category": category,
        "year": year,
        "year_list": year_list,
        "rankings": rankings}, context_instance=RequestContext(request))


def download(request, category="country", year=None):

    min_year = 1995
    max_year = 2012 if category == "country" else 2012

    if category == "country":
        header_row = ["rank", "abbrv", "country", "eci_value", "delta", "year"]
    elif category == "product":
        header_row = ["rank", "sitc4", "product", "pci_value", "delta", "year"]

    response = HttpResponse(mimetype="text/csv;charset=UTF-8")
    csv_writer = csv.writer(
        response,
        delimiter=',',
        quotechar='"')  # , quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(header_row)

    if year:
        rankings = get_rankings(category, year)
        for r in rankings:
            r.append(year)
            csv_writer.writerow(r)
    else:
        for y in range(min_year, max_year):
            rankings = get_rankings(category, y)
            for r in rankings:
                r.append(y)
                csv_writer.writerow(r)

    if year:
        file_name = "%s_rankings_%s" % (category, year)
    else:
        file_name = "%s_rankings" % (category,)

    # Need to change with actual title
    response[
        "Content-Disposition"] = "attachment; filename=%s.csv" % (file_name)

    return response


def get_rankings(category, year, all_fields=False):
    year = int(year)

    rankings = defaultdict(dict)
    rankings_list = []

    if category == "country":

        fields = ["eci_rank", "country__name_3char", "country__name_en", "eci",
                  "year"]

        if all_fields:
            fields += ["gdp", "population"]

        year_rankings = Cy.objects.filter(
            year__in=[year, year-1],
            country__name_3char__isnull=False,
            country__name_2char__isnull=False,
            country__region__isnull=False,
            eci_rank__isnull=False
        ).exclude(
            eci_rank=0
        ).values_list(*fields)

    elif category == "product":

        fields = ["pci_rank", "product__code", "product__name_en", "pci",
                  "year"]

        if all_fields:
            fields += ["world_trade"]

        year_rankings = Hs4_py.objects.filter(
            year__in=[year, year-1]
        ).values_list(*fields)


    # Generate a new dict that looks like:
    # u'KGZ': {2009: (145L, u'KGZ', u'Kyrgyzstan', -0.4462921, 2009),
    # 2010: (177L, u'KGZ', u'Kyrgyzstan', -0.9471428, 2010)}
    for r in year_rankings:
        rankings[r[1]][r[4]] = r

    # Generate a list that looks like:
    # [[219L, u'AGO', u'Angola', -1.937705, -61L],
    # [169L, u'DZA', u'Algeria', -0.8050764, -20L]]
    for r in rankings.values():

        # If previous year and current year data exists, we can calculate delta
        if year-1 in r and year in r:
            delta = r[year - 1][0] - r[year][0]
        else:
            delta = 0

        # Build fields for row
        row = r[year][0:4] + (delta,)
        if all_fields:
            row += r[year][5:]
        rankings_list.append(row)

    rankings_list.sort(key=lambda x: x[0])
    return rankings_list

def api_country_rankings(request, year=2012):
    data = get_rankings("country", year, all_fields=True)
    return HttpResponse(json.dumps({'data':data}),
                        content_type='application/json')

def api_product_rankings(request, year=2012):
    data = get_rankings("product", year, all_fields=True)
    return HttpResponse(json.dumps({'data':data}),
                        content_type='application/json')
