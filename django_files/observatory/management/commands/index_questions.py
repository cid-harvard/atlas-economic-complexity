from django.core.management.base import BaseCommand

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

        # e.g. What did Burundi export in 2013? Which products are feasible for
        # Latvia?
        self.generate_titles(['casy'], ['pie_scatter'], country_names)
        self.generate_titles(['casy'],
                             ['stacked', 'treemap',
                              'product_space', 'rings'],
                             country_names, trade_flows, [[]])

        # e.g. Where did Albania export to in 2009?
        self.generate_titles(['csay'], [None], country_names, trade_flows,
                             [[]])

        # e.g. Who exported Petroleum in 1990?
        self.generate_titles(['sapy'], [None], [None], trade_flows, [[]],
                             product_names)

        # e.g. What did Germany import from Turkey in 2011?
        country_names_flat = Country.objects.get_valid()\
            .values_list('name_en', flat=True)
        self.generate_titles(['ccsy'], [None],
                             itertools.product(country_names_flat,
                                               country_names_flat),
                             trade_flows, [[]])
        # TODO: remove dupes where antarctica is exporting to antarctica

        # e.g. Where did France export wine to in 2012?
        self.generate_titles(['cspy'], [None], country_names, trade_flows,
                             [[]], product_names)

    @staticmethod
    def generate_titles(*possible_parameters):
        """Given a list of possible parameters for the get_title() function,
        generate all permutations of outputs. Parameters must be in order for
        get_title().

        :param possible_parameters: List of lists of possible parameters.
        Should look like: [[param1_possibility1, param1_possibility2],
        [param2_possibility1, param2_possibility2]] etc.
        """
        return itertools.imap(
            lambda args: get_title(*args),
            itertools.product(*possible_parameters))
