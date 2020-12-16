import os, sys, pytest, time, logging,pprint, signal
from socket import gethostname
from configparser import ParsingError
from importlib import reload  

from t_utils import TEST_SERVICE_NAME, reset_Singleton, get_data_of_file, common_Config_class_attributes_after_initialisation


import ps.basic
from ps.basic import DEV_STAGES, Config, Patterns
os.environ["IS_TESTING"] = "YES"


# The fixtures:
#   - dev_allowed_stages
#   - dev_wrong_stages
# are defined in conftest.py



def test_that_an_reinitialization_of_the_singleton_raises_an_Error(dev_allowed_stages):
        with pytest.raises(Config.ForbiddenInitialisationOfSingleton) :
           b = Config.Basic(TEST_SERVICE_NAME)   # Should be  OK
           k = Config.Basic(TEST_SERVICE_NAME)   # Will Raise Error


def test_service_names_with_wrong_stage_name_raise_error(dev_wrong_stages):
    reset_Singleton()
    with pytest.raises(Config.ForbiddenInitialisationOfSingleton) :
        assert Config.service_name == "not_yet_defined"
        Config.Basic(TEST_SERVICE_NAME)

def test_properties_are_set(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert Config.primary_herald_url        == ""

#
# verbose mode 
#
def test_verbose_mode_with_uninitialized_singleton_raises_error(dev_allowed_stages):
    reset_Singleton()
    with pytest.raises(Config.ForbiddenInitialisationOfSingleton) :
        assert Config.service_name == "not_yet_defined"
        Config.Basic.verbose()

def test_verbose_mode_with_initialized_singleton_writes_logging_messages_to_stdout_too(dev_allowed_stages, capsys):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    Config.Basic.verbose()
    msg = "This is a message"
    Config.logger.info(msg,extra={"package_version":"__version__"})
    captured = capsys.readouterr()
    assert captured.out == "" 
    assert captured.err == msg +"\n"
    assert msg in get_data_of_file(Config.log_file_name)

#
# LOCK FILE THINGS
#
def test_properties_are_set_using_guarded_by_lockfile_the_lock_file_does_NOT_already_exist(dev_allowed_stages):
    # Make sure the lock file is deleted
    lock_filename = os.path.join(os.getcwd(),'%s_lock%s'%(TEST_SERVICE_NAME, DEV_STAGES[dev_allowed_stages]["suffix"]))
    if os.path.isfile(lock_filename) :os.remove(lock_filename)
    reset_Singleton()

    Config.Basic(TEST_SERVICE_NAME, guarded_by_lockfile = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert os.path.isfile(Config.lock_file_name)
    assert str(os.getpid()) in get_data_of_file(Config.lock_file_name)
    assert "started new lock guarded instance on"  in  get_data_of_file(Config.log_file_name)
    assert(Config.i_have_lock) 
    # Reset the singleton (but leave the lockfile in the filesystem)
    # The instantiation should raise a Config.LockedInitialisationOfSingleton Exception
    # because the pid ist still the same 
    reset_Singleton()
    with pytest.raises(Config.LockedInitialisationOfSingleton) :
        Config.Basic(TEST_SERVICE_NAME, guarded_by_lockfile = True)
        print(get_data_of_file(Config.log_file_name)) 
    assert(os.getpid() == int(get_data_of_file(Config.lock_file_name)))

    # Write a wrong pid into the lock file ==> now the instantiation will detect, that the service
    # is NOT runningi:
    #    - remove the lock file
    #    - and  raise a Config.LockedInitialisationOfSingleton exception
    assert os.path.isfile(Config.lock_file_name)
    with open(Config.lock_file_name,"w") as fp:
         fp.write("999999")
         fp.flush()
    reset_Singleton(remove_log_file=False)
    with pytest.raises(Config.LockedInitialisationOfSingleton) :
        Config.Basic(TEST_SERVICE_NAME, guarded_by_lockfile = True)
    assert "Will Remove the lock file" in get_data_of_file(Config.log_file_name)
    assert not os.path.isfile(Config.lock_file_name)
    assert(Config.i_have_lock == False) 
     
    # Now the singleton could be used as at the beginning of the test 
    reset_Singleton(remove_log_file=False)
    Config.Basic(TEST_SERVICE_NAME, guarded_by_lockfile = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert os.path.isfile(Config.lock_file_name)
    assert str(os.getpid()) in get_data_of_file(Config.lock_file_name)

#
# CONFIG FILE THINGS
#
def test_not_existing_config_file_directory_raises_ForbiddenInitialisationOfSingleton(dev_allowed_stages,capsys):
    reset_Singleton()
    config_file_directory = "/foobar"
    os.environ["BASIC_CONFIGFILE_DIR"] = config_file_directory
    with pytest.raises(Config.ForbiddenInitialisationOfSingleton):
        Config.Basic(TEST_SERVICE_NAME, have_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert Config.config_file_name == "not_yet_defined"
    assert "The BASIC_CONFIGFILE_DIR %s does not exist"%(config_file_directory) in get_data_of_file(Config.log_file_name)

def test_config_file_in_local_directory(dev_allowed_stages,capsys):
    reset_Singleton()
    os.environ["BASIC_CONFIGFILE_DIR"] = ""
    del os.environ["BASIC_CONFIGFILE_DIR"]
 
    config_file_name = os.path.join(TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    with open( config_file_name, "w") as fp:
        fp.write("[test_section]\n")
        fp.write("    test_name = test_value  \n")

    Config.Basic(TEST_SERVICE_NAME, have_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert(Config.primary_herald_url        == "")

    assert(Config.config_file_name == os.path.join(os.getcwd(),config_file_name))
    assert("test_section" in Config.config_parser.sections())
    assert("test_value" == Config.config_parser["test_section"]["test_name"])



def test_config_file_in_directory(dev_allowed_stages,capsys):
    reset_Singleton()
    config_file_directory = "/tmp"
    config_file_name = os.path.join(config_file_directory, TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    os.environ["BASIC_CONFIGFILE_DIR"] = config_file_directory
    with open( config_file_name, "w") as fp:
        fp.write("[test_section]\n")
        fp.write("    test_name = test_value  \n")

    Config.Basic(TEST_SERVICE_NAME, have_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert(Config.primary_herald_url        == "")

    assert(Config.config_file_name == config_file_name)
    assert("test_section" in Config.config_parser.sections())
    assert("test_value" == Config.config_parser["test_section"]["test_name"])



def test_wrong_formated_config_files_in_directory_raise_error(dev_allowed_stages,capsys):
    reset_Singleton()
    config_file_directory = "/tmp"
    config_file_name = os.path.join(config_file_directory, TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    os.environ["BASIC_CONFIGFILE_DIR"] = config_file_directory
    with open( config_file_name, "w") as fp:
        fp.write("[Wrong Section Entry\n")
        fp.write("    test_name = test_value  \n")

    with pytest.raises(ParsingError):
         Config.Basic(TEST_SERVICE_NAME, have_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert(Config.primary_herald_url        == "")

    assert(Config.config_file_name == config_file_name)
    assert("MissingSectionHeaderError" in get_data_of_file(Config.log_file_name))

def test_forced_config_file_reads_herald_url_and_pattern_language(dev_allowed_stages,capsys):
    reset_Singleton()
    config_file_directory = "/tmp"
    config_file_name = os.path.join(config_file_directory, TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    os.environ["BASIC_CONFIGFILE_DIR"] = config_file_directory
    with open( config_file_name, "w") as fp:
        fp.write("[GLOBAL]\n")
        fp.write("    herald_url = localhost\n")
        fp.write("    pattern_language = DE\n")
        fp.write("    LOGGING =  INFO\n")

    Config.Basic(TEST_SERVICE_NAME, have_config_file = True, have_herald_url_in_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)
    assert(Config.primary_herald_url        == "localhost")

    assert(Config.config_file_name == config_file_name)
    assert("GLOBAL" in Config.config_parser.sections())
    assert("localhost" == Config.config_parser["GLOBAL"]["herald_url"])
    assert("DE" == Config.config_parser["GLOBAL"]["pattern_language"])
    assert "GLOBAL" in get_data_of_file(Config.log_file_name)
    assert "herald_url" in get_data_of_file(Config.log_file_name)
    assert "localhost" in get_data_of_file(Config.log_file_name)

def test_forced_config_file_reads_herald_url_and_pattern_language_but_herald_url_is_not_defined(dev_allowed_stages,capsys):
    reset_Singleton()
    config_file_directory = "/tmp"
    config_file_name = os.path.join(config_file_directory, TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    os.environ["BASIC_CONFIGFILE_DIR"] = config_file_directory
    with open( config_file_name, "w") as fp:
        fp.write("[GLOBAL]\n")
        fp.write("    pattern_language = DE\n")
        fp.write("    LOGGING =  INFO\n")

    with pytest.raises(Config.ForbiddenInitialisationOfSingleton):
        Config.Basic(TEST_SERVICE_NAME, have_config_file = True, have_herald_url_in_config_file = True)
    common_Config_class_attributes_after_initialisation(dev_allowed_stages)

    assert "Value of herald_url" in get_data_of_file(Config.log_file_name)
    assert "not given" in get_data_of_file(Config.log_file_name)




def test_sighup_handler_singleton_uninitialized(dev_allowed_stages,capsys):
    reset_Singleton()
    with pytest.raises(Config.ForbiddenInitialisationOfSingleton):
        os.kill(os.getpid(),signal.SIGHUP)

def test_sighup_handler_singleton_initialized(dev_allowed_stages,capsys):
    reset_Singleton()
    os.environ["BASIC_CONFIGFILE_DIR"] = ""
    del os.environ["BASIC_CONFIGFILE_DIR"]
 
    config_file_name = os.path.join(TEST_SERVICE_NAME + DEV_STAGES[dev_allowed_stages]["suffix"] + ".cfg")
    with open( config_file_name, "w") as fp:
        fp.write("[test_section]\n")
        fp.write("    test_name = test_value  \n")

    Config.Basic(TEST_SERVICE_NAME, have_config_file = True)
    os.kill(os.getpid(),signal.SIGHUP)
    assert "SIGHUP Received. Print Configuration." in get_data_of_file(Config.log_file_name)

def test_ps_shell_ls(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    out,err,exit_code,time_needed= Config.ps_shell("ls -a")
    assert "LOG" in out 
    assert err == ['']
    assert exit_code == 0 
    assert "ls -a" in get_data_of_file(Config.log_file_name)

def test_ps_shell_impossible_cmd(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    out,err,exit_code,time_needed= Config.ps_shell("impossible_command")
    assert out == ['']
    assert "impossible_command" in "".join(err)
    assert exit_code != 0 
    assert "impossible_command" in get_data_of_file(Config.log_file_name)

def test_exec_interpreter_from_string(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    out,err,exit_code,time_needed = Config.exec_interpreter_from_string("print('Hello World')") 
    assert "Hello World" in out 
    assert err == ['']
    assert exit_code == 0 
    assert sys.executable  in get_data_of_file(Config.log_file_name)

def test_template_writer(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
    text = Config.template_writer(Patterns.SUBJECT_PATTERNS,"DE","PROD_LOCKED",{"snapshot_name":"tralala"})
    assert text == "tralala LOCKED "

def test_template_writer_(dev_allowed_stages):
    reset_Singleton()
    Config.Basic(TEST_SERVICE_NAME)
   
    with pytest.raises(KeyError):
        text = Config.template_writer(Patterns.SUBJECT_PATTERNS,"IMPOSSIBLE_KEY","PROD_LOCKED",{"snapshot_name":"tralala"})
    assert "unable to generate string" in get_data_of_file(Config.log_file_name)









