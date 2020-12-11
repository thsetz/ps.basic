import pkg_resources
# get the version number defined in setup.py
__version__ = pkg_resources.get_distribution("ps.basic").version

import logging


DEV_STAGES = {'TESTING': {'suffix': '_t', 'logging_port': 9010,
                          'logging_bridge_port': 9011,
                          'logging_level': logging.DEBUG,
                          'l_admin_mail': ['test@somewhere.com'], },
              'DEVELOPMENT': {'suffix': '_d', 'logging_port': 9020,
                              'logging_bridge_port': 9019,
                              'logging_level': logging.DEBUG,
                              'l_admin_mail': ['d_test@somewhere.com'], },
              'INTEGRATION': {'suffix': '_i', 'logging_port': 9022,
                              'logging_bridge_port': 9018,
                              'logging_level': logging.DEBUG,
                              'l_admin_mail': ['itest@somewhere.com'], },
              'PRODUCTION': {'suffix': '', 'logging_port': 9024,
                             'logging_bridge_port': 9017,
                             'logging_level': logging.DEBUG,
                             'l_admin_mail': ['production@somewhere.com'], },
              }   




