# stdlib
import urllib2
from subprocess import Popen
import os
import time
import httplib
import glob
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
# Create the store static command


class Command(BaseCommand):
    help = 'Generate the JSON & SVG data for provided url'

    def handle(self, *args, **options):
        # Loop through the provided arguments
        for static_json_data in glob.glob(settings.DATA_FILES_PATH + '/*.store'):
            # Read the data from the file
            store_file = open(static_json_data, "r")
            store_data = store_file.read().strip()
            store_file.close()

            # Split the data to get the parts we want
            data_split = store_data.split("||")

            # If the SVG and PNG file is not available
            if (not os.path.exists(settings.DATA_FILES_PATH + "/" + data_split[2] + ".svg")):
                # Call the generate SVG method
                self.save_svg(data_split[1], data_split[2] + ".svg")

                # Call the generate PNG method
                self.save_png(data_split[2])

                # Sleep a bit and then remove the store file
                time.sleep(10)

            # Remove the store file now
            os.remove(static_json_data)

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
	
	Phantom_timeout = 20
	try:
	    logger.info("PhantomJS Initiated")
	    phantom_execute = Popen(phantom_arguments)
	    waited_so_far = 0
	    while phantom_execute.poll() is None:
		if waited_so_far < Phantom_timeout :
		    time.sleep(1)
		    waited_so_far += 1
		else:
		    phantom_execute.terminate()
	    if phantom_execute.returncode !=0:
		logger.info("SVG Generated..Reading it")
		svgFile = open(settings.DATA_FILES_PATH + "/" + file_name, "r")
		svgData = svgFile.read()
		svgFile.close()
		newSvgData = re.sub(r'id=\"([^"]+)\"', r'id="\1-temp-loader"', svgData)
		newSvgData = re.sub(
		    r'class=\"([^"]+)\"',
		    r'class="\1-temp-loader"',
		    newSvgData)
		svgFile.write(newSvgData)
		svgFile.close()
	    logger.info("Phantom Terminated")
		
	except Exception as ex:
	    logger.error("Runtime Error : %s", ex)

    def save_png(self, file_name):
        # Get the SVG data
        try:
	    logger.info("Creating PNG")
            svg_file = open(
                settings.DATA_FILES_PATH +
                "/" +
                file_name +
                ".svg",
                "r")
            svg_data = svg_file.read()
        except:
            logger.error("Error reading the SVG ")
            return False
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
	img.write_to_png(settings.DATA_FILES_PATH + "/" + file_name +".png")

        logger.info("SVG and PNG Created")
