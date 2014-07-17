from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext

from observatory.models import Cy, Hs4_py


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
    import csv

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

    response["Content-Disposition"] = \
        "attachment; filename=%s.csv" % (file_name)

    return response


def get_rankings(category, year):
    from collections import defaultdict
    year = int(year)

    rankings = defaultdict(dict)
    rankings_list = []

    if category == "country":
        year_rankings = Cy.objects\
            .filter(
                year__in=[year, year - 1]
            )\
            .exclude(eci_rank__isnull=True)\
            .exclude(country__name_3char__isnull=True)\
            .exclude(country__name_2char__isnull=True)\
            .exclude(country__region__isnull=True)\
            .exclude(eci_rank=0)\
            .values_list(
                "eci_rank",
                "country__name_3char",
                "country__name_en",
                "eci",
                "year")
    elif category == "product":
        year_rankings = Hs4_py.objects\
            .filter(
                year__in=[year, year - 1])\
            .exclude(pci_rank__isnull=True)\
            .exclude(pci_rank=0)\
            .values_list(
                "pci_rank",
                "product__code",
                "product__name_en",
                "pci",
                "year")

    for r in year_rankings:
        rankings[r[1]][r[4]] = r
    for r in rankings.values():
        if year-1 in r and year in r:
            rankings_list.append(
                [r[year][0], r[year][1], r[year][2], r[year][3],
                 r[year - 1][0] - r[year][0]])
        elif year-1 not in r:
            rankings_list.append(
                [r[year][0], r[year][1], r[year][2], r[year][3], 0])
    rankings_list.sort(key=lambda x: x[0])
    return rankings_list
