""" The Basic Module delivers the *Basis* for Systems in the Production Systems world."""

import os
import logging
import logging.handlers
import sys
import time
import traceback
from configparser import  ConfigParser, ParsingError

from socket import gethostname
from ps.basic import __version__ ,  DEV_STAGES
from ps.basic.Patterns import LOGGING_PATTERNS, PATTERN_LANGUAGES

not_yet_defined                     = "not_yet_defined"

    
service_name           = not_yet_defined  #: e.g test_service_name
suffix                 = not_yet_defined  #: e.g are we on d,i or p system
logging_port           = not_yet_defined  #: which port is used to transmit log_messages
logging_bridge_port    = not_yet_defined  #: which port is used to transmit -bridged- log_messages
webserver_port         = not_yet_defined  #: which port is used to access heralds webserver
logging_level          = not_yet_defined  #: current log level
log_file_name          = not_yet_defined  #: name of the local LOG File
logger                 = not_yet_defined  #: provide the logger to other modules
config_file_name       = not_yet_defined  #: the projects config file name
config_parser          = not_yet_defined  #: provide the config File handler to the outside
dev_stage              = not_yet_defined  #: provide the dev_stage to the outside
herald_sqlite_filename = not_yet_defined  #: provide the dev_stage to the outside
primary_herald_url     = not_yet_defined  #: provide an url where a herald could be reached
lock_file_name         = not_yet_defined  #: provide the lock file name
admin_mail             = not_yet_defined 
curr_mail_sender       = not_yet_defined 
curr_mail_recipients   = not_yet_defined
curr_mail_subject      = not_yet_defined
curr_mail_text         = not_yet_defined 
i_have_lock            = False


class Basic(object):
    _instance              = None 

    @staticmethod
    def instance(*args,**kwargs):
        if Basic._instance == None:
            Basic._instance = Basic(*args,**kwargs)
        else:
            pass
        return Basic._instance

   
    def __init__(self, service_name_p,
                          force_usage_of_config_file = False, 
                          have_config_file = True, 
                          guarded_by_lockfile = False):
        """ 
        """
        global service_name,  dev_stage, suffix, logging_port, logging_bridge_port, webserver_port, logging_bridge_port
        global logging_level, log_file_name, logger, config_file_name, config_parser, herald_sqlite_filename , primary_herald_url
        global lock_file_name, admin_mail, curr_mail_sender, curr_mail_recipients, curr_mail_subject, curr_mail_text, i_have_lock
                
        if Basic._instance == None:
            Basic._instance = self
            dev_stage = os.getenv("DEV_STAGE", None)
            if dev_stage == None or dev_stage not in DEV_STAGES.keys():
                 raise ForbiddenInitialisationOfSingleton("DEV_STAGE %s not an Allowed DEVELOPMENT STAGE"%(dev_stage))
            service_name                = service_name_p 
            os.environ["SYSTEM_ID"]     = service_name_p
            os.environ["SUB_SYSTEM_ID"] = gethostname()
            suffix                      = DEV_STAGES[dev_stage]['suffix']
            log_file_name           = os.path.join("LOG", service_name + suffix + ".log")
            logging_port            = DEV_STAGES[dev_stage]['logging_port']
            webserver_port          = DEV_STAGES[dev_stage]['logging_port'] + 1
            logging_bridge_port     = DEV_STAGES[dev_stage]['logging_bridge_port']
            logging_level           = DEV_STAGES[dev_stage]['logging_level']
            admin_mail              = DEV_STAGES[dev_stage]['l_admin_mail']
            herald_sqlite_filename  = os.path.join(os.getcwd(), 'herald.sqlite%s' % suffix)
            primary_herald_url      = ""
            lock_file_name          = os.path.join(os.getcwd(), '%s_lock%s' % (service_name_p, suffix))

            # Create Local LOG Directory
            if not os.path.isdir("LOG"):
                try:
                     os.mkdir("LOG")
                except:
                    sys.stderr.write("Error creating LOG DIR in %s: EXIT Now"%(os.getcwd()))
                    sys.stderr.write("Error creating LOG DIR: EXIT Now")
                    sys.exit(1)

            logger = logging.getLogger(service_name)
            my_filter = ContextFilter()
            logger.addFilter(my_filter)
            socket_handler = logging.handlers.SocketHandler('localhost', logging_port)
            logger.addHandler(socket_handler)
            logfile_handler = logging.handlers.RotatingFileHandler(log_file_name,
                                                                  maxBytes=MAX_SIZE_FOR_A_ROTATING_LOGFILE,
                                                                 backupCount=MAX_NUMBER_OF_OLD_ROTATING_LOGFILES)
            formatter = logging.Formatter(
                '%(asctime)s %(PRODUKT_ID)s %(SYSTEM_ID)s %(SUB_SYSTEM_ID)s %(SUB_SUB_SYSTEM_ID)s \
                 %(USER_SPEC_1)s %(USER_SPEC_2)s %(levelname)s %(name)-12s %(package_version)s %(lineno)d %(message)s')
            logfile_handler.setFormatter(formatter)
            logger.addHandler(logfile_handler)

            logger.setLevel(logging_level)
            logger.debug("Logging initialized for pid %s" % (os.getpid()),extra={"package_version":__version__})
            is_testing = os.getenv("IS_TESTING", "NOT TESTING")
            # LOCK FILE Handling
            def init_lockfile(fq_path_to_lockfile_p):
                 fp = open(lock_file_name, "w")
                 fp.write("%s" % os.getpid())
                 fp.close()

            if guarded_by_lockfile:
                if not os.path.isfile(lock_file_name):
                    try:
                        init_lockfile(lock_file_name)
                        i_have_lock     = True
                    except:
                        logger.exception("Error opening/writing lock File: version %s"%(__version__))
                        sys.stderr.write("Error open/write lockFile %s: EXIT Now" % (lock_file_name))
                        sys.stderr.write(traceback.format_exc())
                        sys.exit(1)
                    logger.info("system %s started new lock guarded instance on %s"
                                 % (service_name, lock_file_name),extra={"package_version":__version__})
                else:
                    with open(lock_file_name, "r") as fp:
                        pid = fp.read().strip()
                    st  = os.stat(lock_file_name)
                    age = hms_string(time.time()-st.st_mtime)
                    logger.info("%s locked by process with pid %s for: %s: version %s" %
                                               (lock_file_name,pid,age,__version__))
                        
                    logger.handlers[0].flush()
                    logger.handlers[1].flush()
                    sys.stdout.write("%s locked by process with pid %s for %s" % (lock_file_name,pid,age))


                    try:
                        os.kill(int(pid), 0)
                        logger.info("process with pid %s is still alive" % (pid), extra={"package_version":__version__})
                        if is_testing == "YES":
                            logger.info("not exiting while testing " , extra={"package_version":__version__})
                        else:
                            logger.info("process with pid %s is still alive Exit now " % (pid), extra={"package_version":__version__})
                            sys.exit(0)
                    except OSError:
                        logger.error("process with pid %s is not alive: Remove it's lock file" % (pid), extra={"package_version":__version__})
                        sys.stderr.write("process with pid %s is not alive: Remove it's lock file" % (pid))
                        os.remove(lock_file_name)
                        immediate_restart_after_detection_of_failed_service = False
                        if immediate_restart_after_detection_of_failed_service:
                            init_lockfile(lock_file_name)
                            logger.error("lock file reset to pid %s" % (os.getpid()), extra={"package_version":__version__})
                            sys.stderr.write("lock file reset to pid %s" % (os.getpid()))
                        else:
                        # exit here -next time the lock-file has been gone ...
                            self.__exit__( 1,2,3)

            if have_config_file:
                config_file_directory = os.getenv("BASIC_CONFIGFILE_DIR", False)
                if config_file_directory:
                    if not os.path.isdir(config_file_directory):
                        logger.fatal("The BASIC_CONFIGFILE_DIR %s does not exist"%(config_file_directory),extra={"package_version":__version__})
                        sys.stderr.write(
                            "ERROR: The BASIC_CONFIGFILE_DIR %s does not exist. EXIT NOW" % (config_file_directory))
                        raise ForbiddenInitialisationOfSingleton("BASIC_CONFIGFILE_DIR %s not possible"%(config_file_directory))
                    else:
                        config_file_name = os.path.join(config_file_directory, service_name + suffix + ".cfg")
                        logger.info("The config_file was forced  to %s " % config_file_name,extra={"package_version":__version__})
                else:
                    config_file_name = os.path.join(os.getcwd(), service_name + suffix + ".cfg")


                config_parser = ConfigParser()
                try:
                    if os.path.isfile(config_file_name):
                        config_parser.read(config_file_name)
                    else:
                        logger.debug("No config file %s given: version %s " % (config_file_name,__version__))
                        if force_usage_of_config_file:
                            sys.stderr.write("No config file %s given but it's usage is mandatory" % (config_file_name))
                            logger.fatal("No config file %s given but it's usage is mandatory: version %s" % (config_file_name,__version__))
                            if is_testing == "YES":
                                logger.info("not exiting while testing " , extra={"package_version":__version__})
                            else:
                                self.__exit__( 1,2,3)
                                sys.exit(1)

                except ParsingError:
                    e = sys.exc_info()[1]
                    logger.exception("Error reading config File: version %s"%(__version__))
                    sys.stderr.write("Error reading config File: EXIT Now")
                    sys.stderr.write(traceback.format_exc())
                    self.__exit__( 1,2,3)
                    if is_testing == "YES":
                        raise e
                    else:
                        raise e
                        sys.exit(1)
                except SystemExit:
                    e = sys.exc_info()[1]
                    self.__exit__( 1,2,3)
                    raise e

        #                #raise SystemExit()
            if force_usage_of_config_file:
                    try:
                        primary_herald_url = config_parser.get("GLOBAL", 'herald_url')
                    except:
                        logger.fatal( "Value of herald_url in GLOBAL section of %s not given - but needed. EXIT NOW"%(config_file_name),extra={"package_version":__version__})
                        sys.stderr.write("Value of herald_url GLOBAL section of %s not given. EXIT NOW" % config_file_name)
                        self.__exit__( 1,2,3)
                        sys.exit(1)

            try:
                PATTERN_LANGUAGE = config_parser.get("GLOBAL", 'pattern_language')
                if PATTERN_LANGUAGE not in PATTERN_LANGUAGES:
                    logger.fatal( "Value of pattern_language in GLOBAL section of %s not allowed. EXIT NOW" % config_file_name,extra={"package_version":__version__})
                    sys.stderr.write("Value of pattern_language in GLOBAL section of %s not allowed. EXIT NOW" % config_file_name)
                    self.__exit__( 1,2,3)
                    sys.exit(1)
            except:
                PATTERN_LANGUAGE = "EN"
                logger.debug( template_writer(LOGGING_PATTERNS, PATTERN_LANGUAGE, "LANGUAGE_PATTERN_FAILED", locals()),extra={"package_version":__version__})



                # ToDo: Add Trap handler to reread config while running (e.g. switch logging level)
            html_string = "<table>"
            for section_name in config_parser.sections():
                html_string += "<tr><td>%s</td></tr>" % (section_name)
                for name, value in config_parser.items(section_name):
                    html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), str(value))
                    if name == "LOGGING": logger.setLevel(int(value))
                html_string += "</table>"
                if html_string != "<table></table>" :
                     logger.debug(html_string,extra={"package_version":__version__})


        else:
           raise ForbiddenInitialisationOfSingleton("Reinitialization of the singleton is not allowed")

           

   
    @classmethod
    def verbose(self):
        """ Print log messages to stdout too """
        if logger == not_yet_defined: 
            print("Not Allowed on not inited Instance")
            return
        #return
        ch=logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formater=logging.Formatter('%(asctime)s - %(service_name)-12s %(lineno)d - %(message)s')
        logger.addHandler(ch) 

    
    def __exit__(self, exc_type, exc_value, traceback):
          #sys.stderr.write("Exit Basic singleton %s"%(__version__))
          if exc_type ==1 and exc_value == 2 and traceback == 3:
            try:
              if os.path.isfile(lock_file_name):
                  logger.debug("remove lock_file %s"%(lock_file_name), extra={"package_version":__version__})
                  os.unlink(lock_file_name)
            except:
              logger.exception("remove lock_file: version %s"%(__version__))
              sys.stdout.write("Unable to remove lock file")
              sys.stderr.write("Unable to remove lock file")
              sys.stderr.write(traceback.print_exc())
          else:
              logger.error("remove log_file Leave Singleton with nonstandard __exit__", extra={"package_version":__version__})
              sys.stderr.write("Leave Singleton with nonstandard __exit__")
  
  
    def __del__(self):
        """ default destructor currently calling __exit__ only if we have a lockfile"""
        #if i_have_lock: self.__exit__(1, 2, 3)




  
class ContextFilter(logging.Filter):
    """ Is used as a logging.filter and merges additional values into the logging message """

    def filter(self, record):

        if "package_version" not in record.__dict__: record.package_version        = "undef"
        record.SYSTEM_ID         = os.getenv("SYSTEM_ID", "None")
        record.SUB_SYSTEM_ID     = os.getenv("SUB_SYSTEM_ID", "None")
        record.SUB_SUB_SYSTEM_ID = os.getenv("SUB_SUB_SYSTEM_ID", "None")
        record.PRODUKT_ID        = os.getenv("PRODUKT_ID", "None")
        record.USER_SPEC_1       = os.getenv("USER_SPEC_1", "None")
        record.USER_SPEC_2       = os.getenv("USER_SPEC_2", "None")
        return True

def hms_string(sec_elapsed):
    """Utility to get the hour:minute:seceonds for an 
       elapsed period in seconds"""
    h = int(sec_elapsed / (60 * 60))
    m = int(sec_elapsed % (60 * 60) / 60)
    s = sec_elapsed % 60
    return "%02d:%02d:%02d" % (h, m, s)


class ForbiddenInitialisationOfSingleton(Exception):
    def __init__(self,  message):
        self.message = message

class ForbiddenToResetModule(Exception):
    def __init__(self,  message):
        self.message = message

MAX_SIZE_FOR_A_ROTATING_LOGFILE     = 2000000
MAX_NUMBER_OF_OLD_ROTATING_LOGFILES = 10
PATTERN_LANGUAGE                    = "EN"

###########################get_html_string##########################
def get_html_string(var_p ):
   """ return html table structure for a data structure (currently only dict) ."""

   html_string = "<table>"
   for name, value in var_p.items():
     if type(value) is dict:
         html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), get_html_string(value))
     else:
        html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), str(value))
   html_string += "</table>"
   return html_string
###########################get_html_string##########################



#
# The following writer functions are used together with xxx_pattern.py files
# in a project.
# param1 ==> xxx_patterns: dictionary with patterns for different languages
# e.g. LOGGING_PATTERNS = {
#    "DE": {
#        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
#        "RSYNC_SUCC": "SUCCESS rsync uebermittelte %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
#
#    },
#    "EN": {
#        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
#        "RSYNC_SUCC": "SUCCESS rsync transfered %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
#
#    },
# }
# param2 ==> pattern_language: string e.g. DE or EN
# param3 ==> name of the pattern to use e.g. RSYNC_SUCC 
# param4 ==> dictionary  with name value pairs to be substituted in pattern

# The functions return the corresponding string in the defined language with the variables substituted.

def template_writer(patterns_p, pattern_offset_p, pattern_p, d_vars_p):
    """
      A helper function for writing strings  from patterns 
    """

    try:
        template = patterns_p[pattern_offset_p][pattern_p]
        return template % (d_vars_p)
    except:
        logger.exception("unable to generate string in %s from template %s" % (pattern_offset_p, pattern_p))
        time.sleep(2)  # give logging a little time to write the message
        raise KeyError(pattern_offset_p)
