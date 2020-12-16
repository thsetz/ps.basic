# psf: ta=4, -*-Python-*-, vi: set et ts=4: coding: utf-8
__doc__ = """ps_shell_log writes strings to the ps logging of the DEV_STAGE.
             It should be used from accompanying Programms e.g. shell-scripts to 
             write logging Messages which will be integrated to the other logging 
             messages on the correlated DEV_STAGE.
  
  Usage: ps_shell_log [-v] [ --level=LEVEL ] [ --service_name=name ] TEXT ...

  Arguments:
    TEXT  Message to be printed

  Options:
    -h --help             Show this screen.
    -v                    verbose
    --level=LEVEL         LogLevel (DEBUG,INFO,ERROR,WARNING,FATAL) 
    -service_name=value   the system_id of the message  

"""
import sys
import docopt
import re, os
import urllib, base64
from   ps.basic import Config 
from ps.basic import __version__ as version
SERVICE_NAME = "shell_log"

def main():
    level="info"
    options = docopt.docopt(__doc__, version=1)
    if options["-v"]:                     VERBOSE = True
    if options["--level"] != None:        level=options["--level"]
    if options["--service_name"] != None: service_name=options["--service_name"]

    the_singleton = Config.Basic(SERVICE_NAME, have_config_file=False)
    try:
       exec('Basic.logger.%s("%s",extra={"package_version":"%s")'%(level.lower(),options['TEXT'],str(version)))
    except:
       Config.logger.exception("Exception while calling ps_shell_log")
