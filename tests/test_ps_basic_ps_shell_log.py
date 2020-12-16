import pytest
import os
import pprint
from ps.basic import Config
from ps.basic import ps_shell_log

from t_utils import  reset_Singleton, get_data_of_file, common_Config_class_attributes_after_initialisation
from ps.basic.ps_shell_log import SERVICE_NAME
def test_ps_1(dev_allowed_stages):
   reset_Singleton()
   ps_shell_log.main()
   common_Config_class_attributes_after_initialisation(dev_allowed_stages, test_service_name = SERVICE_NAME)
