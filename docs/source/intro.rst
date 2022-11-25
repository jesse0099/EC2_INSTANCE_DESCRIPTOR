Introduction
============

**EC2 instances descriptor** is a script that wraps `boto`_ (Amazon Official SDK for python) 
to make it easier to use on traceability processes as well as to enforce "resources state changed" 
policies (creations, terminations, modifications). Also, a set of classes and methods is provided 
to interact with **Airtable API** \(REST\) without using an SDK.

It's written and has been tested on **Python 3.9.13**. To avoid environment incompatibilities a `venv`_ is
provided using **Poetry**.

Motivation
**********

Limitations
***********

At this iteration, the script is focused only on EC2 instances, as his name says, but it's intended 
to be expanded to other resources, not necessarily using Python. 

Parallel computing strategies are not implemented in the current version.

.. note::
    Even if the script capabilities are expanded using other technologies, this ReadTheDocs-page 
    will be a centralized documentation site regarding tools for documentation automation and 
    policies enforcement automation.

Working on
**********
* **EC2_INSTANCE_DESCRIPTOR documentation**

Future iterations
*****************

    .. todolist::

.. _boto: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
.. _venv: https://docs.python.org/3/library/venv.html