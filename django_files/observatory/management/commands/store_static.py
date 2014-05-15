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
class Command( BaseCommand ):
    help = 'Generate the JSON & SVG data for provided url'

    def handle(self, *args, **options):
        # Loop through the provided arguments
        for static_json_data in glob.glob( settings.DATA_FILES_PATH + '/*.store' ):
            # Read the data from the file
            store_file = open( static_json_data, "r" )
            store_data = store_file.read().strip()
            store_file.close()
            
            # Split the data to get the parts we want
            data_split = store_data.split( "||" )
                
            # If the SVG and PNG file is not available
            if ( not os.path.exists( settings.DATA_FILES_PATH + "/" + data_split[2] + ".svg" ) ):
                # Call the generate SVG method
                self.save_svg( data_split[1], data_split[2] + ".svg" )
                
                # Call the generate PNG method
                self.save_png( data_split[2] )
                
                # Sleep a bit and then remove the store file
                time.sleep( 10 )
            
            # Remove the store file now
            os.remove( static_json_data )
        
    def save_svg( self, page_url, file_name ):

	logger.info("Creating Visulization - " + file_name) 
        # Let us setup the phantomjs script arguments
        phantom_arguments = [ settings.PHANTOM_JS_EXECUTABLE, settings.PHANTOM_JS_SCRIPT, settings.DATA_FILES_PATH + "/" + file_name, page_url ]
        
        # Debug
        #self.stdout.write( "Calling PhantomJS -->" )
        #self.stdout.write( "\n" )
        #print phantom_arguments
        
        # Let us setup the request
        phantom_execute = Popen( phantom_arguments )
        
        # Get the output data from the phantomjs execution
        try:
            execution_results = phantom_execute.communicate()
	    return True
  	except:
 	      self.stdout.write( "RunTime Error" )
              self.stdout.write( "\n" )
 	      logger.error( "RunTime Error") 
        return False
        # Print the stdout data
        print execution_results[0]
        
        # Wait until the SVG file is actually generated
        while ( os.path.exists( settings.DATA_FILES_PATH + "/" + file_name ) != True ):
            # Sleep for a bit and then continue with the loop
            time.sleep( 20 )

        # At this point, we are kind of sure that the SVG file must be created
        # Open up the SVG file and let us try manipulate here itself
        svgFile = open( settings.DATA_FILES_PATH + "/" + file_name, "r" )

        # Set the SVG data
        svgData = svgFile.read()

        # Close the file since we don't need it anymore
        svgFile.close()

        # Let us run the replace on the svg data to swap all id attributes
        newSvgData = re.sub( r'id=\"([^"]+)\"', r'id="\1-temp-loader"', svgData )

        # Let us run the replace on the modified svg data to swap all class attributes
        newSvgData = re.sub( r'class=\"([^"]+)\"', r'class="\1-temp-loader"', newSvgData )

        # Let us now write out the modified markup to file
        svgFile = open( settings.DATA_FILES_PATH + "/" + file_name, "w+" )

        # Write the markup now
        svgFile.write( newSvgData )

        # Close the file now
        svgFile.close()

    def save_png( self, file_name ):
        # Get the SVG data. Defensive code to prevent code freeze in case of corrupt svg data
        try:
            svg_file = open( settings.DATA_FILES_PATH + "/" + file_name + ".svg", "r" )
            svg_data = svg_file.read()
        except:
            logger.error("Error reading the SVG ")
   	    return False 

        # Create the blank image surface
        img = cairo.ImageSurface( cairo.FORMAT_ARGB32, settings.EXPORT_IMAGE_WIDTH, settings.EXPORT_IMAGE_HEIGHT )

        # Get the context
        ctx = cairo.Context( img )

        # Dump SVG data to the image context
        handler = rsvg.Handle( None, str( svg_data ) )
        handler.render_cairo( ctx )

        # Create the final png image
        final_png = img.write_to_png( settings.DATA_FILES_PATH + "/" + file_name + ".png" )

	logger.info("SVG and PNG Created")
