from django.conf import settings
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from observatory.helpers import get_title, params_to_url
from observatory.models import Country

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
    "caribbean",
    "micronesia",
    "melanesia",
    "polynesia",
    "australia"
]

COUNTRY_CODE = Country.objects\
    .filter(originally_included=True)\
    .values_list("name_3char", flat=True)

# These are different from the product communities in the DB in that the names
# are simplified.
# TODO: maybe put this in the DB as a property? The actual community names are
# too long to be handy to remember
PRODUCT_COMMUNITY = [
    "Animal Products",
    "Vegetable products",
    "Foodstuffs",
    "Mineral Products",
    "Chemicals",
    "Plastics",
    "Leather",
    "Wood Products",
    "Textiles",
    "Footwear",
    "Stone",
    "Metals",
    "Machinery",
    "Transportation",
    "Service"
]
PRODUCT_COMMUNITY_RE = re.compile("|".join(PRODUCT_COMMUNITY),
                                  re.IGNORECASE)

REGIONS_RE = re.compile("|".join(REGIONS), re.IGNORECASE)

API_NAMES = ["casy", "cspy", "csay", "ccsy", "sapy"]
API_NAMES_RE = re.compile("|".join(API_NAMES), re.IGNORECASE)

TRADE_FLOWS = ["import", "export", "net_import", "net_export"]
TRADE_FLOWS_RE = re.compile("|".join(TRADE_FLOWS) + r"(?:s|ed)", re.IGNORECASE)

APP_NAME_SYNONYMS = {"network": "product_space",
                     "treemap": "tree_map",
                     "tree map": "tree_map",
                     "feasibility": "pie_scatter",
                     "stacked graph": "stacked",
                     "product space": "product_space"}
APP_NAMES = ["map", "pie_scatter", "stacked", "product_space", "rings",
             "tree_map"]
APP_NAMES_RE = re.compile("|".join(APP_NAMES + APP_NAME_SYNONYMS.keys()))

PRODUCT_CODE_RE = r"(\d{4})"

COUNTRY_CODE_RE = re.compile(
    r"\b(?:" + "|".join(COUNTRY_CODE) + r")\b",
    re.IGNORECASE)

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
        return results[0].span(), [int(y) for y in years]



def fix_spans(string, match, span):
    """ 'where did germany export to between 2010 and 2012' with 'between (\d+)
    and (\d+)' and (27, 47)"""

    pattern = match.re.pattern

    if "(" in pattern:
        location = pattern.find("(")
        span[0] = span[0] - location

    return span


def remove_spans(string, spans):
    """Given a list of (start, end) index pairs, remove all those from a
    string. This is tricky because if you remove them one by one the indices
    are off. """

    if len(spans) == 0:
        return string

    result = []

    span_iter = iter(spans)
    current_span = span_iter.next()

    for idx, c in enumerate(string):

        if idx < current_span[0]:
            result.append(c)
        elif idx >= current_span[1]:

            current_span = next(span_iter, None)
            if current_span is not None:
                if not (current_span[0] <= idx < current_span[1]):
                    result.append(c)
            else:
                result.append(string[idx:])
                break

    return "".join(result)


def make_extractor(compiled_regex, remove_extracted=True,
                   remove_only_matches=False):
    """Given a regex, gives you back a function that'll use that regex to
    extract data from a string. Specifically it:

        1. Finds all strings matched by the regex
        2. Returns those strings and their start and end positions as a list of
        tuples:
            [(("cat", "fish"), ((2, 5),(8, 12))),
            (("dog", "bone"), ((14, 27),))]
        3. Optionally removes those strings from the original string.
        4. Returns the original string, possibly unchanged depending on (3)

    :param remove_extracted: Whether to remove the extracted string from the
    original or not.
    :param remove_only_matches: If the regex has multiple capturing parentheses
    (a.k.a groups), this will remove only the parenthesized part. So if set to
    True, given r"(\d{4}) to (\d{4})", this will remove both numbers AND the '
    to ', as opposed to removing just the numbers. It will also return multiple
    spans for each removed part. """
    def extractor(query):

        matches = re.finditer(compiled_regex, query)
        results = []
        spans = ()

        for match in matches:
            if remove_extracted:

                if remove_only_matches:
                    # Remove match groups individually
                    group_indices = range(1, len(match.group()) + 1)
                    match_spans = tuple(match.span(i) for i in group_indices)
                else:
                    # Remove whole match at once
                    match_spans = (match.span(), )

                spans += match_spans

            results.append(((match.group(),), match_spans))

        query = remove_spans(query, spans)
        return results, query

    return extractor


# Extractors to run on query string, in order.
# elasticsearch field -> extractor function
EXTRACTORS = OrderedDict([
    ("regions", make_extractor(REGIONS_RE)),
    ("api_name", make_extractor(API_NAMES_RE)),
    ("app_name", make_extractor(APP_NAMES_RE)),
    ("trade_flow", make_extractor(TRADE_FLOWS_RE)),
    ("product_code", make_extractor(PRODUCT_CODE_RE)),
    ("country_codes", make_extractor(COUNTRY_CODE_RE)),
    ("product_community", make_extractor(PRODUCT_COMMUNITY_RE)),
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

    # It matters that years get extracted before product codes since it's much
    # likelier that '2012' is a year than a product code. Years are checked to
    # be within valid bounds, anything that's not a valid year doesn't get
    # stripped from the query and thus can potentially be found as a product
    # code.

    # Extract the remaining common fields like region, product codes etc.
    for extractor_name, extractor in EXTRACTORS.iteritems():
        result, query = extractor(query)
        if len(result):
            kwargs[extractor_name] = [x[0][0] for x in result]

    # Determine query type
    if len(query) == 4 and query in API_NAMES:
        query_type = "api"
    else:
        pass

    return query, query_type, kwargs


def prepare_filters(kwargs):

    filters = defaultdict(list)

    for key in EXTRACTORS.keys():
        if key in kwargs:
            filters[key] += kwargs[key]

    return filters


def api_search(request):

    query = request.GET.get("term", None)
    if query is None:
        return HttpResponse("[]")

    # Parse search query
    query, query_type, kwargs = parse_search(query)

    # Resolve any synonyms. feasibility -> pie_scatter etc.
    if "app_name" in kwargs:
        given_app_name = kwargs["app_name"][0]
        kwargs["app_name"] = [APP_NAME_SYNONYMS.get(given_app_name,
                                                    given_app_name)]

    # Prepare elasticsearch filters
    filters = prepare_filters(kwargs)

    es_query = {
        "query": {
            "filtered": {}
        },
        "size": 8
    }

    # Add filters to the query if they were given. Filters are ANDed.
    if filters:
        es_filters = [{"terms": {k: [x.lower() for x in v]}}
                      for k, v in filters.iteritems()]
        es_filters = {"bool": {"must": es_filters}}
        es_query["query"]["filtered"]["filter"] = es_filters

    # Add fuzzy search for query string if any non-filter query string remains
    # after taking out the filters
    if query.strip() != "":
        es_query["query"]["filtered"]["query"] = {
            "fuzzy_like_this": {
                "like_text": query,
                "fields": ["title"],
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
        data = x['_source']

        # Regenerate title and url so we can add stuff into it dynamically,
        # like the year being searched for, or forcing an app.
        years = kwargs.get('years', None)

        # Possible apps this title could be visualized as
        app_names = data['app_name']

        # If the app the user requested is possible, use that. Otherwise, use
        # the first one as default. App names in the elasticsearch index are
        # sorted in a certain way for this to make sense so check out the
        # indexer script
        requested_app_name = filters.get("app_name", [None])[0]
        if requested_app_name in app_names:
            app_name = requested_app_name
        else:
            app_name = app_names[0]

        if years and len(years) == 2:
            if app_name in ["map", "tree_map"]:
                # If multiple years are specified and we can do a stacked
                # graph, do a stacked graph instead of a treemap or map
                app_name = "stacked"
            elif app_name in ["product_space", "pie_scatter"]:
                # Some apps can never have multiple years so just use the first
                # one specified
                years = [years[0]]

        # If no years specified, use default years
        if years is None:
            if app_name == "stacked":
                years = [1995, 2012]
            else:
                years = [2012]

        title = get_title(
            api_name=data['api_name'],
            app_name=app_name,
            country_names=data.get('country_names', None),
            trade_flow=data['trade_flow'],
            years=years,
            product_name=data.get('product_name', None)
        )
        url = params_to_url(
            api_name=data['api_name'],
            app_name=app_name,
            country_codes=data.get('country_codes', None),
            trade_flow=data['trade_flow'],
            years=years,
            product_code=data.get('product_code', None)
        )

        labels.append(title)
        urls.append(settings.HTTP_HOST + url)

    return HttpResponse(json.dumps([
        query,
        labels,
        [],
        urls
    ]))
