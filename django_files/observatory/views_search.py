from django.conf import settings
from django.http import HttpResponse
from elasticsearch import Elasticsearch

import json

from observatory import helpers


def generate_year_strings(years):
    """Handle generating URL parts like '2010.2012' or search result additions
    like (2012 to 2014). """
    if years is None:
        year_string = ""
        year_url_param = ""
    elif len(years) == 1:
        year_string = " (%s)" % years[0]
        year_url_param = "%s/" % years[0]
    else:
        year_string = " (%s to %s)" % (years[0], years[1])
        year_url_param = "%s.%s/" % (years[0], years[1])
    return year_string, year_url_param


def parse_search(query):
    """Given a search query string, figure out what kind of search it is."""

    kwargs = {}
    query_type = None

    # Extract years like in "germany france 2012 2014"
    span, years = helpers.extract_years(query)
    if span is not None:
        # Strip out year expression from query since elasticsearch doesn't
        # contain year data
        query = query[:span[0]] + query[span[1]:]
        kwargs["years"] = years
        kwargs["year_string"], kwargs["year_url_param"] = \
            generate_year_strings(years)

    return query, query_type, kwargs


def api_search(request):

    query = request.GET.get("term", None)
    if query is None:
        return HttpResponse("[]")

    query, query_type, kwargs = parse_search(query)

    es = Elasticsearch()
    result = es.search(
        index="questions",
        body={
            "query": {
                "filtered": {
                    "query": {
                        "fuzzy_like_this": {
                            "like_text": query,
                            "fields": ["title", "api_name"],
                            "fuzziness": 3,
                            "max_query_terms": 15,
                            "prefix_length": 4
                        }
                    }
                }
            },
            # "highlight": {
            #     "pre_tags": ["<div class=highlighted>"],
            #     "fields": {"title": {}},
            #     "post_tags": ["</div>"]
            # },
            "size": 8
        })

    labels = []
    urls = []

    for x in result['hits']['hits']:
        label = x['_source']['title'] + kwargs.get('year_string', '')
        url = x['_source']['url'] + kwargs.get('year_url_param', '')
        # TODO: This is a hack, the correct way is to generate the url here
        # instead of pregenerating it. See issue # 134
        if len(kwargs.get('years', '')) > 1:
            url = url.replace("tree_map", "stacked")
        labels.append(label)
        urls.append(settings.HTTP_HOST + url)

    return HttpResponse(json.dumps([
        query,
        labels,
        [],
        urls
    ]))

