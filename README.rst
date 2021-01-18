Introduction
============
.. Setup
   >>> import pprint,os


The ps (Production System) packages implementation started in 2013. Given a non staged production environment - hosted on different operating Systems all around the globe the implementations first goal was to consolidate the widely spread scripts and standalone Programs - started via cron - under one umbrella. 
At that time it was decided to implement that umbrella using python 2.4. The ps.basic package was created.

Back than the ps.basic requirements where:

 - establish the usage of templates for shell scripts and emails 
 - establish a consistent way calling shell scripts and sending emails
 - establish a consistent way for local logging (with automatic logfile rotation/deletion)
 - establish a consistent way to handle configuration files 
 - establish a consistent way to handle staged environments (TESTING/DEVELOPMENT/INTEGRATION/PRODUCTION)

In the next step it was decided to:

 - enhance the logging 

   - additionally send the logging message to a network socket endpoint
   - enhance the logging message with version number, Product_id, ....
   - implement a program/package `ps_bridge <https://psherald.readthedocs.io/en/latest/ps.html>`_  being able to receive those logging messages
      - to store those logging messages in an sqlite database (as delivered with the python standard distribution)
      - or/and route those logging messages to further destinations 
   - implement a web server  `ps_herald <https://psherald.readthedocs.io/en/latest/ps.html>`_ 
     to analyze the logging messages provided by the sqlite database on a node
   - implement a tool in that package `ps_neelix <https://psherald.readthedocs.io/en/latest/ps.html>`_ to react on 
         - logging messages e.g inform interested parties that something happened e.g using  email via stage_specific configuration files (easily added to versioning control)
         - lost heartbeats of monitored services putting their logging messages in the sqlite database on a node
  
 - add a finite state machine environment to the ps.basic package 

   - easing putting structure to the implementation 
   - a graphical representation based on `pygraphviz <https://pypi.org/project/pygraphviz/>`_ was added - generating the image from the implementation. 

Those mechanisms where implemented compatible to python 2.4. Having a package major version numbers 0 e.g. 0.x.x and are used in daily production.

It allows for a staged development/production environment - combined with CI/CT ... allowing to easily monitor the distributed services behaviour and configuration  - as depicted in the following picture.

.. image::  Jenkins_on_DEV_STAGES.png

Crucial points for the logging are:
         - the used network connections are setup using ssh where the setup of the connection is completely owned by the "mother company"  - it is currently not in the scope of the project to further manage this
         - that the *Version number*  of the service (beside module name , line number ...) is automatically integrated into the logging message - serving Requirements for ITIL.
         - it is possible (and used in production) to (easily) extend existing applicacitions to use the (version based) logging mechanism.
          
Starting with the usage of python 3 the package was released to the public using a major version number 1 e.g. 1.x.x.  


Documentation:  https://psbasic.readthedocs.io

Git:  https://bitbucket.org/drsetz/ps.basic/src/master/


