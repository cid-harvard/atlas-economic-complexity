from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponse
from django.template import RequestContext

from observatory.models import Cy, Hs4_py

from operator import itemgetter
from django.conf import settings


def index(request, category="country", year=settings.YEAR_MAX_HS4):
    year = int(year)
    min_year = settings.YEAR_MIN_HS4
    max_year = settings.YEAR_MAX_HS4 if category == "country" else settings.YEAR_MAX_SITC4
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

    min_year = settings.YEAR_MIN_HS4
    max_year = settings.YEAR_MAX_HS4 if category == "country" else settings.YEAR_MAX_SITC4

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
        for y in range(min_year, max_year + 1):
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

    year = int(year)

    if category == "country":
        year_rankings = Cy.objects\
            .filter(
                year__in=[year, year - 1],
                country__originally_included=True
            )\
            .exclude(eci_rank__isnull=True)\
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
                year__in=[year, year - 1]
            )\
            .exclude(pci_rank__isnull=True)\
            .exclude(pci_rank=0)\
            .values_list(
                "pci_rank",
                "product__code",
                "product__name_en",
                "pci",
                "year")

    # Sort by eci_rank and then year
    rankings_sorted = sorted(year_rankings, key=itemgetter(0, 4))

    # Split into two sorted year lists and recalculate ranks because eci_rank
    # doesn't work because it includes countries other than the original 128 we
    # chose for analysis. (country_originally_included)
    rankings_thisyear = [r for r in rankings_sorted if r[4] == year]
    rankings_thisyear = [r + (i + 1,) for i, r in enumerate(rankings_thisyear)]
    rankings_lastyear = [r for r in rankings_sorted if r[4] == year - 1]
    rankings_lastyear = {r[1]: r + (i + 1,) for i, r in enumerate(rankings_lastyear)}

    rankings_with_delta = []
    for i, r in enumerate(rankings_thisyear):

        key = r[1]
        if key not in rankings_lastyear:
            delta = 0
        else:
            delta = rankings_lastyear[key][5] - r[5]

        rankings_with_delta.append([r[5], r[1], r[2], r[3], delta])

    return rankings_with_delta


def growth_predictions(request):
    return render(request, "rankings/growth-predictions.html")

def growth_predictions_latin_america(request):
    return render(request, "rankings/growth-predictions-latin-america.html")
