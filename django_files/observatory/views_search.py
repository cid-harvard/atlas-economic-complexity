from django.conf import settings
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from collections import defaultdict, OrderedDict
import json
import re

# These are different from the regions in the DB in that they are a bit more
# generalized.
REGIONS = [
    "europe",
    "asia",
    "america",
    "africa",
    "carribean",
    "micronesia",
    "melanesia",
    "polynesia",
    "australia"
]

REGIONS_RE = re.compile("|".join(REGIONS), re.IGNORECASE)

API_NAMES = ["casy", "cspy", "csay", "ccsy", "sapy"]
API_NAMES_RE = re.compile("|".join(API_NAMES), re.IGNORECASE)

TRADE_FLOWS = ["import", "export", "net_import", "net_export"]
TRADE_FLOWS_RE = re.compile("|".join(TRADE_FLOWS), re.IGNORECASE)

YEAR_EXPRESSIONS = [
    re.compile(r'between (\d{4}) and (\d{4})', re.IGNORECASE),
    re.compile(r'from (\d{4}) to (\d{4})', re.IGNORECASE),
    re.compile(r'(\d{4}).*(\d{4})'),
    re.compile(r'(?:in|at|during) (\d{4})', re.IGNORECASE),
    re.compile(r'(\d{4})')
]


def extract_years(input_str):
    """Extract things that look like years out of a given plaintext."""
    results = (exp.search(input_str) for exp in YEAR_EXPRESSIONS)
    results = [result for result in results if result is not None]

    if len(results) == 0:
        return None, None
    else:
        years = results[0].groups()
        for year in years:
            if not (1995 <= int(year) <= 2013):
                return None, None
        return results[0].span(), years


def extract_product_code(query):
    """Returns only first product code."""
    result = re.search(r"(\d{4})", query)

    if result is None:
        return None, None
    else:
        return result.span(), result.groups()[0]


def make_extractor(compiled_regex):
    def inner(query):
        return re.findall(compiled_regex, query)
    return inner


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


# Extractors to run on query string, in order.
EXTRACTORS = OrderedDict([
    ("regions", make_extractor(REGIONS_RE)),
    ("api_names", make_extractor(API_NAMES_RE)),
    ("trade_flows", make_extractor(TRADE_FLOWS_RE)),
])


def parse_search(query):
    """Given a search query string, figure out what kind of search it is."""

    kwargs = {}
    query_type = None

    # Extract years like in "germany france 2012 2014"
    span, years = extract_years(query)
    if years is not None:
        # Strip out year expression from query since elasticsearch doesn't
        # contain year data
        query = query[:span[0]] + query[span[1]:]
        kwargs["years"] = years
        kwargs["year_string"], kwargs["year_url_param"] = \
            generate_year_strings(years)

    # It matters that years get extracted before product codes since it's much
    # likelier that '2012' is a year than a product code. Years are checked to
    # be within valid bounds, anything that's not a valid year doesn't get
    # stripped from the query and thus can potentially be found as a product
    # code.

    # Extract product code
    span, product_code = extract_product_code(query)
    if product_code is not None:
        query = query[:span[0]] + query[span[1]:]
        kwargs["product_code"] = product_code

    # Extract the remaining common fields like region, product codes etc.
    for extractor_name, extractor in EXTRACTORS.iteritems():
        result = extractor(query)
        if len(result):
            kwargs[extractor_name] = result

    # Determine query type
    if len(query) == 4 and query in API_NAMES:
        query_type = "api"
    else:
        pass

    return query, query_type, kwargs


def prepare_filters(kwargs):

    filters = defaultdict(list)

    if "regions" in kwargs:
        filters["region"] += kwargs["regions"]

    if "api_names" in kwargs:
        filters["api_name"] += kwargs["api_names"]

    if "trade_flows" in kwargs:
        filters["trade_flow"] += kwargs["trade_flows"]

    if "product_code" in kwargs:
        filters["product_code"].append(kwargs["product_code"])

    return filters


def api_search(request):

    query = request.GET.get("term", None)
    if query is None:
        return HttpResponse("[]")

    query, query_type, kwargs = parse_search(query)
    filters = prepare_filters(kwargs)

    es_query = {
        "query": {
            "filtered": {}
        },
        # "highlight": {
        #     "pre_tags": ["<div class=highlighted>"],
        #     "fields": {"title": {}},
        #     "post_tags": ["</div>"]
        # },
        "size": 8
    }

    # Add filters to the query if they were given. Filters are ANDed.
    if filters:
        es_filters = [{"terms": {k: v}} for k, v in filters.iteritems()]
        es_filters = {"bool": {"must": es_filters}}
        es_query["query"]["filtered"]["filter"] = es_filters

    # Add fuzzy search for query string if any non-filter query string remains
    # after taking out the filters
    if query.strip() != "":
        es_query["query"]["filtered"]["query"] = {
            "fuzzy_like_this": {
                "like_text": query,
                "fields": ["title"],
                "fuzziness": 3,
                "max_query_terms": 15,
                "prefix_length": 4
            }
        }

    # Do the query
    es = Elasticsearch()
    result = es.search(index="questions", body=es_query)

    # Format the results in a way that complies with the OpenSearch standard's
    # suggestion extension
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
