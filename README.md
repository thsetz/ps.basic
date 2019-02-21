# Introduction

The ps.basic package holds code for the basic building blocks within the "ps".
cc

These are:

    - a singleton (class **Basic**), which is used to setup a "ps-component" e.g. a service
      in a consistent manner

      - using this class the component adapts easily to the surrounding ps-deployment monitor
      - using this class the component adapts easily to the surrounding mechanisms to handle config files
      - using this class the component adapts easily to the surrounding mechanisms for different production_environments/stages

    - a python function  to send mails (having an exception handler trying to send the mail via shell)

    - an easier interface for calling a shell

    - basics to implement and document finite state machines

    - some other small helper  functions


The usage of this package is closely related to the usage of the ps.herald package with adds a (via ssh tunnels distributed usable)
monitoring environment based on the here implemented Basics.

