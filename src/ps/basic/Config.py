""" The Basic Module delivers the *Basis* for Systems in the Production Systems world."""

import os
import logging
import logging.handlers
import sys
import time
import traceback
from subprocess import Popen, PIPE
import traceback
import tempfile
import signal

from configparser import  ConfigParser, ParsingError

from socket import gethostname
from ps.basic import __version__ ,  DEV_STAGES, hms_string
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
is_testing             = not_yet_defined 
i_have_lock            = False


def sighup_handler(signum, frame):
    global config_parser, logger
    if config_parser != not_yet_defined: 
        logger.debug("SIGHUP Received. Print Configuration.",extra={"package_version":__version__})
        log_config_data(config_parser, logger) 
    else:
        raise ForbiddenInitialisationOfSingleton("SIGHUP called but module not yet initiated")

signal.signal(signal.SIGHUP, sighup_handler)
def log_config_data(config_parser,logger):
    html_string = "<table>"
    for section_name in config_parser.sections():
       html_string += "<tr><td>%s</td></tr>" % (section_name)
       for name, value in config_parser.items(section_name):
            html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), str(value))
            if section_name == "GLOBAL" and name == "LOGGING": logger.setLevel(int(value))
       html_string += "</table>"
       if html_string != "<table></table>" :
             logger.debug(html_string,extra={"package_version":__version__})

class Basic(object):
    _instance              = None 

    def __init__(self, service_name_p,
                          have_herald_url_in_config_file = False, 
                          have_config_file = False, 
                          guarded_by_lockfile = False):
        """ 
        """
        global service_name,  dev_stage, suffix, logging_port, logging_bridge_port, webserver_port, logging_bridge_port
        global logging_level, log_file_name, logger, config_file_name, config_parser, herald_sqlite_filename , primary_herald_url
        global lock_file_name, admin_mail, curr_mail_sender, curr_mail_recipients, curr_mail_subject, curr_mail_text, i_have_lock
        global is_testing        

        if Basic._instance == None:
            dev_stage = os.getenv("DEV_STAGE", None)
            if dev_stage == None or dev_stage not in DEV_STAGES.keys():
                 raise ForbiddenInitialisationOfSingleton("DEV_STAGE %s not an Allowed DEVELOPMENT STAGE"%(dev_stage))
            Basic._instance             = self
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
            is_testing              = os.getenv("IS_TESTING", "NOT TESTING")

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

            if guarded_by_lockfile:
                self.__handle_lockfile__()

            if have_config_file:
                self.__handle_configfile__(have_herald_url_in_config_file)
        else:
           raise ForbiddenInitialisationOfSingleton("Reinitialization of the singleton is not allowed")

   
    def __handle_configfile__(self, have_herald_url_in_config_file):
        global config_parser, config_file_name, config_file_directory, primary_herald_url
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
                if have_herald_url_in_config_file:
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
        except SystemExit: #pragma: no cover
              logger.exception("Error reading config File: version %s"%(__version__))
              e = sys.exc_info()[1]
              self.__exit__( 1,2,3)
              raise e

        if have_herald_url_in_config_file:
             try:
                  primary_herald_url = config_parser.get("GLOBAL", 'herald_url')
             except:
                  logger.fatal( "Value of herald_url in GLOBAL section of %s not given - but needed. EXIT NOW"%(config_file_name),extra={"package_version":__version__})
                  sys.stderr.write("Value of herald_url GLOBAL section of %s not given. EXIT NOW" % config_file_name)
                  raise ForbiddenInitialisationOfSingleton("Value of herald_url GLOBAL section of %s not given. EXIT NOW")
                  #self.__exit__( 1,2,3)
                  #sys.exit(1)

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

        # Call the modules sighup_handler which will write the configuration data to the log
        log_config_data(config_parser,logger) 
 

    def __handle_lockfile__(self):
       """ """
       global i_have_lock, logger, is_testing, lock_file_name

       def init_lockfile(fq_path_to_lockfile_p):
           fp = open(lock_file_name, "w")
           fp.write("%s" % os.getpid())
           fp.close()

       if not os.path.isfile(lock_file_name):
           try:
               init_lockfile(lock_file_name)
               i_have_lock     = True
           except: #pragma: no cover
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
          #sys.stdout.write("%s locked by process with pid %s for %s" % (lock_file_name,pid,age))


          try:
               os.kill(int(pid), 0)
               logger.info("process with pid %s is still alive Exit now " % (pid), extra={"package_version":__version__})
               raise LockedInitialisationOfSingleton("%s locked by process with pid %s for %s" % (lock_file_name,pid,age))
          except OSError:
               logger.error("process with pid %s is not alive: Will Remove the lock file" % (pid), extra={"package_version":__version__})
               sys.stderr.write("process with pid %s is not alive: Will Remove the lock file" % (pid))
               os.remove(lock_file_name)
               raise LockedInitialisationOfSingleton("removed orhaned lock_file %s for process with pid %s for %s" % (lock_file_name,pid,age))
               # exit here -next time the lock-file has been gone ...
               self.__exit__( 1,2,3)

   
    def verbose():
        """ Print log messages to stdout too """
        global logger
        if logger == not_yet_defined: 
            raise ForbiddenInitialisationOfSingleton("verbose called but module not yet initiated")
        ch=logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formater=logging.Formatter('%(asctime)s - %(service_name)-12s %(lineno)d - %(message)s')
        logger.addHandler(ch) 
    
    def __exit__(self, exc_type, exc_value, traceback):
          if exc_type ==1 and exc_value == 2 and traceback == 3:
            try:
              if os.path.isfile(lock_file_name):
                  logger.debug("remove lock_file %s"%(lock_file_name), extra={"package_version":__version__})
                  os.unlink(lock_file_name)
            except:               #pragma: no cover
              logger.exception("remove lock_file: version %s"%(__version__))
              sys.stdout.write("Unable to remove lock file")
              sys.stderr.write("Unable to remove lock file")
              sys.stderr.write(traceback.print_exc())
          else: #pragma: no cover
              logger.error("remove log_file Leave Singleton with nonstandard __exit__", extra={"package_version":__version__})
              sys.stderr.write("Leave Singleton with nonstandard __exit__")
  
  
    def __del__(self):
        """ default destructor currently calling __exit__ only if we have a lockfile"""
        if i_have_lock: self.__exit__(1, 2, 3)




  
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


class LockedInitialisationOfSingleton(Exception):
    def __init__(self,  message):
        self.message = message

class ForbiddenInitialisationOfSingleton(Exception):
    def __init__(self,  message):
        self.message = message

class ForbiddenToResetModule(Exception):
    def __init__(self,  message):
        self.message = message

MAX_SIZE_FOR_A_ROTATING_LOGFILE     = 2000000
MAX_NUMBER_OF_OLD_ROTATING_LOGFILES = 10
PATTERN_LANGUAGE                    = "EN"





def template_writer(patterns_p, pattern_offset_p, pattern_p, d_vars_p):
    """
      A helper function for writing strings  from patterns 
    """

    try:
        template = patterns_p[pattern_offset_p][pattern_p]
        return template % (d_vars_p)
    except:
        logger.exception("unable to generate string in %s from template %s" % (pattern_offset_p, pattern_p))
        raise KeyError(pattern_offset_p)



def ps_shell(cmd_p: str, env_p: dict = None):
    global logger, service_name 
    success = "SUCCESS"
    try:
        start_time = time.time()
        child = Popen(cmd_p, shell=True, stdout=PIPE, stderr=PIPE, env=env_p, universal_newlines=True)
        (stdout, stderr) = child.communicate()
        exitcode = child.poll()
        end_time = time.time()

    except Exception:  #pragma: no cover
        sys.stdout.write("%s: Exception while calling %s" % (service_name, cmd_p))
        logger.exception("Exception while calling %s" % (cmd_p))
        stdout = "ERROR"
        stderr = traceback.format_exc()
        exitcode = 1 
        end_time = time.time()

    time_needed = hms_string(end_time - start_time)
    time_needed = "unknown"
    if exitcode != 0:
        success = "ERROR"
    logger.debug("%s %s %s " % (success, time_needed, cmd_p),extra={"package_version":__version__})
    if exitcode != 0:
        logger.error("%d %s" % (int(exitcode), stderr),extra={"package_version":__version__})

    return (
        str(stdout).strip().split("\n"),
        str(stderr).strip().split("\n"),
        exitcode,
        time_needed
    )   

def exec_interpreter_from_string(source_code: str):
    """ 
    """
    tmp = tempfile.NamedTemporaryFile(mode="w+t")
    try:
        tmp.write(source_code)
        tmp.flush() 
        cmd="%s %s"%(sys.executable,tmp.name)
        out,err,exit,time_needed = ps_shell(cmd)
    finally:
       tmp.close    

    return out,err,exit,time_needed


