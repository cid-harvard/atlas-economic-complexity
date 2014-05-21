# stdlib
import urllib2
from subprocess import Popen
import os
import time
import httplib
import re
# graphics
import cairo
import rsvg
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import get_language_info
from django.conf import settings
# App specific
from observatory.models import *
import logging
logger = logging.getLogger(__name__)

# Setup the path constants

# Setup the supported languages so that we can loop over them
supported_langs = (
    (get_language_info('en'), 'usa'),
    #(get_language_info('es'), 'esp'),
    #(get_language_info('tr'), 'tur'),
    #(get_language_info('ja'), 'jpn'),
    #(get_language_info('it'), 'ita'),
    #(get_language_info('de'), 'deu'),
    #(get_language_info('el'), 'grc'),
    #(get_language_info('fr'), 'fra'),
    #(get_language_info('he'), 'isr'),
    #(get_language_info('ar'), 'sau'),
    #(get_language_info('zh-cn'), 'chn'),
    #(get_language_info('ru'), 'rus'),
    #(get_language_info('nl'), 'nld'),
    #(get_language_info('pt'), 'prt'),
    #(get_language_info('hi'), 'ind'),
    #(get_language_info('ko'), 'kor'),
)

# Setup the supported trade_flow so that we can loop over them
trade_flow_list = ["export"]  # , "import", "net_export", "net_import" ]

# Setup the supported trade_flow so that we can loop over them
app_list = ["tree_map"]  # , "product_space", "stacked", "pie_scatter" ]


class Command(BaseCommand):
    help = 'Generate the JSON & SVG data for all permutations of the data set'

    def handle(self, *args, **options):
        if args:
            path = args[0]
            self.batch_url(path)
        else:
            self.process_url()

    def process_url(self):
        # Setup the product classifications -> years mapping
        # product_classifications = { "Sitc4": Sitc4_cpy.objects.values_list( "year", flat=True ).distinct().order_by( '-year' ),
        #                            "Hs4": Hs4_cpy.objects.values_list( "year", flat=True ).distinct().order_by( '-year' ) }
        product_classifications = {"Sitc4": [2010],
                                   "Hs4": [2010]}

        # Get the different "Product Classifications" and loop over them
        for p_classification, p_classification_years in product_classifications.items():
            # Debug
            self.stdout.write(
                "Handling Product Classification: %s" %
                (p_classification))
            self.stdout.write("\n")

            # Loop over the available years
            for p_classification_year in p_classification_years:
                # Debug
                self.stdout.write("Handling Year: %s" % p_classification_year)
                self.stdout.write("\n")

                # Get a list of all the countries and loop over them
                # countries = Country.objects.values()
                countries = [{'name_3char': "usa"}, {'name_3char': "gha"}]

                # Loop over the countries
                for country in countries:
                    # Loop through all the languages available
                    for language in supported_langs:
                        # Loop through all the apps
                        for app_name in app_list:
                            # Loop through all the trade_flow available
                            for trade_flow in trade_flow_list:
                                # Set the product stuff based on the app
                                if (app_name in ["product_space", "pie_scatter"]):
                                    product_url_bit = 'all/show'
                                    product_file_bit = 'all_show'
                                else:
                                    product_url_bit = 'show/all'
                                    product_file_bit = 'show_all'

                                # Build the API JSON Data URL
                                api_url = "http://" + settings.BACKGROUND_CACHE_URL_HOST + "/api/" + trade_flow + "/" + country['name_3char'].lower() + "/" + product_url_bit + "/" + str(
                                    p_classification_year) + "/?lang=" + language[0]['code'].replace('-', '_') + "&data_type=json&prod_class=" + p_classification.lower() + "&use_app_name=" + app_name

                                # Setup the page url
                                page_url = "http://" + settings.BACKGROUND_CACHE_URL_HOST + "/explore/" + app_name + "/" + trade_flow + "/" + country['name_3char'].lower() + "/" + product_url_bit + "/" + str(
                                    p_classification_year) + "/?lang=" + language[0]['code'].replace('-', '_') + "&prod_class=" + p_classification.lower() + "&headless=true"

                                # Debug
                                self.stdout.write(
                                    'Processing API Request URL --> "%s"' %
                                    api_url)
                                self.stdout.write("\n")

                                # Setup the file name
                                file_name = app_name + "_" + language[0]['code'] + "_" + p_classification.lower(
                                ) + "_" + trade_flow + "_" + country['name_3char'].lower() + "_" + product_file_bit + "_" + str(p_classification_year)
                                extra_store_file = "_" + language[0]['code'] + "_" + p_classification.lower() + "_" + trade_flow + "_" + country[
                                    'name_3char'].lower() + "_" + product_file_bit + "_" + str(p_classification_year)
                                # We only want to do the below for data that
                                # doesn't already exist
                                if (os.path.exists(settings.DATA_FILES_PATH + "/" + file_name + ".svg") is False):
                                    # Call the save_json and let it handle it
                                    # at this point
                                    return_code = self.save_json(
                                        api_url,
                                        file_name +
                                        ".json")

                                    # Check the return code before proceeding
                                    if (return_code is True):
                                        # Call the generate SVG method
                                        self.save_svg(
                                            page_url,
                                            file_name +
                                            ".svg")

                                        # Call the generate PNG method
                                        self.save_png(file_name)

                                        # Let us now remove the json file since
                                        # we don't want it anymore
                                        os.remove(
                                            settings.DATA_FILES_PATH +
                                            "/" +
                                            file_name +
                                            ".json")
                                        # Let us now remove the extra store
                                        # file since we don't want it anymore
                                        if extra_store_file:
                                            os.remove(
                                                settings.DATA_FILES_PATH +
                                                "/" +
                                                extra_store_file +
                                                ".store")
                                    else:
                                        # We have already generated the data
                                        # for this permutation
                                        logger.error(
                                            "There was a problem with retrieving the JSON data set. Skipping ...")
                                    # We should wait for a bit before the next
                                    # one
                                    time.sleep(10)
                                else:
                                    # We have already generated the data for
                                    # this permutation
                                    logger.info(
                                        "Data already exists. Skipping ......")

    def batch_url(self, path):
        # Read the data from the file
        file = open(path, "r")
        url_file = file.read()
        # Close file
        file.close()
        # Converting file-data to array
        for url_list in url_file.split('\n'):
            # Build the API JSON Data URL
            api_url = url_list
            # Setup the page url
            page_url = url_list
            # Debug
            self.stdout.write('Processing API Request URL --> "%s"' % api_url)
            self.stdout.write("\n")
            try:
                # Split the array to get the parts we want
                full_url = url_list.split('explore/')
                # Check Url valid or what
                if full_url != ['']:
                    # Split the array to get the parts we want
                    url_and_session_parameters = full_url[1].split('/?')
                    if len(url_and_session_parameters) == 2:
                        # Split the array to get the parts we want
                        session_parameter = url_and_session_parameters[
                            1].split('&')
                        # Split the array to get the parts we want
                        lang = session_parameter[0].split('=')
                        product_classification = session_parameter[
                            1].split('=')
                        language = lang[1]
                        p_classification = product_classification[1]
                    else:
                        language = "en"
                        p_classification = "hs4"
                    # Split the array to get the parts we want
                    url_parameter = url_and_session_parameters[0].split('/')
                    app_name = url_parameter[0]
                    del url_parameter[0]
                    url_map = '_'.join(url_parameter)
                    # Setup the file name
                    file_name = app_name + "_" + language + \
                        "_" + p_classification + "_" + url_map
                    # We only want to do the below for data that doesn't
                    # already exist
                    if (os.path.exists(settings.DATA_FILES_PATH + "/" + file_name + ".svg") is False):
                        # Call the save_json and let it handle it at this point
                        return_code = self.save_json(
                            api_url,
                            file_name +
                            ".json")
                        # Check the return code before proceeding
                        if (return_code is True):
                            # Call the generate SVG method
                            self.save_svg(page_url, file_name + ".svg")

                            # Call the generate PNG method
                            self.save_png(file_name)

                            # Let us now remove the json file since we don't
                            # want it anymore
                            os.remove(
                                settings.DATA_FILES_PATH +
                                "/" +
                                file_name +
                                ".json")
                        else:
                            # We have already generated the data for this
                            # permutation
                            logger.error(
                                'There was a problem with retrieving the JSON data set. Skipping ...')
                            # We should wait for a bit before the next one
                            time.sleep(10)
                    else:
                        # We have already generated the data for this
                        # permutation
                        logger.info("Data already exists. Skipping ......")
            except:
                logger.error("Invalid url format")

    def save_json(self, api_url, file_name):
        # Wrap everything in a try block
        try:
            # Let us setup the request
            json_request = urllib2.urlopen(api_url)

            # get the data from the request
            json_data = json_request.read()

            # Now we want to write this to file
            json_file = open(settings.DATA_FILES_PATH + "/" + file_name, "w+")
            json_file.write(json_data)
            json_file.close()

            # Set the return code to True
            return True
        except urllib2.URLError as exc:
            # We seem to have run in to problems, degrade gracefully
            logger.error(
                "There was an URLLIB Error processing the HTTP request ...")
            print exc
        except httplib.HTTPException as exc:
            # We seem to have run in to problems, degrade gracefully
            logger.error(
                "There was an HTTP Error processing the HTTP request ...")
            print exc
        except IOError as exc:
            # We seem to have run in to problems, degrade gracefully
            logger.error(
                'There was an IO Error processing the HTTP request ...')
            print exc

        # Return false at this point, since we should not come here
        return False

    def save_svg(self, page_url, file_name):

        logger.info("Creating Visulization - " + file_name)
        # Let us setup the phantomjs script arguments
        phantom_arguments = [
            settings.PHANTOM_JS_EXECUTABLE,
            settings.PHANTOM_JS_SCRIPT,
            settings.DATA_FILES_PATH +
            "/" +
            file_name,
            page_url]

        # Debug
        self.stdout.write("Calling PhantomJS -->")
        self.stdout.write("\n")
        print phantom_arguments

        # Let us setup the request
        phantom_execute = Popen(phantom_arguments)

        # Get the output data from the phantomjs execution
        try:
            execution_results = phantom_execute.communicate()
            return True
        except:
            self.stdout.write("RunTime Error")
            self.stdout.write("\n")
        return False
        # Print the stdout data
        print execution_results[0]

        # Wait until the SVG file is actually generated
        while (os.path.exists(settings.DATA_FILES_PATH + "/" + file_name) != True):
            # Sleep for a bit and then continue with the loop
            time.sleep(20)

        # At this point, we are kind of sure that the SVG file must be created
        # Open up the SVG file and let us try manipulate here itself
        svgFile = open(settings.DATA_FILES_PATH + "/" + file_name, "r")

        # Set the SVG data
        svgData = svgFile.read()

        # Close the file since we don't need it anymore
        svgFile.close()

        # Let us run the replace on the svg data to swap all id attributes
        newSvgData = re.sub(r'id=\"([^"]+)\"', r'id="\1-temp-loader"', svgData)

        # Let us run the replace on the modified svg data to swap all class
        # attributes
        newSvgData = re.sub(
            r'class=\"([^"]+)\"',
            r'class="\1-temp-loader"',
            newSvgData)

        # Let us now write out the modified markup to file
        svgFile = open(settings.DATA_FILES_PATH + "/" + file_name, "w+")

        # Write the markup now
        svgFile.write(newSvgData)

        # Close the file now
        svgFile.close()

    def save_png(self, file_name):
        # Get the SVG data
        svg_file = open(
            settings.DATA_FILES_PATH +
            "/" +
            file_name +
            ".svg",
            "r")
        svg_data = svg_file.read()

        # Create the blank image surface
        img = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            settings.EXPORT_IMAGE_WIDTH,
            settings.EXPORT_IMAGE_HEIGHT)

        # Get the context
        ctx = cairo.Context(img)

        # Dump SVG data to the image context
        handler = rsvg.Handle(None, str(svg_data))
        handler.render_cairo(ctx)

        # Create the final png image
        img.write_to_png(
            settings.DATA_FILES_PATH +
            "/" +
            file_name +
            ".png")

        logger.info("SVG and PNG Created")
