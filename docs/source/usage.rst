=====
Usage
=====

The ``ps.basic`` package implements utilities helping in the development of distributed 
services within the ps environment.

    - easing setup for logging
    - easing setup for staging environments
    - easing setup for config files
    - basics to implement and document services based on finite state machines 
    - locking mechanisms to guard against execution of multiple servive instances
 

Core Mechanism Easing setup for staging environments
====================================================

At the core of the ps.basic package is the ``ps.basic.DEV_STAGES`` dictionary holding default
values for the staging environments.

    >>> import pprint,os
    >>> import ps.basic
    >>> print(pprint.pformat(ps.basic.DEV_STAGES)) # doctest: +NORMALIZE_WHITESPACE
    {'DEVELOPMENT': {'l_admin_mail': ['d_test@somewhere.com'],
                     'logging_bridge_port': 9019,
                     'logging_level': 10,
                     'logging_port': 9020,
                     'suffix': '_d'},
     'INTEGRATION': {'l_admin_mail': ['itest@somewhere.com'],
                     'logging_bridge_port': 9018,
                     'logging_level': 10,
                     'logging_port': 9022,
                     'suffix': '_i'},
     'PRODUCTION': {'l_admin_mail': ['production@somewhere.com'],
                    'logging_bridge_port': 9017,
                    'logging_level': 10,
                    'logging_port': 9024,
                    'suffix': ''},
     'TESTING': {'l_admin_mail': ['test@somewhere.com'],
                 'logging_bridge_port': 9011,
                 'logging_level': 10,
                 'logging_port': 9010,
                 'suffix': '_t'}}
 
``logging_level`` defines the logging level to be used, ``logging_port`` and ``logging_bridge_port``
are used with the help of `ps.herald and ps_bridge <https://psherald.readthedocs.io/en/latest/>`_: to
handle the streams of logging messages.
``suffix`` is  used to define a DEV_STAGE specific suffix for configuration and logging files.
``l_admin_mail`` provides a list of email addreses to be used to send emails to service specific admins.

Initially the attributes in ``ps.basic.Config`` are undefined.

    >>> import ps.basic.Config
    >>> assert (ps.basic.Config.suffix == "not_yet_defined")
    >>> assert (ps.basic.Config.logger == "not_yet_defined")
  
    >>> assert (ps.basic.Config.log_file_name == "not_yet_defined")
    >>> assert (ps.basic.Config.config_file_name == "not_yet_defined")

On instantiation of the ps.basic.Config.Basic class the DEV_STAGE os.environ["DEV_STAGE"] is consulted
to initialize values to be used. If the given value of ``os.environ["DEV_STAGE"]`` is not 
in [\'DEVELOPMENT\', \'INTEGRATION\', ...] instantiation will raise an error.
 
    >>> from ps.basic.Config import Basic 
    >>> os.environ["DEV_STAGE"] = "IMPOSSIBLE_STAGE" # documented below
    >>> service_name = "service_name"
    >>> do_not_care = Basic(service_name) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ps.basic.Config.ForbiddenInitialisationOfSingleton: DEV_STAGE IMPOSSIBLE_STAGE not an Allowed DEVELOPMENT STAGE

Provided an allowed value for DEV_STAGE a singleton instance will be created.

    >>> os.environ["DEV_STAGE"] = "DEVELOPMENT" # documented below
    >>> from ps.basic.Config import Basic 
    >>> Basic(service_name) # doctest:+ELLIPSIS
    <ps.basic.Config.Basic object at ...>

It will have set values at least for logging files
 
    >>> assert (ps.basic.Config.suffix == "_d")
    >>> assert (ps.basic.Config.log_file_name.endswith("LOG/service_name_d.log"))

 
The following lines are here to reset the doctest environment - they are NOT needed in the application.
    >>> def reset_singleton():
    ...     from importlib import reload  
    ...     ps.basic.Config = reload(ps.basic.Config)
    ...     assert (ps.basic.Config.suffix == "not_yet_defined")
    ...     assert (ps.basic.Config.logger == "not_yet_defined")
 
Easing setup for logging
========================

Given the above initialisation: 

    - a directory named ``LOG`` inside the workingdirectory is created
    - a file named ``LOG/service_name_d.log`` holding log entries is created

    >>> assert os.path.isdir("LOG")
    >>> assert os.path.isfile("LOG/service_name_d.log")

The content of the log-file LOG/service_name_d.log looks like:

=================== === ===== === ==================================================================
TIME                ... LEVEL ... MESSAGE
=================== === ===== === ==================================================================
2020-12-11 09:53:12 ... DEBUG ... Logging initialized for pid 18011
2020-12-11 09:53:12 ... DEBUG ... No config file /Users/setzt/ps.basic/docs/service_name_d.cfg given
2020-12-11 09:53:12 ... DEBUG ... Error setting PATTERN_LANGUAGE. Use default EN.
=================== === ===== === ==================================================================

A Module beeing used in the application could simply add additional log messages to the logging ...

    >>> from ps.basic.Config import logger
    >>> logger.info("Another log message") 
    >>> logger.fatal("Another log message") 
    >>> reset_singleton()

This would end up in additional entries in the log file ...

=================== === ===== === ==================================================================
TIME                ... LEVEL ... MESSAGE
=================== === ===== === ==================================================================
2020-12-11 09:53:12 ... DEBUG ... Logging initialized for pid 18011
2020-12-11 09:53:12 ... DEBUG ... No config file /Users/setzt/ps.basic/docs/service_name_d.cfg given
2020-12-11 09:53:12 ... DEBUG ... Error setting PATTERN_LANGUAGE. Use default EN.
2020-12-11 09:53:15 ... INFO  ... Another log message
2020-12-11 09:53:15 ... FATAL ... Another log message
=================== === ===== === ==================================================================

The used ``logger`` is based on the standard python logging module enhanced by file_name, line_number 
and some more easers. 
Furthermore with the help of `ps.herald and ps_bridge <https://psherald.readthedocs.io/en/latest/>`_:

    - an easy to use GUI to analyze the logging messages is available
    - tools to establish a distributed logging environment are available. 


.. note::
   To get access to the ps logging environment, a module only needs to:
 
      - instantiate  the ps.basic.Config.Basic class ( if not already done at  startup of the 
        application)
      - import the logger from ps.basic.Config

Easing setup for config files 
=============================

The ``ps.basic.config`` module  additionaly defines a config_parser (Standard python ConfigParser 
instance) through which access to  the service specific configuration is possible/enforced from 
every module of the application.

First we reset the singleton within this test/documentation document.


    
Given a config_file which has to follow the naming convention, the content could be read from 
anywhere within the application. In the example we first write a config file.
    
    >>> config_filename = os.path.join("/tmp", service_name + "_d.cfg") 
    >>> fp=open(config_filename,"w")  # and the suffix for the development stage.
    >>> written = fp.write("[GLOBAL]" + os.linesep)   
    >>> written = fp.write("pattern_language = DE")   # They follow the ini syle (ms-world) for
    >>> fp.close()                                    # configuration files.
    >>> os.environ["BASIC_CONFIGFILE_DIR"] = "/tmp"   # you can overwrite the path to the config file

Next we instantiate the ``ps.basic.Config.Basic`` singleton.

    >>> os.environ["DEV_STAGE"] = "DEVELOPMENT" # documented below
    >>> Basic(service_name,have_config_file=True) # doctest:+ELLIPSIS
    <ps.basic.Config.Basic object at ...>

The configuration Data is available - and could be read from the application. 

    >>> assert('GLOBAL' in ps.basic.Config.config_parser.sections())
    >>> assert(ps.basic.Config.config_parser['GLOBAL']['pattern_language'] == 'DE')


Cleanup the test environment. ....

    >>> if os.path.isfile(ps.basic.Config.lock_file_name):
    ...     os.remove(ps.basic.Config.lock_file_name) # just cleanup the test environment
    >>> reset_singleton()
    >>> if os.path.isfile(ps.basic.Config.config_file_name):
    ...    os.remove(ps.basic.Config.config_file_name)  # just cleanup the test environment

Easing setup for service locking 
================================

To guard against multiple service instances running in parallel, the ``guarded_by_lockfile``
 Flag isused.

If the Basic singleton is instantiated with this flag  

    >>> Basic(service_name, guarded_by_lockfile = True) # doctest:+ELLIPSIS
    <ps.basic.Config.Basic object at ...>

it stores it's PID in ``ps.basic.Config.lock_file_name``

    >>> pid = open(ps.basic.Config.lock_file_name,"r").read()
    >>> assert(int(pid) == os.getpid()) 
    >>> reset_singleton()

If the start of the service finds a running instance, the instantiation will raise an error.

    >>> do_not_care = Basic(service_name, guarded_by_lockfile = True) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ps.basic.Config.LockedInitialisationOfSingleton: locked by still alive process with pid 567567 for 00:00:00 dsadsad

If there is no running instance, the lock file will be deleted. 

This makes sure, that always only one instance of the service is running on the local machine.
 

Easing setup for documentation and implementation 
=================================================
 
