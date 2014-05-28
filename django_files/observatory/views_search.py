from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from elasticsearch import Elasticsearch

import json

from observatory import helpers

def api_search(request):

    query = request.GET.get("term", None)
    if query == None:
        return HttpResponse("[]")

    span, years = helpers.extract_years(query)
    if span is not None:
        # Strip out year expression from query since elasticsearch doesn't
        # contain year data
        query = query[:span[0]] + query[span[1]:]

    if years is None:
        year_string = ""
        year_url_param = ""
    elif len(years) == 1:
        year_string = " (%s)" % years[0]
        year_url_param = "%s/" % years[0]
    else:
        year_string = " (%s to %s)" % (years[0], years[1])
        year_url_param = "%s.%s/" % (years[0], years[1])

    es = Elasticsearch()
    result = es.search(
        index="questions",
        body={
            "query": {
                "filtered": {
                    "query": {
                        "fuzzy_like_this": {
                            "like_text": query,
                            "fields": ["title"],
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
        label = x['_source']['title'] + year_string
        url = x['_source']['url'] + year_url_param
        # TODO: This is a hack, the correct way is to generate the url here
        # instead of pregenerating it. See issue # 134
        if years and len(years) > 1:
            url = url.replace("tree_map", "stacked")
        labels.append(label)
        urls.append(settings.HTTP_HOST + url)

    return HttpResponse(json.dumps([
        query,
        labels,
        [],
        urls
    ]))


def search(request):
    return render_to_response("searchresults.html")
