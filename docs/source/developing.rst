==========
Developing
==========

Maintaining and setting the version number
==========================================

----------------------------------------------
Where is the version number set and accessed ?
----------------------------------------------

The version number of the package is set once within setup.py. As an example::

 version = '2.0.dev0'
 setup(name='ps.basic',
      version=version,
      description="Basic class used in PS environment",
      long_description=LONG_DESCRIPTION,
      ...


Inside the packages __init__.py file e.g. src/ps/basic/__init__.py it is imported::

  import pkg_resources
  # get the version number defined in setup.py
  __version__ = pkg_resources.get_distribution("ps.basic").version

and provided to the application.


--------------------------------
How ist the version number set ?
--------------------------------

The version number is set using the tool `bump2version <https://pypi.org/project/bump2version/>`_

Using the configuration in setup.cfg::

  [bumpversion]
  current_version = 1.2.5
  commit = True
  tag = True
  
  [bumpversion:file:setup.py]
  search = {current_version}
  replace = {new_version}

The version number in setup.py can be incremented with the usage of ``make release`` .::

  make release
  export DEV_STAGE=TESTING && source ./venv/bin/activate && bumpversion --verbose patch
  Reading config file setup.cfg:
  [bumpversion]
  current_version = 1.2.4
  commit = True
  tag = True
  
  [bumpversion:file:setup.py]
  search = {current_version}
  replace = {new_version}
  
  
  Attempting to increment part 'patch'
  Values are now: major=1, minor=2, patch=5
  New version will be '1.2.5'
  Asserting files setup.py contain the version string...
  current_version=1.2.4
  commit=True
  tag=True
  new_version=1.2.5
  Writing to config file setup.cfg:
  [bumpversion]
  current_version = 1.2.5
  commit = True
  tag = True
  
  [bumpversion:file:setup.py]
  search = {current_version}
  replace = {new_version}
  
  
  Preparing Git commit
  Adding changes in file 'setup.py' to Git
  Adding changes in file 'setup.cfg' to Git
  Committing to Git with message 'Bump version: 1.2.4 → 1.2.5'
  Tagging 'v1.2.5' with message 'Bump version: 1.2.4 → 1.2.5' in Git and not signing

With ``make release_dry`` we can see, what would be done.



Packaging namespace packages
============================
The packages ps.basic, ps.herald should allow to add additional packages e.g. 
ps.area1.service1,  ps.area1.service2,  ps.area2.service1 within the ps namespace.
Namespace packages allow to split the sub-packages and modules within a single 
package across multiple, separate distribution packages. Given
Given `Documentation in <https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages>`_ 
namespace packages are used.

Linting with black
==================

`Black <https://black.readthedocs.io/en/stable/>`_ is a code formatter.
The line length of a sourcefile can be given as param ...

It can work on individual files: ::

  black   --line-length 79 my_file.py
  reformatted my_file..py


Or on complete trees. ::

  black src/ps

  reformatted basic/State.py
  reformatted basic/__init__.py 
  ...


It is possible to Check-only. ::

  black --check  src/ps
  

Autoformatting with vim
=======================


Adding the following line to your .vimrc: ::

  " Run Black on save.
  autocmd BufWritePre \*.py execute ':Black'

The  formatting is done on every save of a python file.


Adding pre commit hook
======================

TBD: `pre_commit_hook <https://pre-commit.com/>`_


 
Automation with tox
===================

`tox <https://tox.readthedocs.io/en/latest/>`_ is used for automation.



..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:


