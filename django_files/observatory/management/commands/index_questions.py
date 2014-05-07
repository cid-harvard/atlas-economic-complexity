from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

from observatory.models import Country, Hs4
from observatory.helpers import get_title, params_to_url

import itertools


class Command(BaseCommand):
    help = 'Generate elasticsearch indices for questions in homepage'

    def handle(self, *args, **options):

        # TODO: "the" in country names
        trade_flows = ["import", "export"]
        countries_flat = list(Country.objects.get_valid().only('name_en',
                                                               'name_3char'))
        countries = [[c] for c in countries_flat]
        products = list(Hs4.objects.only('name_en', 'code'))

        # Which products are feasible for Latvia?
        casy_questions = self.generate_titles(['casy'], ['pie_scatter'],
                                              countries)

        # What did Burundi export in 2013?
        casy_questions2 = self.generate_titles(['casy'],
                                               [None], countries,
                                               trade_flows, [None])

        # Where did Albania export to in 2009?
        csay_questions = self.generate_titles(['csay'], [None], countries,
                                              trade_flows, [None])

        # Who exported Petroleum in 1990?
        sapy_questions = self.generate_titles(['sapy'], [None], [None],
                                              trade_flows, [None],
                                              products)

        # What did Germany import from Turkey in 2011?
        country_pairs = itertools.ifilter(
            # Germany importing from Germany etc makes no sense
            lambda country_pair: country_pair[0].id != country_pair[1].id,
            itertools.product(
                countries_flat,
                countries_flat),
        )
        ccsy_questions = self.generate_titles(['ccsy'], [None], country_pairs,
                                              trade_flows, [None])

        # Where did France export wine to in 2012?
        cspy_questions = self.generate_titles(['cspy'], [None], countries,
                                              trade_flows, [None],
                                              products)

        all_questions = itertools.chain(casy_questions, casy_questions2,
                                        csay_questions, sapy_questions,
                                        ccsy_questions, cspy_questions)

        all_questions = enumerate(all_questions)

        es = Elasticsearch()
        for ok, result in streaming_bulk(
            es,
            all_questions,
            index='questions',
            expand_action_callback=self.convert_to_elasticsearch_command
        ):
            if not ok:
                print 'Failed: %s' % result

    @staticmethod
    def convert_to_elasticsearch_command(data):
        """Convert the question list into an elasticsearch `index` command
        consumable by the elasticsearch bulk api."""
        doc_id = data[0]
        doc_body = data[1]

        action = {'index':
                  {'_id': doc_id,
                   '_index': 'questions',
                   '_type': 'question',
                   }}
        return action, doc_body

    @staticmethod
    def generate_index_entries(api_name=None, app_name=None, countries=None,
                               trade_flow=None, years=None, product=None):
        """Given a list of possible parameters for the get_title() and
        params_to_url() functions, generate index entries for all permutations
        of titles. Parameters must be in order for get_title(). Each parameter
        should contain a list of possibilities. For example: api_name=["casy",
        "ccsy"] or countries = [["USA", "DEU"], ["USA", "TUR"]].

        :return: An iterator yielding titles and arguments e.g:
            [{'title': 'foo', 'url':'qux', 'country_name': 'Germany'},
            {'title': 'bar', 'url':'quux', 'country_name': 'Sweden'}]
        """

        def generate_index_entry(args):

            index = {}

            # Generate title
            title = get_title(
                api_name=args[0],
                app_name=args[1],
                country_names=[c.name_en for c in args[2]],
                trade_flow=args[3],
                years=args[4],
                product_names=[p.name_en for p in args[5]],
            )
            index["title"] = title

            # Generate url
            url = params_to_url(
                api_name=args[0],
                app_name=args[1],
                country_codes=[c.name_3char for c in args[2]],
                trade_flow=args[3],
                years=args[4],
                product_codes=[p.code for p in args[5]],
            )
            index["url"] = url

            # TODO: Add in params into elasticsearch in case we need them later

            return index

        parameter_possibilities = [api_name, app_name, countries, trade_flow,
                                   years, product]
        return itertools.imap(
            generate_index_entry,
            itertools.product(*parameter_possibilities)
        )
