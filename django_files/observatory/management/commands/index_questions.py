from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

from observatory.models import Country, Hs4
from observatory.helpers import get_title

import itertools


class Command(BaseCommand):
    help = 'Generate elasticsearch indices for questions in homepage'

    def handle(self, *args, **options):

        # TODO: "the" in country names
        country_names = Country.objects.get_valid()\
            .values_list('name_en')
        trade_flows = ["import", "export"]
        # TODO: should this be name_en?
        product_names = Hs4.objects.values_list('name', flat=True)

        # Which products are feasible for Latvia?
        casy_questions = self.generate_titles(['casy'], ['pie_scatter'],
                                              country_names)

        # What did Burundi export in 2013?
        casy_questions2 = self.generate_titles(['casy'],
                                               [None], country_names,
                                               trade_flows, [None])

        # Where did Albania export to in 2009?
        csay_questions = self.generate_titles(['csay'], [None], country_names,
                                              trade_flows, [None])

        # Who exported Petroleum in 1990?
        sapy_questions = self.generate_titles(['sapy'], [None], [None],
                                              trade_flows, [None],
                                              product_names)

        # What did Germany import from Turkey in 2011?
        country_names_flat = Country.objects.get_valid()\
            .values_list('name_en', flat=True)
        country_pairs = itertools.ifilter(
            # Germany importing from Germany etc makes no sense
            lambda country_pair: country_pair[0] != country_pair[1],
            itertools.product(
                country_names_flat,
                country_names_flat),
        )
        ccsy_questions = self.generate_titles(['ccsy'], [None], country_pairs,
                                              trade_flows, [None])

        # Where did France export wine to in 2012?
        cspy_questions = self.generate_titles(['cspy'], [None], country_names,
                                              trade_flows, [None],
                                              product_names)

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
    def generate_titles(*possible_parameters):
        """Given a list of possible parameters for the get_title() function,
        generate all permutations of titles. Parameters must be in order for
        get_title().

        :param possible_parameters: List of lists of possible parameters.
        Should look like: [[param1_possibility1, param1_possibility2],
        [param2_possibility1, param2_possibility2]] etc.
        :return: An iterator yielding titles and arguments e.g:
            [{'title': 'foo', 'country_name': 'Germany'}, {'title': 'bar',
            'country_name': 'Sweden'}]
        """

        arg_names = ['api_name', 'app_name', 'country_names', 'trade_flow',
                     'years', 'product_name']

        def generate_title(args):
            kwargs = dict(zip(arg_names, args))
            kwargs["title"] = get_title(**kwargs)
            return kwargs

        return itertools.imap(
            generate_title,
            itertools.product(*possible_parameters))
