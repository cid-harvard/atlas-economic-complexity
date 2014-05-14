#!/usr/bin/env python
import os, sys
#Importing optparse
import optparse


if __name__ == "__main__":
     	       
          parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
          parser.add_option("-F", "--data-file", dest="filename",
                      default="None", type="string",
                      help="specify filename to run on")
         
          (options, args) = parser.parse_args()
          filename = options.filename

          if filename != "None":
           sys.argv[2] = filename

          os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlas.settings")

          from django.core.management import execute_from_command_line

          execute_from_command_line(sys.argv)
